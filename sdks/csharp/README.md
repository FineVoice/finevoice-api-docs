# FineVoice C# SDK

Official .NET client for the [FineVoice API](https://api.finevoice.ai): text to speech, voice conversion, speech to text, sound effects, music generation, voice design/training, and audio enhancement.

- .NET 6+
- No third-party dependencies (`HttpClient` + `System.Text.Json`)
- Full API reference: https://api.finevoice.ai

## Installation

```bash
dotnet add package FineVoice
```

## Authentication

Create an API key in the FineVoice dashboard and pass it to the client. Read it from an environment variable or secret store rather than hard-coding it.

```csharp
using FineVoice;

using var client = new FineVoiceClient(Environment.GetEnvironmentVariable("FINEVOICE_API_KEY")!);
```

The constructor also accepts a custom base URL (default `https://apis.finevoice.ai`) and timeout.

## Quick start

Most generation endpoints are asynchronous: the call returns a `taskId`, and you poll until the task finishes. `WaitForTaskAsync` does this for you.

```csharp
var task = await client.SpeechSynthesisAsync(new { voice = "james", text = "[happy] Hello from FineVoice!" });

var result = await client.WaitForTaskAsync(FineVoiceClient.GetTaskId(task)!); // polls GET /v1/task/{id}
Console.WriteLine(result["url"]);
```

### Browse voices

```csharp
var page = await client.PageVoicesAsync(new Dictionary<string, object?>
{
    ["language"] = "en-US",
    ["page"] = 0,
    ["limit"] = 20,
});
var voice = await client.GetVoiceAsync("james");
```

### Music generation

Music tasks take roughly 50 to 60 seconds. The default polling allows up to 10 minutes.

```csharp
var task = await client.MusicGenByPromptAsync(new { prompt = "calm lo-fi beat with soft piano" });
var result = await client.WaitForTaskAsync(FineVoiceClient.GetTaskId(task)!);
Console.WriteLine(result["urls"]);
```

### Audio enhancement

The enhancer endpoints respond directly with a download link, so no polling is needed.

```csharp
var output = await client.SpeechEnhancementAsync(new { url = "https://example.com/noisy.mp3" });
Console.WriteLine(output?["download_url"]);
```

## Async tasks and polling

```csharp
Task<JsonNode> WaitForTaskAsync(string taskId, TimeSpan? interval = null, TimeSpan? timeout = null, CancellationToken ct = default)
```

- Defaults: poll every 5 seconds, time out after 600 seconds.
- A task is finished when its status is `success` (or `3`). `failed` or a numeric status of `4` or higher throws `FineVoiceException`.
- Any other status keeps polling. Transient gateway errors (5xx on proxy paths) are retried.
- `GetTaskId(response)` extracts the id from a submit response; `GetTaskAsync(id)` performs a single status check.
- Every method accepts a `CancellationToken`.

## Available methods

Request bodies can be anonymous objects or dictionaries that use the API field names from the [API reference](https://api.finevoice.ai). Responses are `JsonNode`.

| Area      | Methods |
| --------- | ------- |
| Audio     | `SpeechSynthesisAsync`, `VoiceConversionAsync`, `SpeechToTextAsync`, `SfxGenerationAsync`, `AudioSeparationAsync`, `EnhanceAudioAsync`, `ReaderGenAsync`, `PodcastGenAsync`, `DubbingGenAsync` |
| Voices    | `TrainVoiceAsync`, `DesignVoiceAsync`, `GetVoiceAsync`, `PageVoicesAsync` |
| Music     | `MusicGenByPromptAsync`, `MusicGenAsync` |
| Enhancer  | `SpeechEnhancementAsync`, `RemoveMouthSoundsAsync`, `RemoveLongSilencesAsync`, `FillerWordsRemoveAsync`, `StutteringRemoveAsync`, `AudioNormalizationAsync`, `ProcessPipelineAsync` |
| Tasks     | `GetTaskAsync`, `WaitForTaskAsync` |
| Low level | `RequestAsync`, `RequestBytesAsync` for any endpoint not yet wrapped |

## Error handling

Failures throw `FineVoiceException` with `Status` (HTTP status code, if any) and `Body` (parsed response).

```csharp
try
{
    await client.SpeechSynthesisAsync(new { voice = "james", text = "Hi" });
}
catch (FineVoiceException e)
{
    Console.WriteLine($"{e.Status}: {e.Body}");
}
```

Some validation errors are returned by the API as HTTP 200 with an `error` object (`code`, `message`). Submit calls return that body as-is, so check `response?["error"]`; `WaitForTaskAsync` throws on them.

## License

MIT
