import json


def make_post(tag, summary, desc, op_id, schema_ref, resp_desc="Task accepted. Returns a taskId for async polling or the result URL directly.", resp_schema_ref="AudioTaskResponse"):
    return {"post": {
        "tags": [tag],
        "summary": summary,
        "description": desc,
        "operationId": op_id,
        "requestBody": {
            "required": True,
            "content": {"application/json": {"schema": {"$ref": f"#/components/schemas/{schema_ref}"}}}
        },
        "responses": {
            "200": {
                "description": resp_desc,
                "content": {"application/json": {"schema": {"$ref": f"#/components/schemas/{resp_schema_ref}"} if resp_schema_ref else {"type": "object"}}}
            },
            "401": {"description": "Unauthorized — invalid or missing API key."},
            "422": {"description": "Validation error — check request body fields."}
        }
    }}


def make_post_obj(tag, summary, desc, op_id, schema_ref, resp_desc):
    return {"post": {
        "tags": [tag],
        "summary": summary,
        "description": desc,
        "operationId": op_id,
        "requestBody": {
            "required": True,
            "content": {"application/json": {"schema": {"$ref": f"#/components/schemas/{schema_ref}"}}}
        },
        "responses": {
            "200": {"description": resp_desc, "content": {"application/json": {"schema": {"type": "object"}}}},
            "401": {"description": "Unauthorized — invalid or missing API key."},
            "422": {"description": "Validation error — check request body fields."}
        }
    }}


