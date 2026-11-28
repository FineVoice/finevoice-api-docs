# FineVoice PHP SDK

Official PHP client for the [FineVoice API](https://api.finevoice.ai): text to speech, voice conversion, speech to text, sound effects, music generation, voice design/training, and audio enhancement.

- PHP 7.4+ with the `curl` and `json` extensions
- No third-party dependencies
- Full API reference: https://api.finevoice.ai

## Installation

The package is not on Packagist yet. Copy the `sdks/php` folder into your project and load it with Composer's autoloader (or `require` `src/Client.php` directly).

```php
require 'vendor/autoload.php';
```

## Authentication

Create an API key in the FineVoice dashboard and pass it to the client. Read it from the environment rather than hard-coding it.

```php
$client = new FineVoice\Client(getenv('FINEVOICE_API_KEY'));
```

The constructor also accepts a base URL (default `https://apis.finevoice.ai`) and a timeout in seconds (default `120`).

## Quick start

Most generation endpoints are asynchronous: the call returns a `taskId`, and you poll until the task finishes. `waitForTask` does this for you.

```php
$task = $client->speechSynthesis([
    'voice' => 'james',
    'text'  => '[happy] Hello from FineVoice!',
]);

$result = $client->waitForTask($task); // polls GET /v1/task/{id}
echo $result['url'];
```

### Browse voices

```php
$page  = $client->pageVoices(['language' => 'en-US', 'page' => 0, 'limit' => 20]);
$voice = $client->getVoice('james');
```

### Music generation

Music tasks take roughly 50 to 60 seconds. The default polling allows up to 10 minutes.

```php
$task   = $client->musicGenByPrompt(['prompt' => 'calm lo-fi beat with soft piano']);
$result = $client->waitForTask($task);
print_r($result['urls']);
```

### Audio enhancement

The enhancer endpoints respond directly with a download link, so no polling is needed.

```php
$out = $client->speechEnhancement(['url' => 'https://example.com/noisy.mp3']);
echo $out['download_url'];
```

## Async tasks and polling

```php
$client->waitForTask($taskOrId, float $interval = 5.0, float $timeout = 600.0): array
```

- Accepts either the submit response (array) or a task id string.
- A task is finished when its status is `success` (or `3`). `failed` or a numeric status of `4` or higher throws `FineVoice\FineVoiceException`.
- Any other status keeps polling. Transient gateway errors (5xx on proxy paths) are retried.
- Throws if `$timeout` seconds pass without completion.
- Use `$client->getTask($taskId)` for a single status check.

## Available methods

Request bodies are associative arrays that use the API field names from the [API reference](https://api.finevoice.ai).

| Area      | Methods |
| --------- | ------- |
| Audio     | `speechSynthesis`, `voiceConversion`, `speechToText`, `sfxGeneration`, `audioSeparation`, `enhanceAudio`, `readerGen`, `podcastGen`, `dubbingGen` |
| Voices    | `trainVoice`, `designVoice`, `getVoice`, `pageVoices` |
| Music     | `musicGenByPrompt`, `musicGen` |
| Enhancer  | `speechEnhancement`, `removeMouthSounds`, `removeLongSilences`, `fillerWordsRemove`, `stutteringRemove`, `audioNormalization`, `processPipeline` |
| Tasks     | `getTask`, `waitForTask` |
| Low level | `request($method, $path, $body, $query)` for any endpoint not yet wrapped |

## Error handling

Failures throw `FineVoice\FineVoiceException` with `->status` (HTTP status code, if any) and `->body` (parsed response).

```php
try {
    $client->speechSynthesis(['voice' => 'james', 'text' => 'Hi']);
} catch (FineVoice\FineVoiceException $e) {
    echo $e->status, ' ', json_encode($e->body);
}
```

Some validation errors are returned by the API as HTTP 200 with an `error` object (`code`, `message`). Submit calls return that body as-is, so check `$response['error'] ?? null`; `waitForTask` throws on them.

## License

MIT
