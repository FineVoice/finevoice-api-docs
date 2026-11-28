<?php

declare(strict_types=1);

namespace FineVoice;

class FineVoiceException extends \RuntimeException
{
    /** @var mixed */
    public $body;
    public ?int $status;

    public function __construct(string $message, ?int $status = null, $body = null)
    {
        parent::__construct($message);
        $this->status = $status;
        $this->body = $body;
    }
}

class Client
{
    public const DEFAULT_BASE_URL = 'https://apis.finevoice.ai';

    private string $apiKey;
    private string $baseUrl;
    private int $timeout;

    public function __construct(string $apiKey, string $baseUrl = self::DEFAULT_BASE_URL, int $timeout = 120)
    {
        if ($apiKey === '') {
            throw new \InvalidArgumentException('apiKey is required');
        }
        $this->apiKey = $apiKey;
        $this->baseUrl = rtrim($baseUrl, '/');
        $this->timeout = $timeout;
    }

    /**
     * Returns decoded JSON (array), or the raw body string when the endpoint returns a file.
     *
     * @return array|string
     */
    public function request(string $method, string $path, ?array $body = null, array $query = [])
    {
        $query = array_filter($query, static fn($v) => $v !== null);
        foreach ($query as $k => $v) {
            if (is_bool($v)) {
                $query[$k] = $v ? 'true' : 'false';
            }
        }
        $url = $this->baseUrl . $path . ($query ? '?' . http_build_query($query) : '');

        $headers = ['Authorization: Bearer ' . $this->apiKey];
        $ch = curl_init($url);
        curl_setopt_array($ch, [
            CURLOPT_CUSTOMREQUEST => $method,
            CURLOPT_RETURNTRANSFER => true,
            CURLOPT_TIMEOUT => $this->timeout,
            CURLOPT_ENCODING => '',
        ]);
        if ($body !== null) {
            $headers[] = 'Content-Type: application/json';
            curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($body, JSON_UNESCAPED_UNICODE));
        }
        curl_setopt($ch, CURLOPT_HTTPHEADER, $headers);

        $raw = curl_exec($ch);
        if ($raw === false) {
            $err = curl_error($ch);
            curl_close($ch);
            throw new FineVoiceException("Request failed: $err");
        }
        $status = (int) curl_getinfo($ch, CURLINFO_RESPONSE_CODE);
        $type = (string) curl_getinfo($ch, CURLINFO_CONTENT_TYPE);
        curl_close($ch);

        $isJson = stripos($type, 'json') !== false;
        $data = $isJson ? json_decode((string) $raw, true) : $raw;
        if ($status >= 400) {
            throw new FineVoiceException("HTTP $status on $method $path", $status, $data);
        }
        return $data;
    }

    private function post(string $path, array $body)
    {
        return $this->request('POST', $path, $body);
    }

    // ---- tasks ----
    public function getTask(string $taskId): array
    {
        return $this->request('GET', '/v1/task/' . rawurlencode($taskId));
    }

    /**
     * Polls until the task completes. Accepts a task id or a submit response.
     *
     * @param string|array $taskOrId
     */
    public function waitForTask($taskOrId, float $interval = 5.0, float $timeout = 600.0): array
    {
        $id = is_string($taskOrId) ? $taskOrId : ($taskOrId['taskId'] ?? $taskOrId['task_id'] ?? null);
        if (!$id) {
            throw new FineVoiceException('No taskId in response; the result may already be available.');
        }
        $deadline = microtime(true) + $timeout;
        usleep((int) (min(2.0, $interval) * 1_000_000));
        while (true) {
            $data = $this->getTask($id);
            $s = $data['status'] ?? null;
            $err = $data['error'] ?? null;
            if ($s === 3 || $s === '3' || $s === 'success' || $s === 'completed') {
                return $data;
            }
            $gateway = is_int($s) && $s >= 500 && strpos((string) ($data['path'] ?? ''), '/proxy/') !== false && empty($data['taskId']);
            if ($s === 'failed' || $s === 'error' || (is_int($s) && $s >= 4 && !$gateway)) {
                throw new FineVoiceException("Task $id failed", null, $data);
            }
            $hasErr = is_array($err) && (!empty($err['message']) || !empty($err['code']));
            $transient = $hasErr && $s === null && ($err['code'] ?? null) === 'failed';
            if ($hasErr && !$transient) {
                throw new FineVoiceException("Task $id failed: " . json_encode($err), null, $data);
            }
            if (microtime(true) > $deadline) {
                throw new FineVoiceException("Timed out waiting for task $id", null, $data);
            }
            usleep((int) ($interval * 1_000_000));
        }
    }

    // ---- audio ----
    public function speechSynthesis(array $body) { return $this->post('/v1/audio/speech-synthesis', $body); }
    public function voiceConversion(array $body) { return $this->post('/v1/audio/voice-conversion', $body); }
    public function speechToText(array $body) { return $this->post('/v1/audio/stt', $body); }
    public function sfxGeneration(array $body) { return $this->post('/v1/audio/sfx-generation', $body); }
    public function audioSeparation(array $body) { return $this->post('/v1/audio/separation', $body); }
    public function enhanceAudio(array $body) { return $this->post('/v1/audio/enhanceaudio', $body); }
    public function readerGen(array $body) { return $this->post('/v1/audio/readergen', $body); }
    public function podcastGen(array $body) { return $this->post('/v1/audio/podcastgen', $body); }
    public function dubbingGen(array $body) { return $this->post('/v1/audio/dubbinggen', $body); }

    // ---- voice ----
    public function trainVoice(array $body) { return $this->post('/v1/voice/train', $body); }
    public function designVoice(array $body) { return $this->post('/v1/voice/design', $body); }

    public function getVoice(string $name, ?string $desigUuid = null)
    {
        return $this->request('GET', '/v1/voice/' . rawurlencode($name), null, ['desigUuid' => $desigUuid]);
    }

    /** Filters: categroy, primary_category, gender, language, keyword, page, limit, tts, style, age, sub_category. */
    public function pageVoices(array $filters = [])
    {
        return $this->request('GET', '/v1/voice/pagevoices', null, $filters);
    }

    // ---- music ----
    public function musicGenByPrompt(array $body) { return $this->post('/v1/music/musicgenbyprompt', $body); }
    public function musicGen(array $body) { return $this->post('/v1/music/musicgen', $body); }

    // ---- enhancer ----
    public function speechEnhancement(array $body) { return $this->post('/v1/enhancer/speech_enhancement', $body); }
    public function removeMouthSounds(array $body) { return $this->post('/v1/enhancer/remove_mouth_sounds', $body); }
    public function removeLongSilences(array $body) { return $this->post('/v1/enhancer/remove_long_silences', $body); }
    public function fillerWordsRemove(array $body) { return $this->post('/v1/enhancer/filler_words/remove', $body); }
    public function stutteringRemove(array $body) { return $this->post('/v1/enhancer/stuttering/remove', $body); }
    public function audioNormalization(array $body) { return $this->post('/v1/enhancer/audio_normalization', $body); }
    public function processPipeline(array $body) { return $this->post('/v1/enhancer/process/pipeline', $body); }
}
