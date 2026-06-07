# SECOND-KNOWLEDGE-BRAIN.md — interactive-storyline-agent

> Self-improving knowledge base. Updated weekly by automated crawler.
> Last manual seed: 2026-06-03

---

## Core Concepts & Theoretical Foundations

### Interactive Fiction (IF) Theory
- **Narrative branching:** Story graphs where player choices create edges to alternative scene nodes; balance between authored structure and emergent AI generation
- **Storyworld consistency:** The set of rules, facts, and causal relationships that constitute a fictional world; violations break immersion (Minsky's frame problem applied to narrative)
- **Ludonarrative harmony:** Alignment between gameplay mechanics and story theme; IF succeeds when choices feel meaningful within the narrative logic
- **Emergent narrative:** Narrative arising from AI/procedural systems rather than hand-authored scripts; contrasted with pre-scripted branching

### Style Transfer & Author Voice
- **Stylometric fingerprinting:** Quantifying an author's voice via function word distributions, sentence length distributions, POS tag n-grams, and syntactic complexity measures
- **Neural style transfer for text:** Unlike image style transfer, textual style transfer must preserve semantic content while transforming surface style (vocabulary, sentence structure, tone)
- **Low-resource style adaptation:** Fine-tuning large LMs on small author corpora (5k–50k tokens) using parameter-efficient methods (LoRA, QLoRA) to avoid overfitting

### Retrieval-Augmented Generation (RAG) for Narrative
- **Dense passage retrieval:** Using neural embeddings (not keyword search) to retrieve semantically relevant lore chunks before generation
- **Agentic RAG:** Multi-step RAG where the agent decides what to retrieve, when, and how to integrate retrieved facts — not a single fixed retrieval call
- **Lore grounding:** Pre-filtering generated text for factual consistency against the source text's established world rules

### Knowledge Representation for Worlds
- **Narrative knowledge graphs:** Entities (characters, locations, objects) + relations (knows, hates, owns) as a graph; ChromaDB stores dense embeddings, a separate KG stores symbolic relations
- **Event calculus for fiction:** Formal representation of how events change world state; useful for detecting causal violations in generated continuations

---

## Key Research Papers

| Title | Authors | Year | Venue | Link | Relevance |
|-------|---------|------|-------|------|-----------|
| Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks | Lewis et al. | 2020 | NeurIPS | https://arxiv.org/abs/2005.11401 | Foundational RAG paper — core architecture |
| QLORA: Efficient Finetuning of Quantized LLMs | Dettmers et al. | 2023 | NeurIPS | https://arxiv.org/abs/2305.14314 | QLoRA fine-tuning for style adapters |
| LORA: Low-Rank Adaptation of Large Language Models | Hu et al. | 2022 | ICLR | https://arxiv.org/abs/2106.09685 | LoRA theory underlying QLoRA |
| Wordcraft: Story Writing With Large Language Models | Ippolito et al. | 2022 | IUI | https://arxiv.org/abs/2203.15463 | Human-AI co-writing; relevant to IF scene generation |
| Language Models are Few-Shot Learners (GPT-3) | Brown et al. | 2020 | NeurIPS | https://arxiv.org/abs/2005.14165 | Few-shot style prompting baseline |
| DRAMA: Towards Diverse and Consistent Interactive Fiction | Ammanabrolu et al. | 2021 | ACL | https://arxiv.org/abs/2010.12757 | Consistency in IF generation — directly relevant |
| StoryNLG: Narrative Planning with Causal Commonsense Knowledge | Fan et al. | 2019 | EMNLP | https://arxiv.org/abs/1909.07042 | Narrative planning with commonsense grounding |
| Stylistic Transfer in Natural Language Generation | Shen et al. | 2017 | NeurIPS | https://arxiv.org/abs/1705.09655 | Neural style transfer for text |
| Whisper: Robust Speech Recognition via Large-Scale Weak Supervision | Radford et al. | 2022 | ICML | https://arxiv.org/abs/2212.04356 | Whisper model — voice input backbone |
| CTRL: A Conditional Transformer Language Model for Controllable Generation | Keskar et al. | 2019 | arXiv | https://arxiv.org/abs/1909.05858 | Controlled text generation; style codes |
| Generating Interactive Worlds with Text | Côté et al. | 2019 | AAAI | https://arxiv.org/abs/1906.09427 | Text world generation framework |
| Choose Your Own Adventure: Diverse Storytelling Using LLMs | Chen et al. | 2023 | EMNLP | https://arxiv.org/abs/2310.01717 | Branching story generation with LLMs |

---

## State-of-the-Art ML/DL Models

### Story & Narrative Generation

| Model | HuggingFace ID | Papers with Code | Notes |
|-------|---------------|-----------------|-------|
| Llama-3-8B-Instruct | `meta-llama/Meta-Llama-3-8B-Instruct` | — | Base for style fine-tuning via QLoRA |
| Llama-3-70B-Instruct | `meta-llama/Meta-Llama-3-70B-Instruct` | — | Higher quality; use via API only |
| Mistral-7B-Instruct-v0.3 | `mistralai/Mistral-7B-Instruct-v0.3` | — | Alternative fine-tuning base |
| Phi-3-mini-4k-instruct | `microsoft/Phi-3-mini-4k-instruct` | — | Lightweight option for low-end hardware |
| GPT-NeoX-20B | `EleutherAI/gpt-neox-20b` | LAMBADA: 72.0 | Strong creative writing base |

### Text Embeddings (RAG/ChromaDB)

| Model | HuggingFace ID | Dimension | Notes |
|-------|---------------|-----------|-------|
| all-MiniLM-L6-v2 | `sentence-transformers/all-MiniLM-L6-v2` | 384 | Fast, good quality |
| all-mpnet-base-v2 | `sentence-transformers/all-mpnet-base-v2` | 768 | Higher quality, slower |
| bge-large-en-v1.5 | `BAAI/bge-large-en-v1.5` | 1024 | SOTA retrieval quality |
| e5-large-v2 | `intfloat/e5-large-v2` | 1024 | Strong for passage retrieval |

### Voice Recognition

| Model | HuggingFace ID | WER (LibriSpeech) | Notes |
|-------|---------------|------------------|-------|
| whisper-small | `openai/whisper-small` | 4.2% | Fast, good for clear speech |
| whisper-medium | `openai/whisper-medium` | 3.0% | Better accuracy, 2-3s latency |
| whisper-large-v3 | `openai/whisper-large-v3` | 2.7% | Best accuracy, high memory |
| wav2vec2-large-960h | `facebook/wav2vec2-large-960h` | 3.4% | English-only alternative |

### Image Generation (Scene Illustrations)

| Model | HuggingFace ID | Notes |
|-------|---------------|-------|
| SDXL Base 1.0 | `stabilityai/stable-diffusion-xl-base-1.0` | Best open-source quality |
| SDXL-Turbo | `stabilityai/sdxl-turbo` | 4-step generation, real-time |
| Juggernaut XL | `RunDiffusion/Juggernaut-XL-v9` | Better photorealistic scenes |

---

## Tools, Libraries & Frameworks

| Tool/Library | GitHub | Use Case |
|-------------|--------|---------|
| ChromaDB | https://github.com/chroma-core/chroma | Vector store for lore embeddings |
| LlamaIndex | https://github.com/run-llama/llama_index | High-level RAG framework (alternative to custom RAG) |
| LangChain | https://github.com/langchain-ai/langchain | Agent orchestration, RAG chains |
| Hugging Face PEFT | https://github.com/huggingface/peft | QLoRA fine-tuning |
| bitsandbytes | https://github.com/TimDettmers/bitsandbytes | 4-bit quantization for QLoRA |
| Ollama | https://github.com/ollama/ollama | Local LLM serving (GGUF models) |
| openai-whisper | https://github.com/openai/whisper | Local speech recognition |
| NetworkX | https://github.com/networkx/networkx | Story DAG data structure |
| FastAPI | https://github.com/tiangolo/fastapi | Backend API framework |
| crawl4ai | https://github.com/unclecode/crawl4ai | Self-updating knowledge crawler |
| ebooklib | https://github.com/aerkalov/ebooklib | EPUB parsing |
| pypdf2 | https://github.com/py-pdf/pypdf | PDF parsing |
| Electron | https://github.com/electron/electron | Desktop app framework |
| Ink (narrative scripting) | https://github.com/inkle/ink | Reference: industry IF scripting language |
| Twine | https://github.com/klembot/twinejs | Reference: visual IF authoring |
| AI Dungeon (closed source) | — | Reference product for market benchmarking |

---

## Self-Update Protocol

### crawl4ai Configuration

```python
# scripts/update_knowledge_brain.py
from crawl4ai import AsyncWebCrawler

SOURCES = [
    # ArXiv categories
    "https://arxiv.org/search/?query=interactive+fiction+generation&searchtype=all",
    "https://arxiv.org/search/?query=story+generation+language+model&searchtype=all",
    "https://arxiv.org/search/?query=style+transfer+LLM+text&searchtype=all",
    "https://arxiv.org/search/?query=narrative+branching+AI&searchtype=all",
    # HuggingFace Papers
    "https://huggingface.co/papers?q=story+generation",
    "https://huggingface.co/papers?q=text+style+transfer",
    # ACM Digital Library
    "https://dl.acm.org/action/doSearch?query=interactive+fiction+AI",
    # Papers with Code
    "https://paperswithcode.com/task/story-generation",
    "https://paperswithcode.com/task/text-style-transfer",
]

SEARCH_QUERIES = [
    "interactive fiction generation 2025",
    "story branching large language model",
    "author style transfer fine-tuning",
    "retrieval augmented generation narrative",
    "voice-driven game AI",
    "narrative knowledge graph LLM",
]
```

### Update Frequency
- **Weekly** — every Monday 02:00 local time
- Triggered by: `python scripts/update_knowledge_brain.py --append`
- Max 20 new entries per run to avoid bloat

### Format for New Entries (Date-Stamped)
```markdown
### [YYYY-MM-DD] New Entries
| Title | Authors | Year | Venue | Link | Relevance |
|-------|---------|------|-------|------|-----------|
| ...   | ...     | ...  | ...   | ...  | ...       |
```

---

## Knowledge Update Log

### [2026-06-03] Initial Manual Seed
- Populated: 12 foundational research papers across RAG, style transfer, IF generation, Whisper
- Populated: 18 HuggingFace models across LLMs, embeddings, voice, image generation
- Populated: 15 tools and libraries with GitHub links
- Source: Manual research curation by project author
- Next automated update: 2026-06-10 (first weekly crawl)