openapi = {
    "openapi": "3.0.1",
    "info": {
        "title": "FineVoice API",
        "description": "This is the documentation for the FineVoice API. If you have any questions or need assistance, please contact support@fineshare.ai.",
        "version": "v1"
    },
    "servers": [{"url": "https://apis.finevoice.ai", "description": "FineVoice API Gateway"}],
    "security": [{"BearerAuth": []}],
    "paths": {
        # ── Audio Service ─────────────────────────────────────────────────────
        "/v1/audio/speech-synthesis": make_post(
            "Audio", "Text to Speech",
            "Convert text into natural-sounding speech using a selected AI voice model.",
            "SpeechSynthesis", "TextToSpeechRequest"
        ),
        "/v1/audio/voice-conversion": make_post(
            "Audio", "Voice Conversion",
            "Transform the voice in an audio file to a different AI voice while preserving the original content.",
            "VoiceConversion", "VoiceConversionRequest"
        ),
        "/v1/audio/stt": make_post(
            "Audio", "Speech to Text",
            "Transcribe speech from an audio or video URL into text, with optional speaker diarization and word-level timestamps.",
            "SpeechToText", "SpeechToTextRequest"
        ),
        "/v1/audio/sfx-generation": make_post(
            "Audio", "Sound Effect Generation",
            "Generate royalty-free sound effects from a text prompt or a source video/image.",
            "SfxGeneration", "SoundEffectGenerationRequest"
        ),
        "/v1/audio/separation": make_post(
            "Audio", "Audio Separation",
            "Separate vocals, instruments, and other audio stems from an audio file using AI.",
            "AudioSeparation", "SeparationRequest"
        ),
        "/v1/audio/enhanceaudio": make_post(
            "Audio", "Enhance Audio",
            "Enhance audio files with AI-powered noise removal, stuttering/filler removal, loudness normalization, transcription, and more.",
            "EnhanceAudio", "EnhanceAudioRequest"
        ),
        "/v1/audio/readergen": make_post(
            "Audio", "Reader Generation",
            "Generate an AI-narrated audio version of a given content URL (article, web page, document, etc.).",
            "ReaderGen", "ReaderGenerationRequest"
        ),
        "/v1/audio/podcastgen": make_post(
            "Audio", "Podcast Generation",
            "Generate a multi-speaker AI podcast from a script or prompt, with selectable voice models for each speaker.",
            "PodcastGen", "PodcastGenerationRequest"
        ),
        "/v1/audio/dubbinggen": make_post(
            "Audio", "Dubbing Generation",
            "Automatically dub an audio or video file into another language while preserving the original voice characteristics.",
            "DubbingGen", "DubbingGenerationRequest"
        ),
        # ── Voice Service ─────────────────────────────────────────────────────
        "/v1/voice/train": make_post_obj(
            "Voice", "Train Voice Model",
            "Create a custom AI voice model by providing a training audio URL and basic profile information.",
            "TrainVoice", "VoiceTrainRequest", "Training task accepted."
        ),
        "/v1/voice/design": make_post_obj(
            "Voice", "Voice Design",
            "Design a new AI voice from a text prompt and preview it with sample text.",
            "VoiceDesign", "VoiceDesignRequest", "Voice design task accepted."
        ),
        "/v1/voice/{name}": {"get": {
            "tags": ["Voice"],
            "summary": "Get Voice Detail",
            "description": "Retrieve detailed information about a specific voice model by its name.",
            "operationId": "GetVoiceDetail",
            "parameters": [
                {"name": "name", "in": "path", "required": True, "schema": {"type": "string"}, "description": "The voice model name.", "example": "james"},
                {"name": "desigUuid", "in": "query", "required": False, "schema": {"type": "string"}, "description": "Optional design UUID to retrieve a specific voice design version."}
            ],
            "responses": {
                "200": {"description": "Voice detail returned.", "content": {"application/json": {"schema": {"type": "object"}}}},
                "401": {"description": "Unauthorized — invalid or missing API key."},
                "404": {"description": "Voice not found."}
            }
        }},
        "/v1/voice/pagevoices": {"get": {
            "tags": ["Voice"],
            "summary": "List AI Voices",
            "description": "Retrieve a paginated, filterable list of available AI voice models.",
            "operationId": "PageVoices",
            "parameters": [
                {"name": "categroy", "in": "query", "required": False,
                 "schema": {"type": "string", "enum": ["all", "my_voices", "favorite"], "example": "all"},
                 "description": "Category filter. `all` returns every voice, `my_voices` returns custom models, `favorite` returns favorited voices."},
                {"name": "primary_category", "in": "query", "required": False,
                 "schema": {"type": "string", "enum": ["social-media", "advertisement", "characters-and-animation", "entertainment-and-tv", "informative-and-educational", "narrative-and-story", "interactive_media", "healthcare", "companions", "education_training", "enterprise", "all"], "example": "all"},
                 "description": "Primary category filter."},
                {"name": "gender", "in": "query", "required": False, "schema": {"type": "string"}, "description": "Filter by gender (e.g. `male`, `female`)."},
                {"name": "language", "in": "query", "required": False, "schema": {"type": "string", "example": "en-US"}, "description": "Language filter using locale codes such as `en-US`, `zh-CN`, `ja-JP`."},
                {"name": "keyword", "in": "query", "required": False, "schema": {"type": "string"}, "description": "Search keyword to filter voice names."},
                {"name": "page", "in": "query", "required": False, "schema": {"type": "integer", "format": "int32", "minimum": 0, "example": 0}, "description": "Page index, starting from 0."},
                {"name": "limit", "in": "query", "required": False, "schema": {"type": "integer", "format": "int32"}, "description": "Number of voices per page."},
                {"name": "tts", "in": "query", "required": False, "schema": {"type": "boolean"}, "description": "Filter for TTS-compatible voices only."},
                {"name": "style", "in": "query", "required": False, "schema": {"type": "string"}, "description": "Filter by voice style."},
                {"name": "age", "in": "query", "required": False, "schema": {"type": "string"}, "description": "Filter by age range."},
                {"name": "sub_category", "in": "query", "required": False, "schema": {"type": "string"}, "description": "Sub-category filter."}
            ],
            "responses": {
                "200": {"description": "Paginated list of voice models.", "content": {"application/json": {"schema": {"type": "object"}}}},
                "401": {"description": "Unauthorized — invalid or missing API key."}
            }
        }},
        # ── Task Service ──────────────────────────────────────────────────────
        "/v1/task/{task_id}": {"get": {
            "tags": ["Task"],
            "summary": "Get Task Status",
            "description": "Poll the status and result of an asynchronous audio processing task.",
            "operationId": "GetTaskStatus",
            "parameters": [
                {"name": "task_id", "in": "path", "required": True, "schema": {"type": "string"}, "description": "The task identifier returned by a previous API call.", "example": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"}
            ],
            "responses": {
                "200": {"description": "Task status and result.", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/TaskQueryResponse"}}}},
                "401": {"description": "Unauthorized — invalid or missing API key."},
                "404": {"description": "Task not found."}
            }
        }},
        # ── Music Service ─────────────────────────────────────────────────────
        "/v1/music/musicgenbyprompt": make_post_obj(
            "Music", "Music Generation by Prompt",
            "Generate a music track from a text prompt, with control over style, duration, and model version.",
            "MusicGenByPrompt", "MusicGenerationByPromptRequest", "Task accepted."
        ),
        "/v1/music/musicgen": make_post_obj(
            "Music", "Music Generation",
            "Generate a full music track with vocals and/or instrumentation from lyrics, style description, and reference tracks.",
            "MusicGen", "MusicGenerationRequest", "Task accepted."
        ),
        "/v1/music/cover": make_post_obj(
            "Music", "Music Cover",
            "Create an AI voice cover of a song by replacing the original vocals with a target AI voice model.",
            "MusicCover", "MusicCoverRequest", "Task accepted."
        ),
        # ── Enhancer Service ──────────────────────────────────────────────────
        "/v1/enhancer/speech_enhancement": make_post_obj(
            "Audio Enhancer", "Speech Enhancement",
            "Reduce background noise and enhance speech quality. Supports WAV/MP3/FLAC/AAC/OGG/OPUS/M4A/WEBM. Returns enhanced audio file.",
            "SpeechEnhancement", "SpeechEnhancementRequest", "Enhanced audio returned."
        ),
        "/v1/enhancer/speech_super_resolution": make_post_obj(
            "Audio Enhancer", "Speech Super Resolution",
            "Upsample low-quality audio from 8 kHz to 48 kHz using the MossFormer2_SR_48K model. Returns high sample-rate audio file.",
            "SpeechSuperResolution", "SpeechSuperResolutionRequest", "High sample-rate audio returned."
        ),
        "/v1/enhancer/speech_separation": make_post_obj(
            "Audio Enhancer", "Speech Separation",
            "Separate two speakers from a mixed audio file using the MossFormer2_SS_16K model. Use `speaker_index` (0 or 1) to select which speaker to return.",
            "EnhancerSpeechSeparation", "SpeechSeparationRequest", "Separated speaker audio returned."
        ),
        "/v1/enhancer/remove_mouth_sounds": make_post_obj(
            "Audio Enhancer", "Remove Mouth Sounds",
            "Remove mouth sounds (clicks, pops, breathing) from audio using RNNoise, Hush, or Whisper-based stutter detection.",
            "RemoveMouthSounds", "RemoveMouthSoundsRequest", "Processed audio returned."
        ),
        "/v1/enhancer/remove_long_silences": make_post_obj(
            "Audio Enhancer", "Remove Long Silences",
            "Detect and trim silence segments exceeding a threshold duration while preserving boundary silence to avoid abrupt cuts.",
            "RemoveLongSilences", "RemoveLongSilencesRequest", "Processed audio returned."
        ),
        "/v1/enhancer/filler_words/detect": make_post_obj(
            "Audio Enhancer", "Filler Words Detect",
            "Detect filler words (um, uh, er, hmm) in audio. Default mode uses a lightweight audio classifier (language-agnostic). Whisper mode uses ASR for precise word-level timestamps.",
            "FillerWordsDetect", "FillerWordsRequest", "Filler word timestamps returned."
        ),
        "/v1/enhancer/filler_words/remove": make_post_obj(
            "Audio Enhancer", "Filler Words Remove",
            "Detect and remove filler words from audio. Default mode uses an audio classifier; Whisper mode uses ASR to precisely locate and cut filler words.",
            "FillerWordsRemove", "FillerWordsRequest", "Processed audio file returned."
        ),
        "/v1/enhancer/stuttering/remove": make_post_obj(
            "Audio Enhancer", "Stuttering Remove",
            "Detect and remove stuttering segments from audio using Whisper ASR. Returns processed audio file.",
            "StutteringRemove", "StutteringRemoveRequest", "Processed audio file returned."
        ),
        "/v1/enhancer/audio_normalization": make_post_obj(
            "Audio Enhancer", "Audio Normalization",
            "Normalize audio loudness using peak, RMS, or combined normalization methods. Returns normalized audio file.",
            "AudioNormalization", "AudioNormalizationRequest", "Normalized audio file returned."
        ),
        "/v1/enhancer/process/pipeline": make_post_obj(
            "Audio Enhancer", "Process Pipeline",
            "All-in-one audio processing pipeline. Select steps via boolean flags. Execution order: (1) Speech Enhancement, (2) Remove Mouth Sounds, (3) Remove Long Silences, (4) Super Resolution, (5) Filler Words Removal, (6) Stuttering Removal, (7) Audio Normalization. Returns a download URL.",
            "ProcessPipeline", "PipelineRequest", "Processed audio download URL returned."
        ),
    },
    "components": {
        "securitySchemes": {
            "BearerAuth": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT",
                "description": "Bearer token (API key). Format: `Bearer {your_api_key}`"
            }
        },
        "schemas": {
            "ApiError": {
                "type": "object",
                "properties": {
                    "code": {"type": "string", "description": "Error code."},
                    "message": {"type": "string", "description": "Error message."}
                }
            },
            "AudioTaskResponse": {
                "type": "object",
                "description": "Standard response for audio processing tasks.",
                "properties": {
                    "status": {"type": "integer", "format": "int32", "description": "HTTP-style status code (200 for success, 202 for in-progress)."},
                    "url": {"type": "string", "description": "Download URL of the generated audio file (available when completed)."},
                    "taskId": {"type": "string", "description": "Task identifier for async polling. Use with GET /v1/task/{task_id}.", "example": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"},
                    "error": {"$ref": "#/components/schemas/ApiError"},
                    "urls": {"type": "array", "items": {"type": "string"}, "description": "Multiple output URLs (e.g. for separation stems)."},
                    "service": {"type": "string"},
                    "port": {"type": "string"},
                    "timestamp": {"type": "string"}
                }
            },
            "TaskQueryResponse": {
                "type": "object",
                "description": "Response for task status polling.",
                "properties": {
                    "status": {"type": "integer", "format": "int32", "description": "HTTP-style status code (200 for completed, 202 for in-progress)."},
                    "url": {"type": "string", "description": "Download URL of the result.", "example": "https://cdn.finevoice.ai/output/result.mp3"},
                    "taskId": {"type": "string", "description": "Task identifier.", "example": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"},
                    "error": {"$ref": "#/components/schemas/ApiError"},
                    "urls": {"type": "array", "items": {"type": "string"}, "description": "Multiple output URLs."},
                    "service": {"type": "string"},
                    "port": {"type": "string"},
                    "timestamp": {"type": "string"}
                }
            },
            "TextToSpeechRequest": {
                "type": "object",
                "description": "The text-to-speech request payload.",
                "properties": {
                    "voice": {"type": "string", "description": "The target voice model name. Retrieve available voices from the List AI Voices API.", "example": "james"},
                    "text": {"type": "string", "description": "The text content to synthesize. Supports emotion tags such as `[happy]`, `[sad]`, `[breathe]`.", "example": "[happy] Hello! Welcome to FineVoice."}
                }
            },
            "VoiceConversionRequest": {
                "type": "object",
                "description": "The voice conversion request payload.",
                "properties": {
                    "voice": {"type": "string", "description": "The target voice model name.", "example": "madison"},
                    "sourceUrl": {"type": "string", "description": "The source audio URL.", "example": "https://dlaudio.fineshare.net/cover/speak/30f23d17-634d-420e-99e7-d24097dc669b.mp3"},
                    "outputFormat": {"type": "string", "description": "The desired output audio format. Supported: `mp3`, `wav`.", "example": "mp3"},
                    "useAsync": {"type": "boolean", "description": "Set to `true` to process asynchronously and receive a `taskId` for polling.", "example": True}
                }
            },
            "SpeechToTextRequest": {
                "type": "object",
                "description": "The speech-to-text request payload.",
                "properties": {
                    "url": {"type": "string", "description": "The source audio or video URL.", "example": "https://example.com/audio.mp3"},
                    "language": {"type": "string", "description": "The source language code (e.g. `en`, `zh`, `ja`).", "example": "en"},
                    "title": {"type": "string", "description": "An optional task title for reference."},
                    "format": {"type": "string", "description": "Expected transcript output format: `srt`, `vtt`, `json`, `txt`.", "example": "json"},
                    "engine": {"type": "string", "description": "The transcription engine to use. Supported: `whisper`, `funasr`.", "example": "whisper"},
                    "useAsync": {"type": "boolean", "description": "Set to `true` to process asynchronously.", "example": True},
                    "word_level_timestamp_alignment": {"type": "boolean", "description": "Whether to include word-level timestamp alignment.", "example": False},
                    "speaker_diarization": {"type": "boolean", "description": "Whether to enable speaker diarization (identify multiple speakers).", "example": False},
                    "min_speakers": {"type": "integer", "format": "int32", "description": "Minimum number of speakers for diarization."},
                    "max_speakers": {"type": "integer", "format": "int32", "description": "Maximum number of speakers for diarization."},
                    "batch_size": {"type": "integer", "format": "int32", "description": "The transcription batch size."},
                    "script_target": {"type": "string", "description": "The target output script style or format."}
                }
            },
            "SoundEffectGenerationRequest": {
                "type": "object",
                "description": "The sound effect generation request payload.",
                "properties": {
                    "prompt": {"type": "string", "description": "The prompt describing the desired sound effect.", "example": "Thunderstorm with heavy rain and distant thunder"},
                    "negative_prompt": {"type": "string", "description": "The negative prompt describing sounds to avoid.", "example": "music, voices"},
                    "sourceUrl": {"type": "string", "description": "Source video or image URL for generating contextual sound effects. If provided, `sourceType` is required."},
                    "sourceType": {"type": "string", "description": "The source media type. Supported: `image`, `video`. Required when `sourceUrl` is provided.", "example": "video"},
                    "duration": {"type": "number", "format": "float", "description": "Requested output duration in seconds. Maximum is 30 seconds.", "example": 5.0},
                    "useAsync": {"type": "boolean", "description": "Set to `true` to process asynchronously.", "example": True}
                }
            },
            "SeparationRequest": {
                "type": "object",
                "description": "The audio separation request payload.",
                "properties": {
                    "sourceUrl": {"type": "string", "description": "The source audio URL.", "example": "https://example.com/song.mp3"},
                    "model": {"type": "string", "description": "The separation model. Supported: `vocal-remover`, `htdemucs_6s-4`, `reverb`.", "example": "vocal-remover"},
                    "useAsync": {"type": "boolean", "description": "Set to `true` to process asynchronously.", "example": True}
                }
            },
            "EnhanceAudioRequest": {
                "type": "object",
                "description": "The audio enhancement request payload.",
                "properties": {
                    "files": {"type": "array", "items": {"type": "string"}, "description": "List of source file URLs to enhance.", "example": ["https://example.com/recording.mp3"]},
                    "title": {"type": "string", "description": "The task title."},
                    "video": {"type": "boolean", "description": "Whether the input contains video."},
                    "stutters": {"type": "boolean", "description": "Whether to remove stutters."},
                    "fillers": {"type": "boolean", "description": "Whether to remove filler words."},
                    "hesitations": {"type": "boolean", "description": "Whether to remove hesitations."},
                    "muted": {"type": "boolean", "description": "Whether to remove muted sections."},
                    "breath": {"type": "boolean", "description": "Whether to reduce breathing sounds."},
                    "normalize": {"type": "boolean", "description": "Whether to normalize loudness."},
                    "autoeq": {"type": "boolean", "description": "Whether to apply automatic equalization."},
                    "transcription": {"type": "boolean", "description": "Whether to generate a transcription."},
                    "summarize": {"type": "boolean", "description": "Whether to generate a summary."},
                    "merge": {"type": "boolean", "description": "Whether to merge multiple files into one output."},
                    "totalDurationSecends": {"type": "integer", "format": "int32", "description": "Total source duration in seconds."},
                    "useAsync": {"type": "boolean", "description": "Set to `true` to process asynchronously.", "example": True},
                    "send_email": {"type": "boolean", "description": "Whether to send the result by email."},
                    "long_silences": {"type": "boolean", "description": "Whether to remove long silences."},
                    "mouth_sounds": {"type": "boolean", "description": "Whether to remove mouth sounds."},
                    "remove_noise": {"type": "boolean", "description": "Whether to remove background noise."},
                    "keep_music": {"type": "boolean", "description": "Whether to preserve background music."},
                    "sound_studio": {"type": "boolean", "description": "Whether to apply sound studio processing."},
                    "mute_lufs": {"type": "integer", "format": "int32", "description": "Loudness threshold for muting, in LUFS."},
                    "target_lufs": {"type": "integer", "format": "int32", "description": "Target output loudness, in LUFS."},
                    "export_format": {"type": "string", "description": "The exported file format.", "example": "mp3"},
                    "social_content": {"type": "boolean", "description": "Whether to generate social media content."},
                    "export_timestamps": {"type": "boolean", "description": "Whether to export timestamps."},
                    "signed_url": {"type": "string", "description": "The signed URL used by the upstream service."}
                }
            },
            "ReaderGenerationRequest": {
                "type": "object",
                "description": "The reader generation request payload.",
                "properties": {
                    "title": {"type": "string", "description": "The task title."},
                    "sourceUrl": {"type": "string", "description": "Source content URL (article, web page, document, etc.).", "example": "https://example.com/article"},
                    "sourceType": {"type": "string", "description": "The source content type.", "example": "article"},
                    "thumbnail": {"type": "string", "description": "The thumbnail image URL."},
                    "voice": {"type": "string", "description": "The narration voice model name.", "example": "james"},
                    "engine": {"type": "string", "description": "The reader generation engine."},
                    "useAsync": {"type": "boolean", "description": "Set to `true` to process asynchronously.", "example": True}
                }
            },
            "PodcastGenerationRequest": {
                "type": "object",
                "description": "The podcast generation request payload.",
                "properties": {
                    "text": {"type": "string", "description": "The podcast script content.", "example": "Welcome to the FineVoice podcast. Today we discuss AI audio..."},
                    "thumbnail": {"type": "string", "description": "The thumbnail image URL."},
                    "speakers": {"type": "array", "items": {"type": "string"}, "description": "Voice models used by podcast speakers.", "example": ["james", "madison"]},
                    "expectedDuration": {"type": "string", "description": "The expected generated duration.", "example": "5min"},
                    "prompt": {"type": "string", "description": "The generation prompt."},
                    "style": {"type": "string", "description": "The desired podcast style.", "example": "conversational"},
                    "originalText": {"type": "boolean", "description": "Whether to keep the original text wording."},
                    "useAsync": {"type": "boolean", "description": "Set to `true` to process asynchronously.", "example": True}
                }
            },
            "DubbingGenerationRequest": {
                "type": "object",
                "description": "The dubbing generation request payload.",
                "properties": {
                    "title": {"type": "string", "description": "The task title."},
                    "sourceUrl": {"type": "string", "description": "The source media URL.", "example": "https://example.com/video.mp4"},
                    "sourceType": {"type": "string", "description": "Source media type. Use `simple` for translation-only, or `audio`/`video` for full dubbing.", "example": "video"},
                    "thumbnail": {"type": "string", "description": "The thumbnail image URL."},
                    "sourceLanguageCode": {"type": "string", "description": "The source language code.", "example": "en"},
                    "targetLanguageCode": {"type": "string", "description": "The target language code.", "example": "zh"},
                    "speakers": {"type": "array", "items": {"type": "string"}, "description": "Target speaker voice models. When `sourceType` is `simple`, pass `[female]` or `[male]`. When `audio`/`video`, pass specific voice names like `[leo]`.", "example": ["leo"]},
                    "expectedDuration": {"type": "string", "description": "The expected generated duration."},
                    "duration": {"type": "number", "format": "double", "description": "Source duration in seconds."},
                    "useAsync": {"type": "boolean", "description": "Set to `true` to process asynchronously.", "example": True}
                }
            },
            "VoiceTrainRequest": {
                "type": "object",
                "description": "The voice training request payload.",
                "properties": {
                    "name": {"type": "string", "description": "The display name of the trained model.", "example": "My Custom Voice"},
                    "languageCode": {"type": "string", "description": "The language code of the training audio.", "example": "en-US"},
                    "gender": {"type": "string", "description": "The target voice gender.", "example": "female"},
                    "audioUrl": {"type": "string", "description": "The remote audio URL used for training.", "example": "https://example.com/training_audio.wav"},
                    "imageUrl": {"type": "string", "description": "The remote avatar image URL."}
                }
            },
            "VoiceDesignRequest": {
                "type": "object",
                "description": "The voice design request payload.",
                "properties": {
                    "taskId": {"type": "string", "description": "Task identifier for updating an existing design task."},
                    "engine": {"type": "string", "description": "Voice generation engine. Supported: `v1`, `v2`.", "example": "v2"},
                    "prompt": {"type": "string", "description": "Voice design prompt describing desired voice characteristics.", "example": "A warm, friendly female voice with a slight British accent"},
                    "previewText": {"type": "string", "description": "Preview text used to audition the designed voice.", "example": "Hello, this is a preview of the designed voice."},
                    "modelId": {"type": "string", "description": "The base model identifier."},
                    "seed": {"type": "integer", "format": "int64", "description": "Random seed for deterministic generation."}
                }
            },
            "MusicGenerationByPromptRequest": {
                "type": "object",
                "description": "The prompt-based music generation request payload.",
                "properties": {
                    "prompt": {"type": "string", "description": "The generation prompt describing the desired music.", "example": "Upbeat electronic dance music with heavy bass and synth leads"},
                    "instrumental": {"type": "boolean", "description": "Whether to generate instrumental-only music (no vocals).", "example": True},
                    "duration": {"type": "integer", "format": "int32", "description": "The target duration in seconds.", "example": 30},
                    "continuation": {"type": "boolean", "description": "Whether this generation continues a previous clip."},
                    "title": {"type": "string", "description": "The generated song title."},
                    "modelVersion": {"type": "string", "description": "The model version to use."},
                    "audioId": {"type": "string", "description": "Source audio identifier for continuation or reference."},
                    "prompt_type": {"type": "string", "description": "The prompt input type."},
                    "input_audio": {"type": "string", "description": "Optional input audio reference URL."},
                    "thumbnail_url": {"type": "string", "description": "The thumbnail image URL."}
                }
            },
            "MusicGenerationRequest": {
                "type": "object",
                "description": "The music generation request payload.",
                "properties": {
                    "title": {"type": "string", "description": "The generated song title.", "example": "My AI Song"},
                    "style": {"type": "string", "description": "The target music style.", "example": "pop, energetic, upbeat"},
                    "audioId": {"type": "string", "description": "The source audio identifier."},
                    "referVoice": {"type": "string", "description": "Reference vocal track identifier or URL."},
                    "referInstrumental": {"type": "string", "description": "Reference instrumental track identifier or URL."},
                    "lyrics": {"type": "string", "description": "The lyrics content.", "example": "[Verse 1]\nHello world, this is FineVoice..."},
                    "instrumental": {"type": "boolean", "description": "Whether to generate instrumental-only music.", "example": False},
                    "modelVersion": {"type": "string", "description": "Model version. `v3`: optimized for Chinese vocals and traditional styles. `r2`: studio recording quality with highly realistic vocals.", "example": "v3", "enum": ["v3", "r2"]}
                }
            },
            "MusicCoverRequest": {
                "type": "object",
                "description": "The music cover request payload.",
                "properties": {
                    "voice": {"type": "string", "description": "The primary target voice model name.", "example": "james"},
                    "pitch": {"type": "number", "format": "float", "minimum": -12, "maximum": 12, "description": "Vocal pitch offset in semitones.", "example": 0, "default": 0},
                    "outputFormat": {"type": "string", "description": "The desired output format.", "example": "mp3"},
                    "audioName": {"type": "string", "description": "The output audio name."},
                    "audioCover": {"type": "string", "description": "The cover image URL."},
                    "way": {"type": "string", "description": "Processing mode. Must be `m2`.", "example": "m2"},
                    "cut": {"type": "integer", "format": "int32", "description": "The cut mode."},
                    "engine": {"type": "string", "description": "Voice conversion engine. `v5`: great for singing (rich vibrato, more noise). `v7`: great for speech (clean, stable).", "example": "v5", "enum": ["v5", "v7"]},
                    "sourceUrl": {"type": "string", "description": "The source audio URL.", "example": "https://example.com/song.mp3"},
                    "singers": {"type": "array", "items": {"$ref": "#/components/schemas/MusicCoverSingerRequest"}, "description": "Singer configurations for a multi-singer cover."},
                    "instrument_pitch": {"type": "number", "format": "float", "description": "Instrumental pitch offset in semitones."},
                    "pitch_control": {"type": "string", "description": "Pitch control mode. Must be `rmvpe`.", "example": "rmvpe"},
                    "diffusion_steps": {"type": "integer", "format": "int32", "description": "Number of diffusion steps."},
                    "auto_f0_adjust": {"type": "boolean", "description": "Whether to enable automatic F0 adjustment."},
                    "vocal_types": {"type": "string", "description": "Vocal type configuration.", "example": "solo", "default": "solo", "enum": ["solo", "chorus", "duets"]}
                }
            },
            "MusicCoverSingerRequest": {
                "type": "object",
                "description": "A singer configuration for a multi-singer music cover task.",
                "properties": {
                    "voice": {"type": "string", "description": "The singer voice model name.", "example": "james"},
                    "pitch": {"type": "number", "format": "float", "description": "Pitch offset for this singer in semitones."},
                    "engine": {"type": "string", "description": "Voice conversion engine. `v5`: great for singing. `v7`: great for speech.", "example": "v5", "enum": ["v5", "v7"]},
                    "diffusion_steps": {"type": "integer", "format": "int32", "description": "Number of diffusion steps."},
                    "auto_f0_adjust": {"type": "boolean", "description": "Whether to enable automatic F0 adjustment."}
                }
            },
            "SpeechEnhancementRequest": {
                "type": "object",
                "description": "The speech enhancement request payload.",
                "properties": {
                    "url": {"type": "string", "description": "Audio file URL (http/https). Supports WAV/MP3/FLAC/AAC/OGG/OPUS/M4A/WEBM.", "example": "https://example.com/audio.mp3"},
                    "model": {"type": "string", "description": "Enhancement model. Supported: `MossFormer2_SE_48K`, `FRCRN_SE_16K`, `MossFormerGAN_SE_16K`.", "example": "MossFormer2_SE_48K", "default": "MossFormer2_SE_48K"},
                    "use_vad": {"type": "boolean", "description": "Enable VAD (Voice Activity Detection) preprocessing.", "default": False},
                    "enable_normalization": {"type": "boolean", "description": "Enable audio normalization after enhancement.", "default": False},
                    "normalization_method": {"type": "string", "description": "Normalization method: `peak`, `rms`, or `both`.", "default": "peak"},
                    "normalization_peak_db": {"type": "number", "description": "Target peak level in dBFS.", "default": -1.0},
                    "normalization_rms_db": {"type": "number", "description": "Target RMS level in dBFS.", "default": -20.0},
                    "output_format": {"type": "string", "description": "Output format: `wav`, `mp3`, `flac`, or `m4a`.", "default": "wav"}
                }
            },
            "SpeechSuperResolutionRequest": {
                "type": "object",
                "description": "The speech super resolution request payload.",
                "properties": {
                    "url": {"type": "string", "description": "Low sample-rate audio URL (http/https).", "example": "https://example.com/low_quality.mp3"},
                    "output_format": {"type": "string", "description": "Output format: `wav`, `mp3`, `flac`, or `m4a`.", "default": "wav"}
                }
            },
            "SpeechSeparationRequest": {
                "type": "object",
                "description": "The speech separation request payload.",
                "properties": {
                    "url": {"type": "string", "description": "Mixed-speech audio URL (http/https).", "example": "https://example.com/mixed_speakers.mp3"},
                    "speaker_index": {"type": "integer", "minimum": 0, "maximum": 1, "description": "Which speaker to return: `0` or `1`.", "default": 0},
                    "output_format": {"type": "string", "description": "Output format: `wav`, `mp3`, `flac`, or `m4a`.", "default": "wav"}
                }
            },
            "RemoveMouthSoundsRequest": {
                "type": "object",
                "description": "The remove mouth sounds request payload.",
                "properties": {
                    "url": {"type": "string", "description": "Audio URL (http/https).", "example": "https://example.com/audio.mp3"},
                    "use_rnnoise": {"type": "boolean", "description": "Enable RNNoise broadband denoising.", "default": False},
                    "rnnoise_strength": {"type": "integer", "minimum": 0, "maximum": 100, "description": "RNNoise strength (0–100).", "default": 80},
                    "use_hush": {"type": "boolean", "description": "Enable Hush background voice suppression.", "default": False},
                    "hush_atten_lim_db": {"type": "number", "description": "Hush attenuation limit in dB.", "default": 60.0},
                    "use_whisper_stutter": {"type": "boolean", "description": "Also remove stuttering using Whisper.", "default": False},
                    "whisper_model_size": {"type": "string", "description": "Whisper model size: `tiny`, `base`, `small`, or `medium`.", "default": "base"},
                    "output_format": {"type": "string", "description": "Output format: `wav`, `mp3`, `flac`, or `m4a`.", "default": "wav"}
                }
            },
            "RemoveLongSilencesRequest": {
                "type": "object",
                "description": "The remove long silences request payload.",
                "properties": {
                    "url": {"type": "string", "description": "Audio URL (http/https).", "example": "https://example.com/audio.mp3"},
                    "silence_threshold_db": {"type": "number", "description": "Silence detection threshold in dBFS.", "default": -42.0},
                    "long_silence_ms": {"type": "integer", "description": "Silences longer than this value (ms) are trimmed.", "default": 1200},
                    "keep_silence_ms": {"type": "integer", "description": "Silence padding to preserve at boundaries (ms).", "default": 180},
                    "output_format": {"type": "string", "description": "Output format: `wav`, `mp3`, `flac`, or `m4a`.", "default": "wav"}
                }
            },
            "FillerWordsRequest": {
                "type": "object",
                "description": "The filler words detect/remove request payload.",
                "properties": {
                    "url": {"type": "string", "description": "Audio URL (http/https).", "example": "https://example.com/audio.mp3"},
                    "output_format": {"type": "string", "description": "Output format: `wav`, `mp3`, `flac`, or `m4a`.", "default": "wav"},
                    "use_whisper": {"type": "boolean", "description": "Use Whisper ASR for accurate, language-aware filler word detection.", "default": False},
                    "whisper_model_size": {"type": "string", "description": "Whisper model size: `tiny`, `base`, `small`, or `medium`. Used when `use_whisper` is `true`.", "default": "base"},
                    "language": {"type": "string", "description": "Language code for Whisper (e.g. `en`, `zh`, `ja`, `fr`). Used when `use_whisper` is `true`.", "default": "en"},
                    "filler_words_list": {"type": "string", "description": "Comma-separated filler words to detect/remove. Empty = built-in defaults.", "default": "um,uh,er,hmm,hm,ah,eh,mhm"}
                }
            },
            "StutteringRemoveRequest": {
                "type": "object",
                "description": "The stuttering removal request payload.",
                "properties": {
                    "url": {"type": "string", "description": "Audio URL (http/https).", "example": "https://example.com/audio.mp3"},
                    "whisper_model_size": {"type": "string", "description": "Whisper model size for stutter detection: `tiny`, `base`, `small`, or `medium`.", "default": "base"},
                    "min_similarity": {"type": "number", "minimum": 0.5, "maximum": 1.0, "description": "Minimum similarity threshold for stutter detection.", "default": 0.75},
                    "max_gap_ms": {"type": "number", "minimum": 0.0, "description": "Maximum gap between stutter repetitions in ms.", "default": 500.0},
                    "output_format": {"type": "string", "description": "Output format: `wav`, `mp3`, `flac`, or `m4a`.", "default": "wav"}
                }
            },
            "AudioNormalizationRequest": {
                "type": "object",
                "description": "The audio normalization request payload.",
                "properties": {
                    "url": {"type": "string", "description": "Audio URL (http/https).", "example": "https://example.com/audio.mp3"},
                    "method": {"type": "string", "description": "Normalization method: `peak` (prevents clipping), `rms` (uniform volume), or `both` (RMS first, then peak).", "default": "peak"},
                    "peak_db": {"type": "number", "description": "Target peak level in dBFS.", "default": -1.0},
                    "rms_db": {"type": "number", "description": "Target RMS level in dBFS.", "default": -20.0},
                    "output_format": {"type": "string", "description": "Output format: `wav`, `mp3`, `flac`, or `m4a`.", "default": "wav"}
                }
            },
            "PipelineRequest": {
                "type": "object",
                "description": "The all-in-one audio processing pipeline request payload.",
                "properties": {
                    "url": {"type": "string", "description": "Audio file URL (http/https).", "example": "https://example.com/audio.mp3"},
                    "step_speech_enhancement": {"type": "boolean", "description": "Enable Speech Enhancement step (noise reduction).", "default": True},
                    "step_remove_mouth_sounds": {"type": "boolean", "description": "Enable Remove Mouth Sounds step.", "default": False},
                    "step_remove_long_silences": {"type": "boolean", "description": "Enable Remove Long Silences step.", "default": False},
                    "step_super_resolution": {"type": "boolean", "description": "Enable Super Resolution step (8 kHz to 48 kHz).", "default": False},
                    "step_filler_words_remove": {"type": "boolean", "description": "Enable Filler Words Removal step.", "default": False},
                    "step_stuttering_remove": {"type": "boolean", "description": "Enable Stuttering Removal step.", "default": False},
                    "step_audio_normalization": {"type": "boolean", "description": "Enable Audio Normalization step.", "default": False},
                    "enhancement_model": {"type": "string", "description": "Speech enhancement model: `MossFormer2_SE_48K`, `FRCRN_SE_16K`, or `MossFormerGAN_SE_16K`.", "default": "FRCRN_SE_16K"},
                    "enhancement_use_vad": {"type": "boolean", "description": "Enable VAD preprocessing for speech enhancement.", "default": False},
                    "silence_threshold_db": {"type": "number", "description": "Silence detection threshold in dBFS.", "default": -42.0},
                    "long_silence_ms": {"type": "integer", "description": "Silences longer than this value (ms) are trimmed.", "default": 1200},
                    "keep_silence_ms": {"type": "integer", "description": "Silence padding to preserve at boundaries (ms).", "default": 180},
                    "filler_use_whisper": {"type": "boolean", "description": "Use Whisper for filler word detection.", "default": False},
                    "filler_language": {"type": "string", "description": "Language code for filler word detection (e.g. `en`, `zh`).", "default": "en"},
                    "filler_words_list": {"type": "string", "description": "Comma-separated filler words to remove. Empty = built-in defaults.", "default": "um,uh,er,hmm,hm,ah,eh,mhm"},
                    "stutter_min_similarity": {"type": "number", "minimum": 0.5, "maximum": 1.0, "description": "Minimum similarity for stutter detection.", "default": 0.75},
                    "norm_method": {"type": "string", "description": "Normalization method: `peak`, `rms`, or `both`.", "default": "peak"},
                    "norm_peak_db": {"type": "number", "description": "Target peak level in dBFS.", "default": -1.0},
                    "norm_rms_db": {"type": "number", "description": "Target RMS level in dBFS.", "default": -20.0},
                    "output_format": {"type": "string", "description": "Output format: `wav`, `mp3`, `flac`, or `m4a`.", "default": "wav"}
                }
            }
        }
    }
}

out_path = r"d:/FineVoice-API/finevoice-api-docs/api-reference/openapi.json"
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(openapi, f, indent=2, ensure_ascii=False)

path_count = len(openapi["paths"])
schema_count = len(openapi["components"]["schemas"])
print(f"Written: {path_count} paths, {schema_count} schemas")
