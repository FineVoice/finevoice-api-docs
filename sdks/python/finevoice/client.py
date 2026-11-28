from __future__ import annotations

import time
from typing import Any, Dict, Optional, Union

import requests

DEFAULT_BASE_URL = "https://apis.finevoice.ai"


class FineVoiceError(Exception):
    def __init__(self, message: str, status: Optional[int] = None, body: Any = None):
        super().__init__(message)
        self.status = status
        self.body = body


def _task_id(data: Any) -> Optional[str]:
    if isinstance(data, dict):
        return data.get("taskId") or data.get("task_id")
    return None


class FineVoice:
    """FineVoice API client. Request bodies are plain dicts using the API field names."""

    def __init__(self, api_key: str, base_url: str = DEFAULT_BASE_URL, timeout: float = 120):
        if not api_key:
            raise ValueError("api_key is required")
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._session = requests.Session()
        self._session.headers.update({"Authorization": f"Bearer {api_key}"})

    # ---- core ----
    def request(
        self,
        method: str,
        path: str,
        json: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> Union[Dict[str, Any], bytes]:
        params = {k: v for k, v in (params or {}).items() if v is not None}
        resp = self._session.request(
            method, self.base_url + path, json=json, params=params, timeout=self.timeout
        )
        if not resp.ok:
            try:
                body: Any = resp.json()
            except ValueError:
                body = resp.text
            raise FineVoiceError(f"HTTP {resp.status_code} on {method} {path}", resp.status_code, body)
        if "json" in resp.headers.get("Content-Type", ""):
            return resp.json()
        return resp.content

    def _post(self, path: str, body: Dict[str, Any]):
        return self.request("POST", path, json=body)

    # ---- tasks ----
    def get_task(self, task_id: str):
        return self.request("GET", f"/v1/task/{task_id}")

    def wait_for_task(self, task_or_id: Union[str, Dict[str, Any]], interval: float = 5.0, timeout: float = 600.0):
        """Poll until the task completes. Accepts a task id or a submit response."""
        task_id = task_or_id if isinstance(task_or_id, str) else _task_id(task_or_id)
        if not task_id:
            raise FineVoiceError("No taskId in response; the result may already be available.")
        deadline = time.monotonic() + timeout
        time.sleep(min(2.0, interval))
        while True:
            data = self.get_task(task_id)
            d = data if isinstance(data, dict) else {}
            status = d.get("status")
            err = d.get("error")
            if status in (3, "3", "success", "completed"):
                return data
            gateway = (
                isinstance(status, int) and status >= 500
                and "/proxy/" in str(d.get("path", "")) and not d.get("taskId")
            )
            if status in ("failed", "error") or (isinstance(status, int) and status >= 4 and not gateway):
                raise FineVoiceError(f"Task {task_id} failed", body=data)
            has_err = isinstance(err, dict) and (err.get("message") or err.get("code"))
            transient = has_err and status is None and err.get("code") == "failed"
            if has_err and not transient:
                raise FineVoiceError(f"Task {task_id} failed: {err}", body=data)
            if time.monotonic() > deadline:
                raise FineVoiceError(f"Timed out waiting for task {task_id}", body=data)
            time.sleep(interval)

    # ---- audio ----
    def speech_synthesis(self, body): return self._post("/v1/audio/speech-synthesis", body)
    def voice_conversion(self, body): return self._post("/v1/audio/voice-conversion", body)
    def speech_to_text(self, body): return self._post("/v1/audio/stt", body)
    def sfx_generation(self, body): return self._post("/v1/audio/sfx-generation", body)
    def audio_separation(self, body): return self._post("/v1/audio/separation", body)
    def enhance_audio(self, body): return self._post("/v1/audio/enhanceaudio", body)
    def reader_gen(self, body): return self._post("/v1/audio/readergen", body)
    def podcast_gen(self, body): return self._post("/v1/audio/podcastgen", body)
    def dubbing_gen(self, body): return self._post("/v1/audio/dubbinggen", body)

    # ---- voice ----
    def train_voice(self, body): return self._post("/v1/voice/train", body)
    def design_voice(self, body): return self._post("/v1/voice/design", body)

    def get_voice(self, name: str, desig_uuid: Optional[str] = None):
        return self.request("GET", f"/v1/voice/{name}", params={"desigUuid": desig_uuid})

    def page_voices(self, **filters):
        """Filters: categroy, primary_category, gender, language, keyword, page, limit, tts, style, age, sub_category."""
        return self.request("GET", "/v1/voice/pagevoices", params=filters)

    # ---- music ----
    def music_gen_by_prompt(self, body): return self._post("/v1/music/musicgenbyprompt", body)
    def music_gen(self, body): return self._post("/v1/music/musicgen", body)

    # ---- enhancer ----
    def speech_enhancement(self, body): return self._post("/v1/enhancer/speech_enhancement", body)
    def remove_mouth_sounds(self, body): return self._post("/v1/enhancer/remove_mouth_sounds", body)
    def remove_long_silences(self, body): return self._post("/v1/enhancer/remove_long_silences", body)
    def filler_words_remove(self, body): return self._post("/v1/enhancer/filler_words/remove", body)
    def stuttering_remove(self, body): return self._post("/v1/enhancer/stuttering/remove", body)
    def audio_normalization(self, body): return self._post("/v1/enhancer/audio_normalization", body)
    def process_pipeline(self, body): return self._post("/v1/enhancer/process/pipeline", body)
