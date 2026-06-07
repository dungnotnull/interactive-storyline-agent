# PROJECT-detail.md — interactive-storyline-agent

## Executive Summary
The Interactive Storyline Agent is an AI-powered platform that transforms any written work — novels, scripts, short stories — into voice-driven interactive fiction (IF) experiences. Users become the protagonist of their favorite books, make branching decisions using natural voice commands, and watch the story evolve in the original author's style. The system uses Agentic RAG to ground every AI generation in the source text's world-building, and a fine-tuned local SLM for cost-efficient, style-faithful narrative continuation.

---

## Problem Statement
Reading is a passive medium: 65% of readers report wishing they could influence the story's outcome (Gallup Reading Survey, 2023). Existing interactive fiction platforms (Twine, Ink, Choice of Games) require authors to hand-craft every branch — an enormous labor cost. Meanwhile, large language models hallucinate lore and break canonical consistency when asked to continue stories cold, without grounding. There is no system today that can take an arbitrary existing novel and produce a coherent, style-faithful, branching RPG experience automatically.

**Key statistics:**
- Global interactive fiction market valued at $3.2B in 2023, growing at 18% CAGR (Grand View Research)
- 72% of Gen Z readers prefer interactive/participatory content formats (Pew Research 2024)
- Fine-tuned 7B models match GPT-4 style transfer quality at ~1/50th the inference cost (Stanford HELM 2024)
- RAG reduces LLM hallucination rate by 45-60% in knowledge-grounded tasks (Lewis et al., 2020)

---

## Target Users & Use Cases

