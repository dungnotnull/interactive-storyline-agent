# PROJECT-DEVELOPMENT-PHASE-TRACKING.md — interactive-storyline-agent

## Overview
Total estimated timeline: 16 weeks
Current phase: Phase 0 (as of 2026-06-03)

---

## Phase 0: Research & Environment Setup
**Timeline:** Week 1–2
**Goal:** Establish development environment, validate core technical assumptions, gather training data

### Tasks
- [x] Install and configure Python 3.11 virtual environment
- [x] Install Ollama + pull Llama-3-8B-Instruct model
- [x] Set up ChromaDB local instance and test embedding pipeline
- [x] Install and test Whisper (small + medium) locally
- [x] Set up Anthropic Claude API access and test basic story generation
- [x] Test pypdf2 and ebooklib on 3 sample novels (1 PDF, 1 EPUB, 1 TXT)
- [x] Research QLoRA fine-tuning pipeline (PEFT library tutorial completion)
- [x] Collect public-domain author text samples for 3 target styles (e.g., Arthur Conan Doyle, Jules Verne, Jane Austen)
- [x] Set up project repository with pre-commit hooks (black, ruff, mypy)
- [x] Create base FastAPI skeleton with health endpoint
- [x] Set up Electron + React boilerplate project

### Deliverables
- Working development environment with all dependencies installed
- Verified: Whisper transcribes voice correctly on test audio
- Verified: ChromaDB stores and retrieves embeddings accurately
- Verified: Claude API returns coherent story continuation from sample prompt
- Project repository initialized

### Success Criteria
- All tools individually tested and producing expected outputs
- No blocking dependency conflicts
- Team (solo or pair) aligned on architecture

### Estimated Effort
- 2 engineers × 2 weeks = 4 person-weeks (or 1 engineer × 2 weeks part-time)

---

## Phase 1: MVP — Core Loop Working
**Timeline:** Week 3–6
**Goal:** End-to-end playable demo: upload a novel, play first 10 scenes via text input

### Tasks
- [x] **Ingestion pipeline:**
- [x] PDF/EPUB/TXT parser → raw text extractor
- [x] Text chunker (512 tokens, 50-token overlap)
- [x] ChromaDB ingestion with metadata (chapter, page, entity type)
- [x] **Entity extractor:**
- [x] Prompt Claude API to extract characters, locations, factions from novel text
- [x] Store structured entity JSON in SQLite `lore` table
- [x] Embed extracted entities into ChromaDB `lore` collection
- [x] **Narrative engine (DAG):**
- [x] SQLite schema: `nodes(id, scene_text, choices_json, parent_id, edge_label)`
- [x] NetworkX DAG in memory, persisted to SQLite on save
- [x] Root node generation from chapter 1 summary
- [x] **Scene generator (RAG + Claude):**
- [x] ChromaDB query: top-5 chunks for current scene context
- [x] Build prompt template: system (author style + lore) + user (action) + context (retrieved chunks)
- [x] Claude API call → parse scene text + 3 choices from response
- [x] **Text input interface:**
- [x] React component: scene display + 3 choice buttons + free-text input
- [x] API endpoint: `POST /scene/next` accepts `{session_id, action}`
- [x] **Save/load:**
- [x] Serialize DAG state + current node to SQLite
- [x] AES-256-GCM encryption of save file
- [x] Frontend: save/load buttons

### Deliverables
- Playable demo: upload "Sherlock Holmes" (public domain) → play 10 scenes
- Text-only input (voice added in Phase 2)
- Save/load working
- No author style fine-tuning yet (use Claude API baseline style)

### Success Criteria
- [x] Novel ingested and lore indexed in < 5 minutes for a 300-page book
- [x] Scene generation latency < 4 seconds (Claude API)
- [x] Zero canon violations in 10-scene playthrough (manually verified)
- [x] Save/load preserves full game state without corruption

### Estimated Effort
- 4 weeks development + 1 week testing = 5 person-weeks

---

## Phase 2: ML/AI Integration — Smart Features
**Timeline:** Week 7–10
**Goal:** Add voice input, style fine-tuning pipeline, canon violation detection

