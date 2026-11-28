export const DEFAULT_BASE_URL = "https://apis.finevoice.ai";

export type Body = Record<string, unknown>;

export interface TaskResponse {
  status?: number | string;
  taskId?: string;
  task_id?: string;
  url?: string;
  urls?: string[];
  error?: { code?: string; message?: string } | null;
  [key: string]: unknown;
}

export interface PageVoicesParams {
  categroy?: "all" | "my_voices" | "favorite";
  primary_category?: string;
  gender?: string;
  language?: string;
  keyword?: string;
  page?: number;
  limit?: number;
  tts?: boolean;
  style?: string;
  age?: string;
  sub_category?: string;
}

export class FineVoiceError extends Error {
  constructor(message: string, public status?: number, public body?: unknown) {
    super(message);
    this.name = "FineVoiceError";
  }
}

export interface ClientOptions {
  apiKey: string;
  baseUrl?: string;
  fetch?: typeof fetch;
}

export class FineVoice {
  private apiKey: string;
  private baseUrl: string;
  private fetchImpl: typeof fetch;

  constructor(opts: ClientOptions) {
    if (!opts.apiKey) throw new Error("apiKey is required");
    this.apiKey = opts.apiKey;
    this.baseUrl = (opts.baseUrl ?? DEFAULT_BASE_URL).replace(/\/+$/, "");
    this.fetchImpl = opts.fetch ?? fetch;
  }

  /** Returns parsed JSON, or an ArrayBuffer when the endpoint returns a file. */
  async request<T = TaskResponse>(
    method: string,
    path: string,
    opts: { body?: Body; query?: Record<string, unknown> } = {},
  ): Promise<T> {
    const url = new URL(this.baseUrl + path);
    for (const [k, v] of Object.entries(opts.query ?? {})) {
      if (v !== undefined && v !== null) url.searchParams.set(k, String(v));
    }
    const res = await this.fetchImpl(url, {
      method,
      headers: {
        Authorization: `Bearer ${this.apiKey}`,
        ...(opts.body ? { "Content-Type": "application/json" } : {}),
      },
      body: opts.body ? JSON.stringify(opts.body) : undefined,
    });
    const isJson = (res.headers.get("content-type") ?? "").includes("json");
    if (!res.ok) {
      const errBody = isJson ? await res.json().catch(() => null) : await res.text();
      throw new FineVoiceError(`HTTP ${res.status} on ${method} ${path}`, res.status, errBody);
    }
    return (isJson ? await res.json() : await res.arrayBuffer()) as T;
  }

  private post<T = TaskResponse>(path: string, body: Body) {
    return this.request<T>("POST", path, { body });
  }

  // ---- tasks ----
  getTask(taskId: string) {
    return this.request<TaskResponse>("GET", `/v1/task/${encodeURIComponent(taskId)}`);
  }

  /** Polls until the task completes. Accepts a task id or a submit response. */
  async waitForTask(
    taskOrId: string | TaskResponse,
    opts: { intervalMs?: number; timeoutMs?: number } = {},
  ): Promise<TaskResponse> {
    const id = typeof taskOrId === "string" ? taskOrId : taskOrId.taskId ?? taskOrId.task_id;
    if (!id) throw new FineVoiceError("No taskId in response; the result may already be available.");
    const interval = opts.intervalMs ?? 5000;
    const deadline = Date.now() + (opts.timeoutMs ?? 600_000);
    await new Promise((r) => setTimeout(r, Math.min(2000, interval)));
    for (;;) {
      const data = await this.getTask(id);
      const s: unknown = data.status;
      const err = data.error;
      if (s === 3 || s === "3" || s === "success" || s === "completed") return data;
      const gateway = typeof s === "number" && s >= 500 && String((data as any).path ?? "").includes("/proxy/") && !data.taskId;
      if (s === "failed" || s === "error" || (typeof s === "number" && s >= 4 && !gateway)) {
        throw new FineVoiceError(`Task ${id} failed`, undefined, data);
      }
      const hasErr = !!err && !!(err.message || err.code);
      const transient = hasErr && (s === undefined || s === null) && err!.code === "failed";
      if (hasErr && !transient) {
        throw new FineVoiceError(`Task ${id} failed: ${JSON.stringify(err)}`, undefined, data);
      }
      if (Date.now() > deadline) throw new FineVoiceError(`Timed out waiting for task ${id}`, undefined, data);
      await new Promise((r) => setTimeout(r, interval));
    }
  }

  // ---- audio ----
  speechSynthesis(body: { voice: string; text: string } & Body) { return this.post("/v1/audio/speech-synthesis", body); }
  voiceConversion(body: Body) { return this.post("/v1/audio/voice-conversion", body); }
  speechToText(body: Body) { return this.post("/v1/audio/stt", body); }
  sfxGeneration(body: Body) { return this.post("/v1/audio/sfx-generation", body); }
  audioSeparation(body: Body) { return this.post("/v1/audio/separation", body); }
  enhanceAudio(body: Body) { return this.post("/v1/audio/enhanceaudio", body); }
  readerGen(body: Body) { return this.post("/v1/audio/readergen", body); }
  podcastGen(body: Body) { return this.post("/v1/audio/podcastgen", body); }
  dubbingGen(body: Body) { return this.post("/v1/audio/dubbinggen", body); }

  // ---- voice ----
  trainVoice(body: Body) { return this.post<Body>("/v1/voice/train", body); }
  designVoice(body: Body) { return this.post<Body>("/v1/voice/design", body); }
  getVoice(name: string, desigUuid?: string) {
    return this.request<Body>("GET", `/v1/voice/${encodeURIComponent(name)}`, { query: { desigUuid } });
  }
  pageVoices(params: PageVoicesParams = {}) {
    return this.request<Body>("GET", "/v1/voice/pagevoices", { query: { ...params } });
  }

  // ---- music ----
  musicGenByPrompt(body: Body) { return this.post<Body>("/v1/music/musicgenbyprompt", body); }
  musicGen(body: Body) { return this.post<Body>("/v1/music/musicgen", body); }

  // ---- enhancer ----
  speechEnhancement(body: Body) { return this.post<Body | ArrayBuffer>("/v1/enhancer/speech_enhancement", body); }
  removeMouthSounds(body: Body) { return this.post<Body | ArrayBuffer>("/v1/enhancer/remove_mouth_sounds", body); }
  removeLongSilences(body: Body) { return this.post<Body | ArrayBuffer>("/v1/enhancer/remove_long_silences", body); }
  fillerWordsRemove(body: Body) { return this.post<Body | ArrayBuffer>("/v1/enhancer/filler_words/remove", body); }
  stutteringRemove(body: Body) { return this.post<Body | ArrayBuffer>("/v1/enhancer/stuttering/remove", body); }
  audioNormalization(body: Body) { return this.post<Body | ArrayBuffer>("/v1/enhancer/audio_normalization", body); }
  processPipeline(body: Body) { return this.post<Body>("/v1/enhancer/process/pipeline", body); }
}
