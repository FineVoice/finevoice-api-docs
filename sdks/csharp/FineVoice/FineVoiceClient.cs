using System.Net.Http.Headers;
using System.Text;
using System.Text.Json;
using System.Text.Json.Nodes;

namespace FineVoice;

public class FineVoiceException : Exception
{
    public int? Status { get; }
    public string? Body { get; }

    public FineVoiceException(string message, int? status = null, string? body = null) : base(message)
    {
        Status = status;
        Body = body;
    }
}

public class FineVoiceClient : IDisposable
{
    public const string DefaultBaseUrl = "https://apis.finevoice.ai";

    private readonly HttpClient _http;
    private readonly bool _ownsClient;

    public FineVoiceClient(string apiKey, string baseUrl = DefaultBaseUrl, HttpClient? httpClient = null)
    {
        if (string.IsNullOrEmpty(apiKey)) throw new ArgumentException("apiKey is required", nameof(apiKey));
        _ownsClient = httpClient == null;
        _http = httpClient ?? new HttpClient(
            new HttpClientHandler { AutomaticDecompression = System.Net.DecompressionMethods.All })
        { Timeout = TimeSpan.FromSeconds(120) };
        _http.BaseAddress = new Uri(baseUrl.TrimEnd('/') + "/");
        _http.DefaultRequestHeaders.Authorization = new AuthenticationHeaderValue("Bearer", apiKey);
    }

    public void Dispose()
    {
        if (_ownsClient) _http.Dispose();
    }

    /// <summary>Sends a request. Returns the parsed JSON, or null if the endpoint returned a file (use <see cref="RequestBytesAsync"/>).</summary>
    public async Task<JsonNode?> RequestAsync(HttpMethod method, string path, object? body = null,
        IDictionary<string, object?>? query = null, CancellationToken ct = default)
    {
        using var res = await SendAsync(method, path, body, query, ct);
        var text = await res.Content.ReadAsStringAsync(ct);
        return string.IsNullOrWhiteSpace(text) ? null : JsonNode.Parse(text);
    }

    /// <summary>For endpoints that return an audio file directly.</summary>
    public async Task<byte[]> RequestBytesAsync(HttpMethod method, string path, object? body = null, CancellationToken ct = default)
    {
        using var res = await SendAsync(method, path, body, null, ct);
        return await res.Content.ReadAsByteArrayAsync(ct);
    }

    private async Task<HttpResponseMessage> SendAsync(HttpMethod method, string path, object? body,
        IDictionary<string, object?>? query, CancellationToken ct)
    {
        var rel = path.TrimStart('/');
        if (query != null)
        {
            var parts = query.Where(kv => kv.Value != null).Select(kv =>
                $"{Uri.EscapeDataString(kv.Key)}={Uri.EscapeDataString(Convert.ToString(kv.Value is bool b ? (b ? "true" : "false") : kv.Value, System.Globalization.CultureInfo.InvariantCulture)!)}");
            var qs = string.Join("&", parts);
            if (qs.Length > 0) rel += "?" + qs;
        }

        using var req = new HttpRequestMessage(method, rel);
        if (body != null)
            req.Content = new StringContent(JsonSerializer.Serialize(body), Encoding.UTF8, "application/json");

        var res = await _http.SendAsync(req, ct);
        if (!res.IsSuccessStatusCode)
        {
            var err = await res.Content.ReadAsStringAsync(ct);
            res.Dispose();
            throw new FineVoiceException($"HTTP {(int)res.StatusCode} on {method} {path}", (int)res.StatusCode, err);
        }
        return res;
    }

    private Task<JsonNode?> PostAsync(string path, object body, CancellationToken ct) =>
        RequestAsync(HttpMethod.Post, path, body, null, ct);

    // ---- tasks ----
    public Task<JsonNode?> GetTaskAsync(string taskId, CancellationToken ct = default) =>
        RequestAsync(HttpMethod.Get, $"/v1/task/{Uri.EscapeDataString(taskId)}", null, null, ct);

    /// <summary>Polls until the task completes. Accepts a task id.</summary>
    public async Task<JsonNode> WaitForTaskAsync(string taskId, TimeSpan? interval = null, TimeSpan? timeout = null,
        CancellationToken ct = default)
    {
        var delay = interval ?? TimeSpan.FromSeconds(5);
        var deadline = DateTime.UtcNow + (timeout ?? TimeSpan.FromMinutes(10));
        await Task.Delay(delay < TimeSpan.FromSeconds(2) ? delay : TimeSpan.FromSeconds(2), ct);
        while (true)
        {
            var data = await GetTaskAsync(taskId, ct) ?? throw new FineVoiceException("Empty task response");
            var status = data["status"];
            var hasStatus = false;
            if (status is JsonValue sv)
            {
                if (sv.TryGetValue<int>(out var code))
                {
                    hasStatus = true;
                    if (code == 3) return data;
                    var gateway = code >= 500 && ((string?)data["path"] ?? "").Contains("/proxy/") && data["taskId"] is null;
                    if (code >= 4 && !gateway) throw new FineVoiceException($"Task {taskId} failed", null, data.ToJsonString());
                }
                else if (sv.TryGetValue<string>(out var s))
                {
                    hasStatus = true;
                    if (s is "3" or "success" or "completed") return data;
                    if (s is "failed" or "error") throw new FineVoiceException($"Task {taskId} failed", null, data.ToJsonString());
                }
            }
            var err = data["error"];
            if (err is JsonObject eo && (!string.IsNullOrEmpty((string?)eo["message"]) || !string.IsNullOrEmpty((string?)eo["code"])))
            {
                var transient = !hasStatus && (string?)eo["code"] == "failed";
                if (!transient) throw new FineVoiceException($"Task {taskId} failed: {err.ToJsonString()}", null, data.ToJsonString());
            }
            if (DateTime.UtcNow > deadline) throw new FineVoiceException($"Timed out waiting for task {taskId}", null, data.ToJsonString());
            await Task.Delay(delay, ct);
        }
    }

