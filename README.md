
# Interactive Storyline Agent

**Transform any written work into a voice-driven interactive role-playing experience.**

## Overview

The Interactive Storyline Agent is an AI-powered platform that converts novels, scripts, or any narrative into interactive fiction games. Users become the protagonist and make real-time decisions that branch the storyline. The system preserves the original author's writing style and world logic through **Agentic RAG** (Vector DB lore store) and fine-tuned local SLMs.

## ✨ Features

- **Novel Ingestion**: Process PDF, EPUB, and TXT files into searchable lore chunks
- **Entity Extraction**: Automatically identify characters, locations, and factions using AI
- **Branching Narrative**: Story evolves as a Directed Acyclic Graph (DAG) based on user choices
- **Voice Input**: Speak your decisions using local Whisper transcription
- **AI Story Generation**:
  - Primary: Anthropic Claude API (with prompt caching for cost efficiency)
  - Fallback: OpenAI GPT-4 or Local Ollama (fine-tuned Llama-3)
- **Style Adaptation**: Train custom style adapters (QLoRA) to match any author's voice
- **Canon Violation Detection**: Automatic checking against source material to prevent lore breaks
- **Encrypted Save System**: AES-256-GCM protected game states
- **Cross-Platform Desktop App**: Built with Electron for Windows, macOS, and Linux
- **Self-Improving Knowledge Base**: Automated weekly updates from ArXiv, HuggingFace, and ACM

## 🏗️ Architecture

The system consists of a **Frontend** (React + Electron) and a **Backend** (FastAPI) communicating via REST APIs.

### Frontend
Handles user interface, novel upload, voice input, story display, and choice selection.

### Backend
Processes novels, extracts entities, manages the narrative DAG, generates scenes using LLMs, handles voice transcription, and save/load functionality.

### Key Components
- ChromaDB + Sentence Transformers for RAG
- LLMs: Claude (primary), GPT-4, Ollama Llama-3
- Whisper for speech-to-text
- NetworkX for DAG operations
- SQLite for narrative state
- Cryptography (AES-256-GCM) for save encryption

## 🛠️ Technology Stack

### Backend
- **Language**: Python 3.11
- **Framework**: FastAPI
- **ML / LLM**:
  - Llama-3-8B (Ollama) with QLoRA fine-tuning
  - Anthropic Claude API
  - OpenAI GPT-4 API
  - Whisper (small/medium)
  - Sentence Transformers (`all-MiniLM-L6-v2`)
  - ChromaDB, SQLite, NetworkX
  - PEFT + bitsandbytes

### Frontend
- **Framework**: React 18.3.1
- **Styling**: TailwindCSS 3.4.4
- **Desktop**: Electron 31.0.0
- **State Management**: Zustand (planned) / React Context (current)
- **HTTP Client**: Axios
- **Voice**: Web Audio API + MediaRecorder

## 📥 Installation

### Prerequisites
- Python 3.11+
- Node.js 18+
- Git
- Ollama (for local LLM fallback)
- API keys for Anthropic and OpenAI

### Setup

```bash
# 1. Clone the repository
git clone https://github.com/dungnotnull/interactive-storyline-agent.git
cd interactive-storyline-agent

# 2. Install backend dependencies
pip install -r backend/requirements.txt

# 3. Install frontend dependencies
cd frontend
npm install
cd ..

# 4. Configure environment variables
cp .env.example .env
# Edit .env to add your API keys and SAVE_KEY
```

```bash
# 5. Pull local models (optional)
ollama pull llama3
```

```bash
# 6. Run the application

# Terminal 1 - Backend
uvicorn backend.app.main:app --reload

# Terminal 2 - Frontend
cd frontend
npm start           # For web browser
# npm run electron  # For desktop app
```

## 🎮 Usage

1. Launch the application (backend must be running first)
2. Upload a novel (PDF, EPUB, or TXT)
3. Wait for processing (text extraction + embedding)
4. Begin your interactive journey:
   - Read the generated scene
   - Choose from options or speak your own action
5. Use the voice button for hands-free play
6. Save/load progress anytime

## 📁 Project Structure

```
interactive-storyline-agent/
├── backend/                    # FastAPI application
├── frontend/                   # React + Electron
├── electron/                   # Desktop packaging
├── scripts/                    # Utility scripts
├── .env.example
├── README.md
├── PROJECT-DEVELOPMENT-PHASE-TRACKING.md
├── CLAUDE.md
└── PROJECT-detail.md
```

## 👥 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**Created with ❤️ by [dungnotnull](https://github.com/dungnotnull) and Claude**
```
