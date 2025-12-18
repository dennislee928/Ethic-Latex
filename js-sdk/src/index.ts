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