    /// <summary>Extracts taskId / task_id from a submit response.</summary>
    public static string? GetTaskId(JsonNode? response) => (string?)response?["taskId"] ?? (string?)response?["task_id"];

    // ---- audio ----
    public Task<JsonNode?> SpeechSynthesisAsync(object body, CancellationToken ct = default) => PostAsync("/v1/audio/speech-synthesis", body, ct);
    public Task<JsonNode?> VoiceConversionAsync(object body, CancellationToken ct = default) => PostAsync("/v1/audio/voice-conversion", body, ct);
    public Task<JsonNode?> SpeechToTextAsync(object body, CancellationToken ct = default) => PostAsync("/v1/audio/stt", body, ct);
    public Task<JsonNode?> SfxGenerationAsync(object body, CancellationToken ct = default) => PostAsync("/v1/audio/sfx-generation", body, ct);
    public Task<JsonNode?> AudioSeparationAsync(object body, CancellationToken ct = default) => PostAsync("/v1/audio/separation", body, ct);
    public Task<JsonNode?> EnhanceAudioAsync(object body, CancellationToken ct = default) => PostAsync("/v1/audio/enhanceaudio", body, ct);
    public Task<JsonNode?> ReaderGenAsync(object body, CancellationToken ct = default) => PostAsync("/v1/audio/readergen", body, ct);
    public Task<JsonNode?> PodcastGenAsync(object body, CancellationToken ct = default) => PostAsync("/v1/audio/podcastgen", body, ct);
    public Task<JsonNode?> DubbingGenAsync(object body, CancellationToken ct = default) => PostAsync("/v1/audio/dubbinggen", body, ct);

    // ---- voice ----
    public Task<JsonNode?> TrainVoiceAsync(object body, CancellationToken ct = default) => PostAsync("/v1/voice/train", body, ct);
    public Task<JsonNode?> DesignVoiceAsync(object body, CancellationToken ct = default) => PostAsync("/v1/voice/design", body, ct);

    public Task<JsonNode?> GetVoiceAsync(string name, string? desigUuid = null, CancellationToken ct = default) =>
        RequestAsync(HttpMethod.Get, $"/v1/voice/{Uri.EscapeDataString(name)}", null,
            new Dictionary<string, object?> { ["desigUuid"] = desigUuid }, ct);

    /// <summary>Filters: categroy, primary_category, gender, language, keyword, page, limit, tts, style, age, sub_category.</summary>
    public Task<JsonNode?> PageVoicesAsync(IDictionary<string, object?>? filters = null, CancellationToken ct = default) =>
        RequestAsync(HttpMethod.Get, "/v1/voice/pagevoices", null, filters, ct);

    // ---- music ----
    public Task<JsonNode?> MusicGenByPromptAsync(object body, CancellationToken ct = default) => PostAsync("/v1/music/musicgenbyprompt", body, ct);
    public Task<JsonNode?> MusicGenAsync(object body, CancellationToken ct = default) => PostAsync("/v1/music/musicgen", body, ct);

    // ---- enhancer (use RequestBytesAsync with the same path if the endpoint returns a file) ----
    public Task<JsonNode?> SpeechEnhancementAsync(object body, CancellationToken ct = default) => PostAsync("/v1/enhancer/speech_enhancement", body, ct);
    public Task<JsonNode?> RemoveMouthSoundsAsync(object body, CancellationToken ct = default) => PostAsync("/v1/enhancer/remove_mouth_sounds", body, ct);
    public Task<JsonNode?> RemoveLongSilencesAsync(object body, CancellationToken ct = default) => PostAsync("/v1/enhancer/remove_long_silences", body, ct);
    public Task<JsonNode?> FillerWordsRemoveAsync(object body, CancellationToken ct = default) => PostAsync("/v1/enhancer/filler_words/remove", body, ct);
    public Task<JsonNode?> StutteringRemoveAsync(object body, CancellationToken ct = default) => PostAsync("/v1/enhancer/stuttering/remove", body, ct);
    public Task<JsonNode?> AudioNormalizationAsync(object body, CancellationToken ct = default) => PostAsync("/v1/enhancer/audio_normalization", body, ct);
    public Task<JsonNode?> ProcessPipelineAsync(object body, CancellationToken ct = default) => PostAsync("/v1/enhancer/process/pipeline", body, ct);
}
