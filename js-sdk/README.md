# ERH JavaScript SDK

A Node.js/TypeScript SDK for the Ethical Riemann Hypothesis (ERH) Framework.

## Installation

```bash
npm install erh-js-sdk
```

## Usage

### Client Library
Use the client in your Node.js or TypeScript application:

```typescript
import { ERHClient } from 'erh-js-sdk';

const client = new ERHClient("http://localhost:8000");

async function run() {
  const health = await client.healthCheck();
  if (health) {
    const result = await client.runSimulation(1000, 'zipf');
    console.log(result);
  }
}
run();
```

### CLI Tool
The SDK typically installs a CLI tool `erh-cli` (if installed globally or via npx):

```bash
# Run a simulation
npx erh-cli simulate --num-actions 500 --dist zipf
```

## Development
1. Install dependencies: `npm install`
2. Build: `npm run build`
