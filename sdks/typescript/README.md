# FineVoice TypeScript SDK

Requires Node 18+ (global `fetch`) or any runtime with `fetch`.

```bash
cd sdks/typescript && npm install && npm run build
```

```ts
import { FineVoice } from "finevoice";

const client = new FineVoice({ apiKey: process.env.FINEVOICE_API_KEY! });

const task = await client.speechSynthesis({ voice: "james", text: "[happy] Hello!" });
const result = await client.waitForTask(task); // polls GET /v1/task/{id}
console.log(result.url);
```

Errors throw `FineVoiceError` (`.status`, `.body`).
