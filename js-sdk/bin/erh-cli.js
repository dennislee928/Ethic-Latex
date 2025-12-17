#!/usr/bin/env node
const { program } = require('commander');
const { ERHClient } = require('../dist/index'); // Importing from built dist
const fs = require('fs');

program
    .name('erh-cli')
    .description('CLI for Ethical Riemann Hypothesis Framework')
    .version('0.1.0');

program.command('simulate')
    .description('Run a simulation via the API')
    .option('-n, --num-actions <number>', 'Number of actions', 1000)
    .option('-d, --dist <type>', 'Complexity distribution', 'zipf')
    .option('-u, --url <url>', 'API Base URL', 'http://localhost:8000')
    .option('-o, --output <file>', 'Output JSON file')
    .action(async (options) => {
        console.log(`Running simulation: N=${options.numActions}, Dist=${options.dist}, URL=${options.url}`);

        const client = new ERHClient(options.url);
        try {
            // Health check first
            const healthy = await client.healthCheck();
            if (!healthy) {
                console.error("Error: API is not reachable or unhealthy at " + options.url);
                process.exit(1);
            }

            const result = await client.runSimulation(parseInt(options.numActions), options.dist);
            console.log("Simulation complete!");
            console.log(`Mistakes: ${result.mistakes}, Primes: ${result.primes}`);
            console.log(`ERH Satisfied: ${result.erh_satisfied}`);

            if (options.output) {
                fs.writeFileSync(options.output, JSON.stringify(result, null, 2));
                console.log(`Results saved to ${options.output}`);
            }
        } catch (error) {
            console.error("Simulation failed:", error.message);
            process.exit(1);
        }
    });

program.parse();