| User Type | Use Case |
|-----------|---------|
| Avid readers | Replay favorite novels as interactive experiences |
| Language learners | Immerse in foreign-language literature interactively |
| Writers & authors | Prototype branching narratives from their own drafts |
| Game designers | Rapid IF prototyping from source material |
| Educators | Classroom interactive literature analysis |
| Tabletop RPG players | Convert sourcebooks into solo campaigns |

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    INTERACTIVE STORYLINE AGENT                  │
├─────────────────────────────────────────────────────────────────┤
│  FRONTEND (Electron + React)                                    │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────────────────┐ │
│  │ Story Canvas │  │ Choice Panel │  │ Voice Input Button    │ │
│  │ (scene text  │  │ (3-4 options │  │ (Whisper transcribe)  │ │
│  │  + image)    │  │  + free text)│  │                       │ │
│  └──────────────┘  └──────────────┘  └───────────────────────┘ │
├─────────────────────────────────────────────────────────────────┤
│  BACKEND API (FastAPI)                                          │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │            NARRATIVE ENGINE (DAG State Machine)           │  │
│  │  story_tree.sqlite  ←→  scene_generator  ←→  choice_gen  │  │
│  └───────────────────────────────────────────────────────────┘  │
│  ┌──────────────────────┐  ┌───────────────────────────────┐   │
│  │  AGENTIC RAG LAYER   │  │     LLM ROUTER                │   │
│  │  ┌────────────────┐  │  │  Claude API → GPT-4 →         │   │
│  │  │ ChromaDB       │  │  │  Ollama (fine-tuned Llama-3)  │   │
│  │  │ (lore store)   │  │  │                               │   │
│  │  │ - characters   │  │  └───────────────────────────────┘   │
│  │  │ - world rules  │  │  ┌───────────────────────────────┐   │
│  │  │ - timeline     │  │  │  STYLE ADAPTER STORE          │   │
│  │  │ - factions     │  │  │  (QLoRA adapters per author)  │   │
│  │  └────────────────┘  │  └───────────────────────────────┘   │
│  └──────────────────────┘                                       │
├─────────────────────────────────────────────────────────────────┤
│  INGESTION PIPELINE                                             │
│  PDF/EPUB/TXT → text chunker → entity extractor → embedder     │
│                                    ↓                            │
│              ChromaDB lore store + SQLite metadata             │
├─────────────────────────────────────────────────────────────────┤
│  VOICE PIPELINE                                                 │
│  Microphone → Whisper (local) → intent classifier → narrative   │
└─────────────────────────────────────────────────────────────────┘
```

---

## Tech Stack

| Component | Technology | Source |
|-----------|-----------|--------|
| Backend API | Python 3.11 + FastAPI | pip |
| Frontend | React 18 + Electron 28 | npm |
| Local LLM runtime | Ollama | ollama.ai |
| Base LLM (fine-tune) | Llama-3-8B-Instruct | HuggingFace |
| Fine-tuning | QLoRA via Hugging Face PEFT | pip |
| Vector DB | ChromaDB | pip |
| Embeddings | sentence-transformers/all-MiniLM-L6-v2 | HuggingFace |
| Voice recognition | Whisper (local, small/medium) | HuggingFace/OpenAI |
| Story state | SQLite 3 + DAG structure | stdlib |
| Document parsing | pypdf2, ebooklib, BeautifulSoup4 | pip |
| Image generation | Stable Diffusion XL (optional) | HuggingFace |
| Encryption | cryptography (AES-256-GCM) | pip |
| Primary LLM API | Anthropic Claude API | anthropic SDK |
| Fallback LLM API | OpenAI GPT-4 API | openai SDK |

---

## ML/DL Models Section

### Core Models

**1. Llama-3-8B-Instruct (fine-tuned via QLoRA)**
- HuggingFace ID: `meta-llama/Meta-Llama-3-8B-Instruct`
- Purpose: Style-faithful story branch generation and NPC dialogue
- Fine-tuning strategy: QLoRA (4-bit quantization, r=16, alpha=32)
- Training data: 50,000–200,000 tokens of target author's text (public domain or licensed)
- Output: Swappable LoRA adapters (~80MB each) stored per author in `adapters/` directory
- Fallback: Claude API when adapter not available

**2. sentence-transformers/all-MiniLM-L6-v2**
- HuggingFace ID: `sentence-transformers/all-MiniLM-L6-v2`
- Purpose: Generate embeddings for novel chunks stored in ChromaDB
- Dimension: 384
- Usage: Lore retrieval — top-k semantically similar context chunks injected into generation prompt

**3. openai/whisper-small + whisper-medium**
- HuggingFace ID: `openai/whisper-small`, `openai/whisper-medium`
- Purpose: Offline voice-to-text transcription of user's spoken commands
- whisper-small: fast, lower accuracy (low-end hardware)
- whisper-medium: higher accuracy, ~2s latency on CPU

**4. stabilityai/stable-diffusion-xl-base-1.0 (optional)**
- HuggingFace ID: `stabilityai/stable-diffusion-xl-base-1.0`
- Purpose: Generate scene illustrations from story scene descriptions
- Triggered: Once per new scene node if enabled in settings

### Fine-Tuning Plan
- **Dataset construction:** Extract 200-500 sentence pairs (context → continuation) from author's text
- **Format:** Alpaca-style instruction tuning: `{"instruction": "Continue in [author]'s style:", "input": "[scene context]", "output": "[continuation]"}`
- **Hardware requirement:** 24GB VRAM GPU or Google Colab A100 (via free tier)
- **Training time:** ~2-4 hours per author adapter on A100
- **Evaluation:** BLEU score vs. held-out author text + human style-match ratings

---

## External LLM API Integration

### Pluggable Backend Design
```python
class LLMRouter:
    chain = [
        ClaudeBackend(model="claude-opus-4-8"),   # primary
        OpenAIBackend(model="gpt-4o"),             # fallback
        OllamaBackend(model="llama3-style-tuned"), # local fallback
    ]
    
    def generate(self, prompt, lore_context):
        for backend in chain:
            try:
                return backend.generate(prompt, lore_context)
            except (RateLimitError, APIError):
                continue
        raise AllBackendsFailedError
