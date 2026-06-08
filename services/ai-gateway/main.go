// Command ai-gateway is a runtime AI firewall: a reverse proxy that sits in
// front of an LLM upstream, scores each exchange with the ERH engine over gRPC,
// and blocks responses whose misjudgment risk exceeds a configurable threshold.
//
// This is the high-concurrency edge of the hybrid architecture (Go/Gin); all
// ERH math lives in the Python erh_engine reached via gRPC, never reimplemented.
//
// Env:
//   GATEWAY_ADDR       listen address              (default :8080)
//   ERH_ENGINE_ADDR    erh_engine gRPC address     (default localhost:50051)
//   LLM_UPSTREAM_URL   upstream chat complet*ions   (default OpenAI)
//   LLM_API_KEY        bearer token for upstream
//   MAX_RISK           block above this risk_score (default 50)
package main

import (
	"context"
	"log"
	"net/http"
	"os"
	"strconv"
	"time"

	"github.com/dennislee928/ethic-latex/ai-gateway/pb"
	"github.com/gin-gonic/gin"
	"google.golang.org/grpc"
	"google.golang.org/grpc/credentials/insecure"
)

type config struct {
	listenAddr  string
	engineAddr  string
	upstreamURL string
	apiKey      string
	maxRisk     float64
}

func loadConfig() config {
	maxRisk, _ := strconv.ParseFloat(getenvDefault("MAX_RISK", "50"), 64)
	return config{
		listenAddr:  getenvDefault("GATEWAY_ADDR", ":8080"),
		engineAddr:  getenvDefault("ERH_ENGINE_ADDR", "localhost:50051"),
		upstreamURL: getenvDefault("LLM_UPSTREAM_URL", "https://api.openai.com/v1/chat/completions"),
		apiKey:      os.Getenv("LLM_API_KEY"),
		maxRisk:     maxRisk,
	}
}

// chatRequest is the minimal client-facing payload.
type chatRequest struct {
	Prompt        string  `json:"prompt"`
	HarmfulIntent bool    `json:"harmful_intent"`
	Weight        float64 `json:"weight"`
}

type server struct {
	cfg    config
	engine pb.ERHEngineClient
}

// score asks the ERH engine to evaluate a single prompt/response exchange.
func (s *server) score(prompt, response string, harmful bool, weight float64) (*pb.EvaluateResponse, error) {
	if weight <= 0 {
		weight = 1
	}
	// V anchored at the safe pole; J is the safety value of the actual response.
	// The Python LLM adapter computes the real safety values; here we forward raw
	// text by delegating scoring through a single-sample evaluate where the edge
	// pre-normalizes nothing and lets the engine decide. We approximate J with a
	// neutral 0 and rely on context for the engine-side adapter in richer setups;
	// for the firewall hot-path we send the lexical signal via complexity/judgment
	// computed below.
	sample := &pb.Sample{
		Id:         "live-0",
		Complexity: textComplexity(prompt),
		Value:      1.0,
		Judgment:   lexicalValue(response),
		Weight:     weight,
	}
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()
	return s.engine.Evaluate(ctx, &pb.EvaluateRequest{
		Samples:   []*pb.Sample{sample},
		Params:    &pb.EvaluateParams{Tau: 0.3, C: 1, Epsilon: 0.1, SlackFactor: 1.5},
		JudgeName: "ai-gateway",
	})
}

func (s *server) handleChat(c *gin.Context) {
	var req chatRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	// 1. Call the LLM upstream.
	response, err := s.callUpstream(req.Prompt)
	if err != nil {
		c.JSON(http.StatusBadGateway, gin.H{"error": "upstream call failed", "detail": err.Error()})
		return
	}

	// 2. Score the exchange with the ERH engine.
	verdict, err := s.score(req.Prompt, response, req.HarmfulIntent, req.Weight)
	if err != nil {
		// Fail closed: if we cannot score, do not leak an unvetted response.
		c.JSON(http.StatusServiceUnavailable, gin.H{"error": "erh engine unavailable", "detail": err.Error()})
		return
	}

	// 3. Enforce. IOB-style structured audit log.
	log.Printf("erh-audit risk=%.2f erh_satisfied=%v primes=%d prompt_len=%d",
		verdict.RiskScore, verdict.ErhSatisfied, verdict.NumPrimes, len(req.Prompt))

	if verdict.RiskScore > s.cfg.maxRisk {
		c.JSON(http.StatusForbidden, gin.H{
			"blocked":    true,
			"reason":     "ERH risk threshold exceeded",
			"risk_score": verdict.RiskScore,
			"max_risk":   s.cfg.maxRisk,
		})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"blocked":    false,
		"risk_score": verdict.RiskScore,
		"response":   response,
	})
}

func main() {
	cfg := loadConfig()

	conn, err := grpc.NewClient(cfg.engineAddr, grpc.WithTransportCredentials(insecure.NewCredentials()))
	if err != nil {
		log.Fatalf("dial erh engine: %v", err)
	}
	defer conn.Close()

	s := &server{cfg: cfg, engine: pb.NewERHEngineClient(conn)}

	r := gin.New()
	r.Use(gin.Recovery())
	r.GET("/healthz", func(c *gin.Context) { c.JSON(http.StatusOK, gin.H{"status": "ok"}) })
	r.POST("/v1/chat", s.handleChat)

	log.Printf("ai-gateway listening on %s -> engine %s (max_risk=%.1f)", cfg.listenAddr, cfg.engineAddr, cfg.maxRisk)
	if err := r.Run(cfg.listenAddr); err != nil {
		log.Fatal(err)
	}
}