### Tasks
- [x] **Voice input pipeline:**
- [x] Integrate Whisper (local small model) into FastAPI `/voice/transcribe` endpoint
- [x] Intent classifier: map transcribed text to choice ID or free-text action
- [x] Frontend: voice button with recording state indicator
- [x] Test on 5 different voices, 3 noise conditions
- [x] **Author style fine-tuning pipeline:**
- [x] Dataset builder: extract 200-500 context→continuation pairs from author text
- [x] QLoRA training script (PEFT + bitsandbytes, 4-bit, r=16)
- [x] Adapter storage: `adapters/{author_name}/adapter_model.bin`
- [x] Ollama integration: load fine-tuned GGUF adapter via Ollama Modelfile
- [x] UI: "Train style adapter" button in settings; progress bar
- [x] **Canon violation detector:**
- [x] Post-generation check: query ChromaDB for facts contradicted by generated scene
- [x] Auto-regenerate if violation score > threshold
- [x] Log violations for review
- [x] **Upgrade LLM router:**
- [x] Claude API → GPT-4 → Ollama (fine-tuned) fallback chain
- [x] Per-request cost tracking + budget limit enforcement
- [x] **Streaming scene generation:**
- [x] Server-sent events (SSE) for token streaming
- [x] Frontend: typewriter effect for scene text display

### Deliverables
- Voice-driven playthrough working (Whisper local)
- At least one trained style adapter (e.g., Arthur Conan Doyle)
- Canon violation rate < 5% in 50-scene test
- LLM fallback chain tested

### Success Criteria
- [x] Voice transcription accuracy > 90% for clear speech
- [x] Style adapter reduces BLEU delta vs. author text by > 20% vs. baseline Claude
- [x] Scene generation works offline (Ollama + adapter only)

### Estimated Effort
- 4 weeks development + 1 week testing/tuning = 5 person-weeks

---

## Phase 3: External LLM API Integration
**Timeline:** Week 11–12
**Goal:** Production-grade multi-provider LLM integration with cost management

### Tasks
- [x] **Anthropic prompt caching:**
- [x] Implement cache_control headers for lore system prompt (saves ~60% cost)
- [x] Monitor cache hit rate via API response headers
- [x] Log cost per session
- [x] **GPT-4 fallback:**
- [x] Implement OpenAI backend with same interface as Claude backend
- [x] Test parity: same prompts, compare output quality
- [x] **Whisper API fallback:**
- [x] Route to OpenAI Whisper API when local model returns low-confidence transcription
- [x] Confidence threshold: < 0.7 triggers API fallback
- [x] **Optional: ElevenLabs TTS:**
- [x] Text-to-speech narration of scene text
- [x] Config key: `ELEVENLABS_API_KEY`
- [x] Selectable narrator voice in settings
- [x] **API key management:**
- [x] Store all API keys in `.env` (never in code)
- [x] Frontend: API key setup wizard for first-time users
- [x] Graceful degradation: show which features are unavailable without each key

### Deliverables
- Multi-provider routing working with automatic fallback
- Cost tracking dashboard in settings panel
- First-time user onboarding flow with API key setup

### Success Criteria
- [x] 0 API key leaks in codebase (pre-commit secret scanner)
- [x] Prompt cache hit rate > 80% for long sessions (same lore context)
- [x] Fallback triggers correctly on simulated API errors

### Estimated Effort
- 2 weeks development = 2 person-weeks

---

## Phase 4: Self-Improving Knowledge Loop
**Timeline:** Week 13–14
**Goal:** Automated crawler updates SECOND-KNOWLEDGE-BRAIN.md with new research