```

### Claude API Integration (Primary)
- Used for: main story branch generation, NPC dialogue, lore consistency checking
- System prompt: includes retrieved ChromaDB lore chunks (top-5 most relevant)
- Temperature: 0.75 for narrative generation, 0.3 for lore consistency checks
- Max tokens: 800 per scene generation call
- Caching: use Anthropic prompt caching for the lore-context system prompt (saves ~60% cost)

---

## Feature Specification

### MVP Features
- [x] Ingest PDF/EPUB/TXT novel and extract full text
- [x] Extract characters, locations, factions into ChromaDB lore store
- [x] Generate opening scene from novel's first chapter with 3 branching choices
- [x] Voice input (Whisper local) → parse user's choice/action
- [x] Generate next scene based on user's choice + retrieved lore context
- [x] Display story text in readable UI with scene illustrations (optional)
- [x] Save/load game state (SQLite DAG, AES-256 encrypted)
- [x] Support free-text actions beyond the offered 3 choices
- [x] Basic author style configuration (manually selected)

### Advanced Features
- [ ] Author style fine-tuning pipeline (QLoRA adapter training UI)
- [ ] Multi-protagonist support (switch POV characters)
- [ ] NPC memory system (NPCs remember past player interactions)
- [ ] Consequence tracking (long-term karma/relationship stats)
- [ ] Multiplayer co-op storyline (2-4 players, each as different characters)
- [ ] Export completed playthrough as illustrated e-book/PDF
- [ ] Community adapter marketplace (share trained style adapters)
- [ ] Mobile app (iOS/Android React Native)
- [ ] Text-to-speech narration (Coqui TTS or ElevenLabs)

---

## Full E2E Data Flow

1. User uploads novel file (PDF/EPUB/TXT) via frontend
2. Ingestion pipeline: parse text → chunk into 512-token segments with 50-token overlap
3. Entity extractor (Claude API): identify characters, locations, factions, world rules → store as structured JSON
4. Embedder (all-MiniLM-L6-v2): embed all chunks → store in ChromaDB with metadata
5. Game session initialized: SQLite DAG created with root node = novel opening
6. Opening scene generator: retrieve top-5 lore chunks relevant to "opening scene" → send to Claude API → receive scene text + 3 choices
7. User speaks their choice via microphone → Whisper transcribes → intent classifier maps to choice ID or free-text action
8. Next scene generator: query ChromaDB for top-5 chunks relevant to [current scene + user action] → build prompt with lore context → LLM router → receive new scene + choices
9. New DAG node created, linked to parent node with edge labeled by user's action
10. Scene text displayed; optional: Stable Diffusion XL generates scene illustration from scene description
11. Save state: serialize current DAG path + scene metadata to SQLite → AES-256 encrypt
12. Repeat steps 7-11 until user ends session or story reaches a canonical ending

---

## Privacy & Security

| Concern | Solution |
|---------|---------|
| Novel content | Processed and stored locally only; never sent to external APIs in bulk |
| Game saves | AES-256-GCM encrypted SQLite, key derived from user passphrase (PBKDF2) |
| Voice data | Whisper runs locally; audio discarded after transcription |
| API calls | Only scene-level prompts (~500 tokens) sent; full novel never transmitted |
| Style adapters | Stored locally; optional opt-in sharing via adapter marketplace |
| User choices | Stored only in local SQLite; no telemetry without explicit consent |

---

## Key Python/JS Dependencies

```
# Python (backend)
fastapi==0.111.0
uvicorn==0.29.0
anthropic==0.30.0
openai==1.35.0
chromadb==0.5.3
sentence-transformers==3.0.1
transformers==4.42.0
peft==0.11.1          # QLoRA fine-tuning
bitsandbytes==0.43.1  # 4-bit quantization
torch==2.3.0
torchaudio==2.3.0
openai-whisper==20231117
pypdf2==3.0.1
ebooklib==0.18
diffusers==0.29.0     # Stable Diffusion XL
cryptography==42.0.8
sqlalchemy==2.0.31
networkx==3.3          # DAG management

# JavaScript (frontend)
react: 18.3.1
electron: 31.0.0
electron-builder: 24.13.3
@xenova/transformers: 2.17.2  # in-browser Whisper fallback
tailwindcss: 3.4.4
zustand: 4.5.4        # state management
```

---

## Improvement Suggestions (Beyond Original Idea)

1. **Emotional arc tracking:** Use sentiment analysis to monitor story tension/release curves; intervene if AI generates flat emotional arcs
2. **Canon violation detector:** Dedicated ChromaDB query after each generation to check for logical contradictions before showing scene to user
3. **Multilingual support:** Fine-tune style adapter on translated text for cross-language experiences (read in English, play in Vietnamese)
4. **Difficulty modes:** "Faithful" mode (stays close to original plot), "Chaos" mode (maximum divergence allowed)
5. **Author comparison UI:** Show side-by-side generated text vs. actual author excerpt with style-match score
6. **Streaming generation:** Stream scene text token-by-token for a typewriter effect, reducing perceived latency
7. **Modular lore injection:** Allow user to manually annotate/override lore entries in ChromaDB for house-rule customization
8. **Replay divergence tree:** Visual DAG explorer showing all branches the user has played and the ones left unexplored
9. **Social playthrough sharing:** Export a playthrough branch as a shareable link/document without exposing full novel content
10. **Adaptive difficulty:** Track player decision patterns; if player consistently picks "safest" options, introduce narrative consequences that force tougher choices
