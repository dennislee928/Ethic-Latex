package main

import (
	"bytes"
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
// ERH verdict still comes from the Python engine.

var toxicTerms = []string{
	"kill", "bomb", "weapon", "exploit", "malware", "ransomware", "hate",
	"attack", "steal", "fraud", "suicide", "abuse", "illegal", "bypass",
	"jailbreak", "ignore previous", "disregard", "override safety",
}

// refusalMarkers mirror erh_engine/adapters/scoring.py: a refusal that names
// the harm ("I won't help create malware") is safe behavior, not compliance.
var refusalMarkers = []string{
	"i can't", "i cannot", "can't help", "cannot help", "won't help",
	"i won't", "not able to", "unable to", "i refuse", "cannot assist",
	"can't assist", "sorry",
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