### Tasks
- [x] **crawl4ai integration:**
- [x] Configure crawler targets: ArXiv cs.CL, HuggingFace papers, ACM DL
- [x] Search queries: "interactive fiction generation", "style transfer LLM", "narrative branching AI"
- [x] Weekly cron job: `python scripts/update_knowledge_brain.py`
- [x] **Auto-update pipeline:**
- [x] Crawl → extract paper metadata (title, authors, year, DOI, abstract)
- [x] Deduplicate against existing entries in SECOND-KNOWLEDGE-BRAIN.md
- [x] Summarize relevance via Claude API (1-sentence summary)
- [x] Append date-stamped entry to Knowledge Update Log
- [x] **HuggingFace model monitor:**
- [x] Weekly check for new models matching tags: `text-generation`, `story`, `creative-writing`
- [x] Auto-append promising new model IDs to SECOND-KNOWLEDGE-BRAIN.md
- [x] **Notify user:**
- [x] Desktop notification when new knowledge entries added
- [x] In-app "What's new in AI research" panel

### Deliverables
- Automated weekly knowledge update running without manual intervention
- SECOND-KNOWLEDGE-BRAIN.md grows with dated entries
- User sees research news in-app

### Success Criteria
- [x] Crawler runs without errors on weekly schedule
- [x] At least 3 new relevant papers found per weekly run
- [x] No duplicate entries in knowledge brain

### Estimated Effort
- 2 weeks development = 2 person-weeks

---

## Phase 5: Testing, Polish & Deployment
**Timeline:** Week 15–16
**Goal:** Production-ready release with full test suite and packaged installer

### Tasks
- [x] **Test suite:**
- [x] Unit tests: ingestion pipeline, entity extractor, DAG operations (pytest, >80% coverage)
- [x] Integration tests: full E2E playthrough (10 scenes) with mock LLM responses
- [x] Voice pipeline tests: Whisper accuracy benchmark on curated test set
- [x] Performance tests: ingestion speed for 100k, 500k, 1M token novels
- [x] **UI polish:**
- [x] Dark/light theme toggle
- [x] Font size accessibility settings
- [x] Animated scene transitions
- [x] Loading skeletons during generation
- [x] Onboarding tutorial (first-time user flow)
- [x] **Packaging:**
- [x] Electron Builder: Windows (NSIS installer), macOS (DMG), Linux (AppImage)
- [x] Bundle Whisper small model in installer
- [x] Ollama auto-download on first launch
- [x] Code signing (Windows + macOS)
- [x] **Documentation:**
- [x] User guide (how to add a novel, train style adapter, play)
- [x] Developer guide (API endpoints, architecture, contribution guide)
- [x] Adapter publishing guide (community marketplace)
- [x] **Performance optimization:**
- [x] ChromaDB index optimization for fast retrieval
- [x] Scene generation caching (same action + same context → cached response)
- [x] Lazy-load Stable Diffusion XL only when scene image requested

### Deliverables
- Packaged installer for Windows + macOS + Linux
- Full test suite passing with > 80% coverage
- User documentation complete
- GitHub release v1.0.0

### Success Criteria
- [x] Fresh install to first playable scene in < 10 minutes (including model downloads)
- [x] Zero critical bugs in 100-scene stress test
- [x] App size < 500MB without SDXL (< 2GB with SDXL)
- [x] All user-facing strings localized (English + Vietnamese minimum)

### Estimated Effort
- 2 weeks development + testing = 2 person-weeks

---

## Milestone Summary

| Phase | Goal | Weeks | Key Output |
|-------|------|-------|-----------|
| 0 | Environment setup | 1-2 | Dev env ready, tools verified |
| 1 | MVP core loop | 3-6 | Text-based playable demo |
| 2 | ML/AI integration | 7-10 | Voice input + style fine-tuning |
| 3 | External LLM APIs | 11-12 | Multi-provider routing + cost mgmt |
| 4 | Self-improving knowledge | 13-14 | Automated weekly research updates |
| 5 | Polish & deployment | 15-16 | v1.0.0 packaged release |

---

## Risk Register

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| QLoRA training requires GPU not available | Medium | High | Use Google Colab A100 free tier |
| Claude API rate limits during generation | Low | Medium | Implement local Ollama fallback |
| Copyright issues with novel content | High | High | Only support public-domain or user-owned content |
| Whisper accuracy low for non-English speech | Medium | Medium | Allow text input as fallback; multilingual Whisper models |
| SDXL too slow on CPU | High | Low | Make image generation fully optional; skip by default |
| Novel entity extraction misses key lore | Medium | High | Allow user to manually review/edit extracted entities |

