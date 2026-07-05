package main

import (
	"bytes"
	_ "embed"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"regexp"
	"strings"
	"time"
)

// callUpstream sends the prompt to the configured LLM upstream (OpenAI-style
// chat completions) and returns the assistant's text. If no API key is set it
// returns an echo stub so the gateway is runnable without credentials.
func (s *server) callUpstream(prompt string) (string, error) {
	if s.cfg.apiKey == "" {
		return "[stub] no LLM_API_KEY set; echoing prompt: " + prompt, nil
	}

	body, _ := json.Marshal(map[string]any{
		"model":    firstNonEmpty(getenv("LLM_MODEL"), "gpt-4o-mini"),
		"messages": []map[string]string{{"role": "user", "content": prompt}},
	})
	req, err := http.NewRequest(http.MethodPost, s.cfg.upstreamURL, bytes.NewReader(body))
	if err != nil {
		return "", err
	}
	req.Header.Set("Authorization", "Bearer "+s.cfg.apiKey)
	req.Header.Set("Content-Type", "application/json")

	client := &http.Client{Timeout: 60 * time.Second}
	resp, err := client.Do(req)
	if err != nil {
		return "", err
	}
	defer resp.Body.Close()
	raw, _ := io.ReadAll(resp.Body)
	if resp.StatusCode >= 300 {
		return "", fmt.Errorf("upstream %d: %s", resp.StatusCode, string(raw))
	}

	var parsed struct {
		Choices []struct {
			Message struct {
				Content string `json:"content"`
			} `json:"message"`
		} `json:"choices"`
	}
	if err := json.Unmarshal(raw, &parsed); err != nil {
		return "", err
	}
	if len(parsed.Choices) == 0 {
		return "", fmt.Errorf("upstream returned no choices")
	}
	return parsed.Choices[0].Message.Content, nil
}

// --- lightweight scoring signals mirrored from erh_engine/adapters/scoring.py ---
// These let the edge produce a J/complexity for the gRPC call; the authoritative
// ERH verdict still comes from the Python engine. Term lists are embedded from
// the shared ethics lexicon (canonical: shared/ethics_lexicon.json; this copy is
// kept in sync by tests/test_lexicon_parity.py).

//go:embed ethics_lexicon.json
var lexiconJSON []byte

var toxicTerms []string
var refusalMarkers []string

func init() {
	var lex struct {
		ToxicTerms     []string `json:"toxic_terms"`
		RefusalMarkers []string `json:"refusal_markers"`
	}
	if err := json.Unmarshal(lexiconJSON, &lex); err != nil {
		panic(fmt.Sprintf("ai-gateway: embedded ethics_lexicon.json invalid: %v", err))
	}
	toxicTerms = lex.ToxicTerms
	refusalMarkers = lex.RefusalMarkers
}

func lexicalValue(text string) float64 {
	if text == "" {
		return 1.0
	}
	lowered := strings.ToLower(text)
	hits := 0.0
	for _, t := range toxicTerms {
		if strings.Contains(lowered, t) {
			hits++
		}
	}
	if hits > 0 {
		for _, m := range refusalMarkers {
			if strings.Contains(lowered, m) {
				hits *= 0.2
				break
			}
		}
	}
	v := 1.0 - 0.5*hits
	if v < -1.0 {
		return -1.0
	}
	return v
}

var clauseRe = regexp.MustCompile(`[.!?;]|\band\b|\bor\b|\bif\b|\bthen\b`)

func textComplexity(text string) float64 {
	if text == "" {
		return 1.0
	}
	tokens := len(strings.Fields(text))
	clauses := len(clauseRe.FindAllString(strings.ToLower(text), -1))
	raw := 1.0 + float64(tokens)/20.0 + float64(clauses)*2.0
	if raw > 100.0 {
		return 100.0
	}
	return raw
}
