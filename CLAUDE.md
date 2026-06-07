# CLAUDE.md — interactive-storyline-agent

## Project Identity
- **Name:** interactive-storyline-agent
- **Tagline:** Transform any written work into a voice-driven interactive role-playing experience
- **Status:** Phase 0 — Research & Environment Setup
- **Phase:** Pre-MVP

---

## Core Problem Being Solved
Traditional reading is passive — readers consume stories without agency. This agent converts any novel, script, or narrative into an interactive fiction game where the user embodies the protagonist and makes real decisions that branch the storyline. The AI preserves the original author's writing style and world logic by combining Agentic RAG (Vector DB lore store) with a fine-tuned local SLM trained on the author's stylistic fingerprint, enabling immersive, coherent branching narratives without breaking canonical lore.

---

## Architecture Summary
- **Platform:** Desktop application (Python/FastAPI backend + React/Electron frontend)
- **ML Stack:** Agentic RAG pipeline, style-transfer fine-tuning (Llama-3-8B via Ollama), voice recognition (Whisper), image generation (Stable Diffusion XL optional)
- **Local SLM:** Llama-3-8B via Ollama (fine-tuned per author style)
- **External LLM APIs:** Claude API (story branch generation, NPC dialogue), OpenAI GPT-4 (fallback), Whisper API (voice-to-text)
- **Vector DB:** ChromaDB (local, persistent) for lore/world-building storage

---

## Key Technical Decisions
1. Agentic RAG architecture: all lore (characters, world rules, timeline) stored in ChromaDB; every generation call retrieves top-k relevant lore chunks to prevent canon violations
2. Author style fine-tuning: fine-tune Llama-3-8B on curated text samples from the target author using QLoRA (4-bit) to create lightweight, swappable style adapters
3. Voice input pipeline: Whisper (local small/medium model) for offline transcription; fallback to Whisper API for accuracy
4. Branching narrative engine: story tree stored as directed acyclic graph (DAG) in SQLite; each node stores scene text, choices offered, and chosen path
5. Pluggable LLM backend: Claude API → GPT-4 → local Ollama with graceful fallback chain
6. Privacy-first: all novel content, user decisions, and personal data stored locally (SQLite + AES-256 for saved games)

---

## External LLM API Integrations

| Provider | Purpose | Config Key |
|----------|---------|-----------|
| Anthropic Claude | Primary story branch generation, NPC dialogue, style coherence checking | `ANTHROPIC_API_KEY` |
| OpenAI GPT-4 | Fallback story generation, summarization | `OPENAI_API_KEY` |
| OpenAI Whisper API | High-accuracy voice transcription fallback | `OPENAI_API_KEY` |
| Stability AI | Optional scene illustration generation | `STABILITY_API_KEY` |

---

## HuggingFace Models In Use

| Model ID | Purpose | Link |
|----------|---------|------|
| `meta-llama/Meta-Llama-3-8B-Instruct` | Base for author-style fine-tuning via QLoRA | https://huggingface.co/meta-llama/Meta-Llama-3-8B-Instruct |
| `openai/whisper-small` | Local voice-to-text transcription | https://huggingface.co/openai/whisper-small |
| `openai/whisper-medium` | Higher-accuracy local transcription | https://huggingface.co/openai/whisper-medium |
| `sentence-transformers/all-MiniLM-L6-v2` | Text embeddings for ChromaDB RAG | https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2 |
| `stabilityai/stable-diffusion-xl-base-1.0` | Optional scene image generation | https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0 |

---

## Current Active Development Tasks
- [ ] Set up development environment (Python 3.11, Ollama, ChromaDB)
- [ ] Build novel ingestion pipeline (PDF/EPUB/TXT → chunked text)
- [ ] Implement ChromaDB lore store with character/world extraction
- [ ] Integrate Whisper for voice input
- [ ] Build RAG-augmented story branch generator (Claude API)
- [ ] Implement DAG-based narrative state machine (SQLite)
- [ ] Build style-transfer fine-tuning pipeline (QLoRA on Llama-3-8B)
- [ ] Create React/Electron frontend (story display + choice UI + voice button)
- [ ] Add optional scene image generation (Stable Diffusion XL)

---

## Related Files
- `PROJECT-detail.md` — Full technical specification and architecture
- `PROJECT-DEVELOPMENT-PHASE-TRACKING.md` — Phase-by-phase development roadmap
- `SECOND-KNOWLEDGE-BRAIN.md` — Research papers, models, self-improving knowledge base
