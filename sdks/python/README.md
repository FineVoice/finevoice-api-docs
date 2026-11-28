# FineVoice Python SDK

Official Python client for the [FineVoice API](https://api.finevoice.ai): text to speech, voice conversion, speech to text, sound effects, music generation, voice design/training, and audio enhancement.

- Python 3.8+
- Single dependency: `requests`
- Full API reference: https://api.finevoice.ai

## Installation

```bash
pip install finevoice
```

## Authentication

Create an API key in the FineVoice dashboard and pass it to the client. Keep it out of source control, for example by reading it from an environment variable.

```python
import os
from finevoice import FineVoice

client = FineVoice(os.environ["FINEVOICE_API_KEY"])
```

Optional constructor arguments:

| Argument   | Default                      | Description                       |
| ---------- | ---------------------------- | --------------------------------- |
| `base_url` | `https://apis.finevoice.ai`  | Override the API host.            |
| `timeout`  | `120`                        | Per-request timeout in seconds.   |

## Quick start

Most generation endpoints are asynchronous: the call returns a `taskId`, and you poll until the task finishes. `wait_for_task` does this for you.

```python
task = client.speech_synthesis({
    "voice": "james",
    "text": "[happy] Hello from FineVoice!",
})

result = client.wait_for_task(task)   # polls GET /v1/task/{taskId}
print(result["url"])
```

### Browse voices

```python
page = client.page_voices(language="en-US", page=0, limit=20)
voice = client.get_voice("james")
```

### Music generation

Music tasks take roughly 50 to 60 seconds. Use the default polling, which allows up to 10 minutes.

```python
task = client.music_gen_by_prompt({"prompt": "calm lo-fi beat with soft piano"})
result = client.wait_for_task(task)
print(result["urls"])        # list of audio URLs
```

### Audio enhancement

The enhancer endpoints respond directly with a download link, so no polling is needed.

```python
out = client.speech_enhancement({"url": "https://example.com/noisy.mp3"})
print(out["download_url"], out["filename"])
```

## Async tasks and polling

```python
client.wait_for_task(task_or_id, interval=5.0, timeout=600.0)
```

- Accepts either the submit response (dict) or a task id string.
- A task is finished when its status is `success` (or `3`). `failed` or a numeric status of `4` or higher raises `FineVoiceError`.
- Any other status keeps polling. Transient gateway errors (5xx on proxy paths) are retried.
- Raises `FineVoiceError` if `timeout` seconds pass without completion.
- Use `client.get_task(task_id)` for a single status check.

## Available methods

Request bodies use the API field names exactly as in the [API reference](https://api.finevoice.ai).

| Area      | Methods |
| --------- | ------- |
| Audio     | `speech_synthesis`, `voice_conversion`, `speech_to_text`, `sfx_generation`, `audio_separation`, `enhance_audio`, `reader_gen`, `podcast_gen`, `dubbing_gen` |
| Voices    | `train_voice`, `design_voice`, `get_voice`, `page_voices` |
| Music     | `music_gen_by_prompt`, `music_gen` |
| Enhancer  | `speech_enhancement`, `remove_mouth_sounds`, `remove_long_silences`, `filler_words_remove`, `stuttering_remove`, `audio_normalization`, `process_pipeline` |
| Tasks     | `get_task`, `wait_for_task` |
| Low level | `request(method, path, json=None, params=None)` for any endpoint not yet wrapped |

## Error handling

All failures raise `FineVoiceError` with:

- `.status`: HTTP status code, if any
- `.body`: parsed response body

```python
from finevoice import FineVoice, FineVoiceError

try:
    client.speech_synthesis({"voice": "james", "text": "Hi"})
except FineVoiceError as e:
    print(e.status, e.body)
```

Note that some validation errors are returned by the API as HTTP 200 with an `error` object (`code`, `message`). Submit calls return that body as-is, so check `result.get("error")`; `wait_for_task` raises on them.

## License

MIT
