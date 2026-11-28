# FineVoice API Docs

Official documentation, OpenAPI spec, and SDKs for the **FineVoice API**: AI text-to-speech, voice cloning, voice conversion, speech-to-text, music and sound-effect generation, and audio enhancement behind one REST API.

- 📖 Documentation: https://api.finevoice.ai/
- 🌐 API Base URL: `https://api.finevoice.ai`
- 🎧 Try it online: [FineVoice AI Voice Generator](https://finevoice.ai/)

## 🚀 Features

- 🎙️ **Text-to-Speech (TTS)**: natural-sounding speech in many languages and voices, with [emotion tags](https://api.finevoice.ai/api-reference/emotion-tags)
- 🧬 **Voice cloning and design**: train a custom voice from audio, or design one from a text description
- 🎭 **Voice conversion**: convert existing audio into a different voice
- 📝 **Speech-to-Text (STT)**: transcription and subtitle generation
- 🎙️ **Podcast generation**: multi-speaker podcasts from a script or a topic
- 🎵 **Music and sound effects**: generate songs from prompts, and sound effects from text
- 🎚️ **Audio separation**: split vocals and instrumentals
- 🧹 **Audio enhancement**: speech enhancement, loudness normalization, and removal of mouth sounds, long silences, filler words, and stuttering
- 🤖 **MCP server**: let AI agents call FineVoice directly (see [Use with AI Agents](#-use-with-ai-agents-recommended))

## 🔑 Authentication

Every request needs an **API key**, sent as a Bearer token. Create a key on the [FineVoice](https://finevoice.ai/) dashboard and keep it out of source control and client-side code.

```bash
export FINEVOICE_API_KEY=your_api_key_here
```

```http
Authorization: Bearer YOUR_API_KEY
```

See the [Quickstart](https://api.finevoice.ai/quickstart) for how to get a key.

> 💡 Audiobooks and other long-form audio need more test credits. Contact [support@finevoice.ai](mailto:support@finevoice.ai) to request additional test credits for free.

## ⚡ Quick Start

Generate your first speech file with cURL (see the [TTS reference](https://api.finevoice.ai/api-reference/endpoint/tts) for all parameters):

```bash
curl -X POST "https://apis.finevoice.ai/v1/audio/speech-synthesis" \
  -H "Authorization: Bearer $FINEVOICE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello from FineVoice!", "voice": "james"}'
```

Long-running jobs (TTS, music, voice training, and so on) return a `taskId`. Poll it until the task finishes:

```bash
curl "https://apis.finevoice.ai/v1/task/TASK_ID" \
  -H "Authorization: Bearer $FINEVOICE_API_KEY"
```

A task is done when its status is `success` (or `3`), and failed when it is `failed` (or `4` and above). Any other value means keep polling. Music generation typically takes about a minute.

## 🧰 SDKs

| Language | Package | Install                      | Docs                                  |
| :------- | :------ | :--------------------------- | :------------------------------------ |
| Python   | `finevoice` on PyPI  | `pip install finevoice`      | [sdks/python](sdks/python/README.md)  |
| C# / .NET | `FineVoice` on NuGet | `dotnet add package FineVoice` | [sdks/csharp](sdks/csharp/README.md) |

Example (Python):

```python
import os
from finevoice import FineVoice

client = FineVoice(os.environ["FINEVOICE_API_KEY"])
task = client.speech_synthesis({"text": "Hello from FineVoice!", "voice": "james"})
result = client.wait_for_task(task)
print(result)
```

See the SDK READMEs for all methods and request fields.

## 🤖 Use with AI Agents (Recommended)

If you build with AI coding assistants or agents, the quickest way to use FineVoice is the **MCP server**. MCP-compatible clients such as Claude Desktop, Cursor, and VS Code can then call FineVoice tools directly in conversation, with no integration code.

- Endpoint: `https://mcp.finevoice.ai/v1/mcp` (Streamable HTTP)
- Auth: the same `Authorization: Bearer YOUR_API_KEY` header as the REST API

Example for Cursor (`.cursor/mcp.json`) and Claude Desktop (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "finevoice": {
      "url": "https://mcp.finevoice.ai/v1/mcp",
      "headers": { "Authorization": "Bearer YOUR_API_KEY" }
    }
  }
}
```

For VS Code, use `.vscode/mcp.json` with a `servers` object and `"type": "http"`. After restarting the client, try prompts like:

- "Convert this text to speech using the voice james."
- "Transcribe this audio file and give me subtitles."
- "Generate a 30-second lo-fi track for a study video."
- "Remove the filler words and long silences from this recording."

Full setup and the list of tools: [MCP Server](https://api.finevoice.ai/api-reference/mcp).

**Which should I use?**

| Use case | Recommended |
| :------- | :---------- |
| Chatting with an AI assistant or agent that should create audio for you | MCP server |
| Application code in Python or .NET | SDK |
| Any other language, or full control over requests | REST API |

## 📚 API Overview

Base URL: `https://apis.finevoice.ai`. Full reference: https://api.finevoice.ai/

| Category | Endpoint | Description |
| :------- | :------- | :---------- |
| Text-to-Speech | `POST /v1/audio/speech-synthesis` | Convert text into speech |
| Voice Conversion | `POST /v1/audio/voice-conversion` | Convert audio to another voice |
| Speech-to-Text | `POST /v1/audio/stt` | Transcribe audio and generate subtitles |
| Podcast Generation | `POST /v1/audio/podcastgen` | Generate a multi-speaker podcast |
| Sound Effects | `POST /v1/audio/sfx-generation` | Generate sound effects from text |
| Audio Separation | `POST /v1/audio/separation` | Separate vocals and instrumentals |
| Voice Training | `POST /v1/voice/train` | Train a custom voice clone |
| Voice Design | `POST /v1/voice/design` | Design a voice from a description |
| Voices | `GET /v1/voice/pagevoices`, `GET /v1/voice/{name}` | List voices and get voice details |
| Music | `POST /v1/music/musicgen`, `POST /v1/music/musicgenbyprompt` | Generate music |
| Audio Enhancement | `POST /v1/enhancer/*` | Speech enhancement, normalization, silence, mouth-sound, filler-word, and stuttering removal |
| Task Status | `GET /v1/task/{task_id}` | Poll an asynchronous task |

## ⚙️ Configuration

Keep secrets in a `.env` file and make sure it is git-ignored:

```
FINEVOICE_API_KEY=your_api_key_here
```

## 🛡️ Best Practices

- Never expose your API key in client-side code or commit it to a repository
- Rotate a key immediately if it has been shared or leaked
- Poll tasks every few seconds with a timeout, and handle `failed` statuses
- Some validation errors come back as HTTP 200 with an `error` object, so check the body as well as the status code
- Follow FineVoice's usage policies for voice cloning and commercial use

## ✏️ Working on These Docs

The docs are built with [Mintlify](https://mintlify.com). Navigation lives in `docs.json`, endpoint pages in `api-reference/endpoint/*.mdx`, and the OpenAPI spec in `api-reference/openapi.json`, which `build_openapi.py` generates.

```bash
npm i -g mint
mint dev
```

## 📝 Changelog

See [changelog.mdx](changelog.mdx) or https://api.finevoice.ai/changelog.

## 💬 Support

- 📧 Email: [support@finevoice.ai](mailto:support@finevoice.ai)
- 🎁 Need more test credits for audiobooks or other long-form audio? Email us to apply for free credits.
- 🌐 Website: [FineVoice AI Voice Generator](https://finevoice.ai/)

## 📄 License

See [LICENSE](LICENSE).
