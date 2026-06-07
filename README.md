# Interactive Storyline Agent

Transform any written work into a voice-driven interactive role-playing experience.

## Overview

The Interactive Storyline Agent is an AI-powered platform that converts novels, scripts, or narratives into interactive fiction games where users become the protagonist and make real-time decisions that branch the storyline. The system preserves the original author's writing style and world logic through Agentic RAG (Vector DB lore store) and fine-tuned local SLMs.

## Features

- **Novel Ingestion**: Process PDF, EPUB, and TXT files into searchable lore chunks
- **Entity Extraction**: Automatically identify characters, locations, and factions using AI
- **Branching Narrative**: Story evolves as a directed acyclic graph (DAG) based on user choices
- **Voice Input**: Speak your decisions using local Whisper transcription
- **AI Story Generation**: 
  - Primary: Anthropic Claude API (with prompt caching for cost efficiency)
  - Fallback: OpenAI GPT-4 ? Local Ollama (fine-tuned Llama-3)
- **Style Adaptation**: Train custom style adapters (QLoRA) to match any author's voice
- **Canon Violation Detection**: Automatic checking against source material to prevent lore breaks
- **Encrypted Save System**: AES-256-GCM protected game states
- **Cross-Platform Desktop App**: Built with Electron for Windows/macOS/Linux
- **Self-Improving Knowledge Base**: Automated weekly updates from ArXiv, HuggingFace, and ACM

## Architecture

The system consists of a frontend (React + Electron) and a backend (FastAPI) communicating via REST APIs.

- **Frontend**: Handles user interface, novel upload, voice input, story display, and choice selection.
- **Backend**: Processes novels, extracts entities, manages the narrative DAG, generates scenes using LLMs, and handles voice transcription and saving/loading.
- **AI Components**: 
  - ChromaDB stores novel embeddings for retrieval-augmented generation.
  - LLMs (Claude, OpenAI, Ollama) generate story continuations.
  - Whisper transcribes voice input.
  - Sentence Transformers create embeddings for lore retrieval.
- **Data Storage**: 
  - SQLite stores the narrative DAG and encrypted game saves.
  - ChromaDB stores lore embeddings for quick retrieval.
- **Workflow**: 
  1. User uploads a novel.
  2. Backend extracts text, chunks it, and stores embeddings in ChromaDB.
  3. Entity extraction identifies characters, locations, and factions (stored in SQLite and ChromaDB).
  4. The narrative engine initializes a DAG with the opening scene.
  5. For each user action (via text or voice), the backend retrieves relevant lore, generates the next scene using the LLM fallback chain, and updates the DAG.
  6. The frontend displays the scene and choices, and the cycle repeats.

## Technology Stack

### Backend
- **Language**: Python 3.11
- **Framework**: FastAPI
- **ML/Ops**: 
  - Llama-3-8B (Ollama) with QLoRA fine-tuning
  - Anthropic Claude API (primary)
  - OpenAI GPT-4 API (fallback)
  - Whisper (small/medium) for speech-to-text
  - Sentence Transformers (all-MiniLM-L6-v2) for embeddings
  - ChromaDB for vector storage
  - SQLite for narrative state management
  - NetworkX for DAG operations
  - Cryptography (AES-256-GCM) for save encryption
  - PEFT & bitsandbytes for efficient fine-tuning

### Frontend
- **Framework**: React 18.3.1
- **Styling**: TailwindCSS 3.4.4
- **Desktop**: Electron 31.0.0
- **State Management**: Zustand (planned) / React Context (current)
- **HTTP Client**: Axios
- **Voice**: Web Audio API + MediaRecorder

## Installation

### Prerequisites
- Python 3.11+
- Node.js 18+ (for frontend)
- Git
- Ollama (for local LLM fallback)
- API keys for:
  - Anthropic Claude (ANTHROPIC_API_KEY)
  - OpenAI (OPENAI_API_KEY)
  - Optional: ElevenLabs (ELEVENLABS_API_KEY), Stability AI (STABILITY_API_KEY)

### Setup

1. **Clone the repository**
   `ash
   git clone https://github.com/dungnotnull/interactive-storyline-agent.git
   cd interactive-storyline-agent
   `

2. **Install backend dependencies**
   `ash
   pip install -r backend/requirements.txt
   `

3. **Install frontend dependencies**
   `ash
   cd frontend
   npm install
   cd ..
   `

4. **Configure environment**
   `ash
   cp .env.example .env
   # Edit .env to add your API keys and set a 32-byte SAVE_KEY
   `

5. **Pull required models** (if using local fallback)
   `ash
   ollama pull llama3
   # Whisper model is loaded automatically by the backend
   `

6. **Start the application**
   `ash
   # Start backend
   uvicorn backend.app.main:app --reload
   
   # In a new terminal, start frontend
   cd frontend
   npm start    # For web browser
   # OR
   npm run electron  # For desktop app
   `

## Usage

1. Launch the application (backend must be running first)
2. Upload a novel (PDF, EPUB, or TXT format)
3. Wait for processing (extracts text, chunks, and builds lore index)
4. Begin your interactive journey:
   - Read the generated scene
   - Choose from presented options or speak your own action
   - Watch the story evolve in the author's style
5. Use voice button for hands-free interaction
6. Save/load your progress at any time
7. Train custom style adapters in Settings ? Style Training

## API Endpoints

### Novel Processing
- POST /novel/upload - Upload and process a novel file
- POST /entity/extract - Extract characters, locations, factions

### Story Generation
- POST /scene/generate - Generate next scene based on user action
- POST /voice/transcribe - Transcribe voice input to text

### Style Management
- GET /style/adapters - List available style adapters
- POST /style/train - Upload text to train a new style adapter

### Consistency Checking
- POST /canon/check - Check generated text for lore violations

### Save System
- POST /save/game - Encrypt and save current game state
- POST /load/game - Load and decrypt a saved game state

### Health
- GET /health - Service health check

## Development

### Code Structure
- ackend/: Contains the FastAPI application.
  - pp/main.py: Main application with all API endpoints.
  - equirements.txt: Python dependencies.
- rontend/: Contains the React + Electron frontend.
  - public/index.html: HTML template.
  - src/App.js: Main React component.
  - src/index.js: Entry point.
  - package.json: Node.js dependencies and scripts.
- electron/: Electron main and preload scripts for desktop packaging.
- scripts/: Utility scripts.
  - update_knowledge_brain.py: Weekly knowledge base updater.
- Configuration files:
  - .env.example: Template for environment variables.
  - .gitignore: Git ignore rules.
- Documentation:
  - README.md: This file.
  - PROJECT-DEVELOPMENT-PHASE-TRACKING.md: Development roadmap.
  - CLAUDE.md: Project identity and guidelines.
  - PROJECT-detail.md: Full technical specification.
  - SECOND-KNOWLEDGE-BRAIN.md: Knowledge base.

### Contributing
We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Ensure tests pass
5. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Anthropic for Claude API access
- Hugging Face for open-source models and libraries
- The Electron and React communities
- Open-source contributors to Whisper, ChromaDB, Ollama, and PEFT

## Contact

For questions or support, please open an issue on GitHub or contact the maintainers.

**Created with ?? by [dungnotnull](https://github.com/dungnotnull) and Claude**

