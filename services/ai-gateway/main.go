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
	"fmt"
	"log"
	"net/http"
	"os"
	"strconv"
	"sync"
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
	maxRisk, err := strconv.ParseFloat(getenvDefault("MAX_RISK", "50"), 64)
	if err != nil {
		log.Printf("invalid MAX_RISK %q, using default 50", os.Getenv("MAX_RISK"))
		maxRisk = 50
	}
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

// sessionWindow is how many recent exchanges per client feed the ERH
// evaluation. A window (not a single sample) lets the engine fit the error
// growth exponent over the client's trajectory — the actual ERH signal.
const sessionWindow = 32

type session struct {
	mu      sync.Mutex
	seq     int
	samples []*pb.Sample
}

type server struct {
	cfg      config
	engine   pb.ERHEngineClient
	mu       sync.Mutex
	sessions map[string]*session
}

func (s *server) sessionFor(id string) *session {
	s.mu.Lock()
	defer s.mu.Unlock()
	if s.sessions == nil {
		s.sessions = make(map[string]*session)
	}
	sess, ok := s.sessions[id]
	if !ok {
		sess = &session{}
		s.sessions[id] = sess
	}
	return sess
}

// score appends this exchange to the client's rolling window and asks the ERH
// engine to evaluate the whole window, so the verdict reflects the session's
// error-growth trajectory rather than one isolated sample.
func (s *server) score(clientID, prompt, response string, harmful bool, weight float64) (*pb.EvaluateResponse, error) {
	if weight <= 0 {
		weight = 1
	}
	// A declared harmful intent raises the stakes of a misjudgment: weight the
	// sample up so the engine treats an unsafe answer as a critical prime.
	if harmful {
		weight *= 4
	}
	sess := s.sessionFor(clientID)
	sess.mu.Lock()
	sess.seq++
	sample := &pb.Sample{
		Id:         fmt.Sprintf("%s-%d", clientID, sess.seq),
		Complexity: textComplexity(prompt),
		Value:      1.0,
		Judgment:   lexicalValue(response),
		Weight:     weight,
	}
	sess.samples = append(sess.samples, sample)
	if len(sess.samples) > sessionWindow {
		sess.samples = sess.samples[len(sess.samples)-sessionWindow:]
	}
	window := make([]*pb.Sample, len(sess.samples))
	copy(window, sess.samples)
	sess.mu.Unlock()

	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()
	return s.engine.Evaluate(ctx, &pb.EvaluateRequest{
		Samples:   window,
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

	// 2. Score the client's rolling window with the ERH engine.
	clientID := c.GetHeader("X-Client-Id")
	if clientID == "" {
		clientID = c.ClientIP()
	}
	verdict, err := s.score(clientID, req.Prompt, response, req.HarmfulIntent, req.Weight)
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
