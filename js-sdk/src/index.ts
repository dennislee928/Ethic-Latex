/**
 * Ethical Riemann Hypothesis JS SDK
 * 
 * Client for interacting with the ERH simulation and API.
 */

export class ERHClient {
    baseUrl: string;

    constructor(baseUrl: string = "http://localhost:8000") {
        this.baseUrl = baseUrl;
    }

    /**
     * Check API health
     */
    async healthCheck(): Promise<boolean> {
        try {
            const response = await fetch(`${this.baseUrl}/health`);
            return response.ok;
        } catch (error) {
            console.error("Health check failed:", error);
            return false;
        }
    }

    /**
     * Run a simulation via the API
     */
    async runSimulation(numActions: number = 1000, complexityDist: string = "zipf"): Promise<any> {
        try {
            const response = await fetch(`${this.baseUrl}/simulate`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    num_actions: numActions,
                    complexity_dist: complexityDist
                }),
            });

            if (!response.ok) {
                throw new Error(`API error: ${response.statusText}`);
            }

            return await response.json();
        } catch (error) {
            console.error("Simulation failed:", error);
            throw error;
        }
    }
}

/** A domain-agnostic decision sample for the ERH engine. */
export interface ERHSample {
    id: string;
    complexity: number;
    value: number;     // true value V(a) in [-1, 1]
    judgment: number;  // system judgment J(a) in [-1, 1]
    weight?: number;
    context?: Record<string, unknown>;
}

/**
 * Client for the standardized ERH engine (erh_engine REST service).
 *
 * Wraps POST /v1/evaluate so any system can obtain an ERH verdict for a batch
 * of decision samples.
 */
export class ERHEngineClient {
    baseUrl: string;

    constructor(baseUrl: string = "http://localhost:8000") {
        this.baseUrl = baseUrl.replace(/\/$/, "");
    }

    async health(): Promise<boolean> {
        try {
            const response = await fetch(`${this.baseUrl}/v1/health`);
            return response.ok;
        } catch (error) {
            console.error("Health check failed:", error);
            return false;
        }
    }

    /** Evaluate a batch of samples against the ERH bound. */
    async evaluate(
        samples: ERHSample[],
        params: Record<string, unknown> = {},
        judgeName?: string
    ): Promise<any> {
        const response = await fetch(`${this.baseUrl}/v1/evaluate`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ samples, params, judge_name: judgeName }),
        });
        if (!response.ok) {
            throw new Error(`Engine error: ${response.statusText}`);
        }
        return await response.json();
    }
}
