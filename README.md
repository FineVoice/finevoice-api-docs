# FineVoice Kit

**FineVoice Kit** is a developer-friendly toolkit built on top of the **FineVoice API**, designed to help developers easily integrate AI voice capabilities into their applications.

With FineVoice Kit, you can generate natural-sounding speech, clone custom voices, transform voices, and convert speech to text using a simple and scalable REST API.

🌐 API Base URL: https://api.finevoice.ai/

## 🚀 Features

- 🎙️ High-quality AI Text-to-Speech (TTS)
- 🧬 Custom voice cloning
- 🎭 Voice transformation and effects
- 📝 Speech-to-Text (STT)
- 🌍 Support for multiple languages and voices
- 🔗 Simple RESTful API, compatible with any programming language

## 📦 Installation

Clone the repository:

```
git clone https://github.com/FineVoice/docs.git
cd finevoice-kit
```

Install dependencies:

```
npm install        # Node.js
# or
pip install -r requirements.txt   # Python
```

---

## 🔑 Authentication

To use the FineVoice API, you need an **API Key**.

Create your API key from the FineVoice dashboard and store it securely as an environment variable:

```
export FINEVOICE_API_KEY=your_api_key_here
```

Quick Get your API Key: https://api.finevoice.ai/quickstart

## ⚡ Quick Start

**Your First TTS Request**: https://api.finevoice.ai/quickstart

## 📚 API Overview

| Feature                     | Endpoint             | Description                           |
| :-------------------------- | :------------------- | :------------------------------------ |
| Text-to-Speech              | `/v1/text_to_speech` | Convert text into AI-generated speech |
| Voice Cloning               | `/v1/voice_clone`    | Create a custom voice model           |
| Voice Changer (Coming Soon) | `/v1/voice_changer`  | Apply voice styles or effects         |
| Sound Effects (Coming Soon) | `/v1/sound_effect`   | Generate or apply sound effects       |

## ⚙️ Configuration

We recommend using a `.env` file to manage sensitive configuration:

```
FINEVOICE_API_KEY=your_api_key_here
```

## 🛡️ Best Practices

- Never expose your API key in client-side code
- Handle API errors and rate limits properly
- Follow FineVoice’s usage policies for voice cloning and commercial use

## 📖 Documentation

Full API documentation is available at:\
👉 https://api.finevoice.ai/

## 💬 Support

If you have questions or need assistance:

- 📧 Email: [support@finevoice.ai](mailto:support@finevoice.ai)
- 🌐 Website: https://finevoice.ai/
