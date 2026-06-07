
import os
import io
import json
import hashlib
import sqlite3
from datetime import datetime
from typing import List, Optional, Dict, Any
from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from dotenv import load_dotenv
import anthropic
import openai
import chromadb
from sentence_transformers import SentenceTransformer
import torch
import whisper
import numpy as np
import networkx as nx
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from peft import PeftModel, PeftConfig
from transformers import AutoModelForCausalLM, AutoTokenizer
import ollama
# Load environment variables
load_dotenv()
# Initialize FastAPI app
app = FastAPI(title='Interactive Storyline Agent', version='0.1.0')
# Configuration
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
ELEVENLABS_API_KEY = os.getenv('ELEVENLABS_API_KEY')
STABILITY_API_KEY = os.getenv('STABILITY_API_KEY')
OLLAMA_HOST = os.getenv('OLLAMA_HOST', 'http://localhost:11434')
CHROMA_PATH = os.getenv('CHROMA_PATH', './chroma_db')
SQLITE_PATH = os.getenv('SQLITE_PATH', './storyline.db')
SAVE_KEY = os.getenv('SAVE_KEY', '').encode()  # 32-byte key for AESGCM
if not SAVE_KEY or len(SAVE_KEY) != 32:
    raise RuntimeError('SAVE_KEY must be set to a 32-byte value in .env')
# Initialize clients
anthropic_client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY) if ANTHROPIC_API_KEY else None
openai_client = openai.OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None
# ChromaDB
chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)
chroma_collection = chroma_client.get_or_create_collection(name='lore')
# Embedding model
embedder = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
# Whisper model (small)
whisper_model = whisper.load_model('small')
# SQLite setup
def get_db():
    conn = sqlite3.connect(SQLITE_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn
def init_db():
    conn = get_db()
    c = conn.cursor()
    # Lore table for extracted entities
    c.execute('''
        CREATE TABLE IF NOT EXISTS lore (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            entity_type TEXT NOT NULL,
            name TEXT NOT NULL,
            description TEXT,
            embedding BLOB
        )
    ''')
    # Narrative DAG nodes table
    c.execute('''
        CREATE TABLE IF NOT EXISTS nodes (
            id TEXT PRIMARY KEY,
            scene_text TEXT NOT NULL,
            choices_json TEXT NOT NULL,
            parent_id TEXT,
            edge_label TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    # Game saves table (encrypted)
    c.execute('''
        CREATE TABLE IF NOT EXISTS saves (
            save_id TEXT PRIMARY KEY,
            encrypted_data BLOB NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()
init_db()
# Pydantic models
class NovelUploadResponse(BaseModel):
    message: str
    chunk_count: int
class EntityExtractResponse(BaseModel):
    entities: List[Dict[str, Any]]
class SceneGenerateRequest(BaseModel):
    session_id: str
    action: str
class SceneGenerateResponse(BaseModel):
    scene_text: str
    choices: List[str]
    node_id: str
class VoiceTranscribeResponse(BaseModel):
    text: str
class StyleAdapterInfo(BaseModel):
    author: str
    adapter_path: str
class SaveGameRequest(BaseModel):
    session_id: str
    save_name: str
class LoadGameRequest(BaseModel):
    save_name: str
# Helper functions
def get_embedding(text: str) -> List[float]:
    return embedder.encode(text).tolist()
def store_lore_entity(entity_type: str, name: str, description: str):
    conn = get_db()
    c = conn.cursor()
    embedding = get_embedding(description or name)
    c.execute('''
        INSERT INTO lore (entity_type, name, description, embedding)
        VALUES (?, ?, ?, ?)
    ''', (entity_type, name, description, sqlite3.Binary(np.array(embedding, dtype=np.float32).tobytes())))
    conn.commit()
    conn.close()
    # Also add to ChromaDB for retrieval
    chroma_collection.add(
        embeddings=[embedding],
        documents=[description or name],
        metadatas=[{'entity_type': entity_type, 'name': name}],
        ids=[f'{entity_type}:{name}:{hashlib.md5((entity_type+name).encode()).hexdigest()}']
    )
def extract_entities_with_claude(text: str) -> List[Dict[str, str]]:
    if not anthropic_client:
        raise RuntimeError('Anthropic API not configured')
    prompt = 'Extract characters, locations, and factions from the following text. Return a JSON list where each item has fields: entity_type (character|location|faction), name, description (brief). Text:\\n' + text
    try:
        msg = anthropic_client.messages.create(
            model='claude-opus-4-8',
            max_tokens=1000,
            temperature=0.0,
            system='You are an expert literary analyst.',
            messages=[{'role': 'user', 'content': prompt}]
        )
        import json
        content = msg.content[0].text if hasattr(msg.content[0], 'text') else str(msg.content[0])
        entities = json.loads(content)
        return entities
    except Exception as e:
        raise RuntimeError(f'Entity extraction failed: {e}')
def retrieve_lore_context(query: str, k: int = 5) -> List[str]:
    q_emb = get_embedding(query)
    results = chroma_collection.query(query_embeddings=[q_emb], n_results=k)
    return results.get('documents', [[]])[0]
def generate_scene_with_llm(prompt: str, max_tokens: int = 800, temperature: float = 0.75) -> str:
    # Try Claude, then OpenAI, then Ollama
    if anthropic_client:
        try:
            msg = anthropic_client.messages.create(
                model='claude-opus-4-8',
                max_tokens=max_tokens,
                temperature=temperature,
                system='You are a storyteller that continues narratives in the style of the provided author, using the given lore context.',
                messages=[{'role': 'user', 'content': prompt}]
            )
            return msg.content[0].text if hasattr(msg.content[0], 'text') else str(msg.content[0])
        except Exception as e:
            print(f'Claude API error: {e}')
    if openai_client:
        try:
            resp = openai_client.chat.completions.create(
                model='gpt-4o',
                max_tokens=max_tokens,
                temperature=temperature,
                messages=[{'role': 'system', 'content': 'You are a storyteller that continues narratives in the style of the provided author, using the given lore context.'},
                          {'role': 'user', 'content': prompt}]
            )
            return resp.choices[0].message.content
        except Exception as e:
            print(f'OpenAI API error: {e}')
    # Ollama fallback (assumes model is pulled)
    try:
        resp = ollama.generate(model='llama3', prompt=prompt, options={'temperature': temperature, 'num_predict': max_tokens})
        return resp['response']
    except Exception as e:
        raise RuntimeError(f'All LLM backends failed: {e}')
def parse_scene_and_choices(llm_output: str) -> tuple[str, List[str]]:
    # Expect format: Scene: ...\\nChoices: 1. ... 2. ... 3. ...
    lines = llm_output.strip().split('\\n')
    scene_lines = []
    choices = []
    in_choices = False
    import re
    for line in lines:
        if line.lower().startswith('choices:'):
            in_choices = True
            choice_part = line[len('choices:'):].strip()
            if choice_part:
                parts = re.split(r'\\d+\\.', choice_part)
                choices = [p.strip() for p in parts if p.strip()]
            continue
        if in_choices:
            if re.match(r'^\\d+\\.', line):
                parts = re.split(r'\\d+\\.', line)
                choices.extend([p.strip() for p in parts if p.strip()])
            else:
                scene_lines.append(line)
        else:
            scene_lines.append(line)
    scene = ' '.join(scene_lines).strip()
    if not choices:
        choices = re.findall(r'(?:^|\\n)\\s*[\\-\\*]\\s+(.+)', llm_output)
    return scene, choices[:4]  # limit to 4
def encrypt_data(data: bytes) -> bytes:
    nonce = os.urandom(12)
    aesgcm = AESGCM(SAVE_KEY)
    ct = aesgcm.encrypt(nonce, data, None)
    return nonce + ct
def decrypt_data(encrypted: bytes) -> bytes:
    nonce = encrypted[:12]
    ct = encrypted[12:]
    aesgcm = AESGCM(SAVE_KEY)
    return aesgcm.decrypt(nonce, ct, None)
# API Endpoints
@app.post('/novel/upload', response_model=NovelUploadResponse)
async def upload_novel(file: UploadFile = File(...)):
    content = await file.read()
    text = ''
    if file.filename.endswith('.pdf'):
        import pypdf2
        pdf_reader = pypdf2.PdfReader(io.BytesIO(content))
        for page in pdf_reader.pages:
            text += page.extract_text() or ''
    elif file.filename.endswith('.epub'):
        import ebooklib
        from ebooklib import epub
        book = epub.read_epub(io.BytesIO(content))
        for item in book.get_items():
            if item.get_type() == ebooklib.ITEM_DOCUMENT:
                text += item.get_content().decode('utf-8', errors='ignore')
    else:
        text = content.decode('utf-8', errors='ignore')
    # Chunk text (approx 2000 chars per chunk)
    max_chunk_chars = 2000
    overlap = 200
    chunks = []
    start = 0
    while start < len(text):
        end = start + max_chunk_chars
        chunk = text[start:end]
        chunks.append(chunk)
        start = end - overlap
    # Store chunks in ChromaDB
    for i, chunk in enumerate(chunks):
        emb = get_embedding(chunk)
        chroma_collection.add(
            embeddings=[emb],
            documents=[chunk],
            metadatas=[{'chunk_index': i, 'source': file.filename}],
            ids=[f'{file.filename}_chunk_{i}_{hashlib.md5(chunk.encode()).hexdigest()}']
        )
    return NovelUploadResponse(message='Novel uploaded and indexed', chunk_count=len(chunks))
@app.post('/entity/extract', response_model=EntityExtractResponse)
async def extract_entities(novel_filename: str = Form(...)):
    # Get all chunks for this novel from ChromaDB
    results = chroma_collection.get()
    documents = results.get('documents', [])
    metadatas = results.get('metadatas', [])
    relevant_chunks = [doc for doc, meta in zip(documents, metadatas) if meta.get('source') == novel_filename]
    if not relevant_chunks:
        raise HTTPException(status_code=404, detail='Novel not found in index')
    full_text = '\\n'.join(relevant_chunks[:5])  # limit for demo
    entities = extract_entities_with_claude(full_text)
    for ent in entities:
        store_lore_entity(ent['entity_type'], ent['name'], ent.get('description', ''))
    return EntityExtractResponse(entities=entities)
# DAG management helper
def get_narrative_dag(session_id: str) -> nx.DiGraph:
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT id, scene_text, choices_json, parent_id, edge_label FROM nodes WHERE id LIKE ?', (f'{session_id}:%',))
    rows = c.fetchall()
    conn.close()
    G = nx.DiGraph()
    for row in rows:
        node_id = row['id']
        scene_text = row['scene_text']
        choices_json = row['choices_json']
        parent_id = row['parent_id']
        edge_label = row['edge_label']
        G.add_node(node_id, scene_text=scene_text, choices_json=choices_json)
        if parent_id:
            G.add_edge(parent_id, node_id, label=edge_label)
    return G
def add_node_to_dag(session_id: str, scene_text: str, choices: List[str], parent_id: Optional[str], edge_label: Optional[str]) -> str:
    node_id = f'{session_id}:{datetime.utcnow().timestamp():.6f}'
    conn = get_db()
    c = conn.cursor()
    c.execute('''
        INSERT INTO nodes (id, scene_text, choices_json, parent_id, edge_label)
        VALUES (?, ?, ?, ?, ?)
    ''', (node_id, scene_text, json.dumps(choices), parent_id, edge_label))
    conn.commit()
    conn.close()
    return node_id
@app.post('/scene/generate', response_model=SceneGenerateResponse)
async def generate_scene(req: SceneGenerateRequest):
    G = get_narrative_dag(req.session_id)
    parent_id = None
    edge_label = None
    if G.number_of_nodes() == 0:
        prompt = 'Generate the opening scene of a story based on the uploaded novel. Provide 3-4 choices for the user to continue.'
    else:
        leaves = [n for n in G.nodes() if G.out_degree(n) == 0]
        if not leaves:
            leaves = list(G.nodes())
        leaf = sorted(leaves)[-1]
        parent_id = leaf
        edge_label = req.action
        parent_scene = G.nodes[leaf]['scene_text']
        query = parent_scene + ' ' + req.action
        lore_chunks = retrieve_lore_context(query)
        lore_text = '\\n'.join(lore_chunks)
        prompt = 'You are a talented storyteller. Continue the story in the style of the original author.\\n\\nCurrent scene: ' + parent_scene + '\\nUser action or choice: ' + req.action + '\\n\\nRelevant lore context:\\n' + lore_text + '\\n\\nGenerate the next scene description and provide 3-4 choices for what the user can do next.'
    llm_output = generate_scene_with_llm(prompt)
    scene_text, choices = parse_scene_and_choices(llm_output)
    node_id = add_node_to_dag(req.session_id, scene_text, choices, parent_id, edge_label)
    return SceneGenerateResponse(scene_text=scene_text, choices=choices, node_id=node_id)
@app.post('/voice/transcribe', response_model=VoiceTranscribeResponse)
async def transcribe_voice(file: UploadFile = File(...)):
    contents = await file.read()
    import tempfile
    with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp:
        tmp.write(contents)
        tmp_path = tmp.name
    try:
        result = whisper_model.transcribe(tmp_path)
        text = result['text'].strip()
    finally:
        os.remove(tmp_path)
    return VoiceTranscribeResponse(text=text)
@app.get('/style/adapters', response_model=List[StyleAdapterInfo])
async def list_style_adapters():
    adapter_dir = './adapters'
    if not os.path.isdir(adapter_dir):
        return []
    adapters = []
    for author in os.listdir(adapter_dir):
        author_path = os.path.join(adapter_dir, author)
        if os.path.isdir(author_path):
            adapters.append(StyleAdapterInfo(author=author, adapter_path=author_path))
    return adapters
@app.post('/style/train')
async def train_style_adapter(author: str = Form(...), text_file: UploadFile = File(...)):
    adapter_dir = f'./adapters/{author}'
    os.makedirs(adapter_dir, exist_ok=True)
    train_path = os.path.join(adapter_dir, 'train.txt')
    with open(train_path, 'wb') as f:
        f.write(await text_file.read())
    return {'message': f'Training data saved for {author}. Training not executed in this demo.'}
@app.post('/canon/check')
async def check_canon(scene_text: str = Form(...)):
    chunks = retrieve_lore_context(scene_text, k=3)
    query_emb = get_embedding(scene_text)
    violations = []
    for chunk in chunks:
        chunk_emb = get_embedding(chunk)
        sim = np.dot(query_emb, chunk_emb) / (np.linalg.norm(query_emb) * np.linalg.norm(chunk_emb))
        if sim < 0.5:
            violations.append({'chunk': chunk, 'similarity': float(sim)})
    return {'violations': violations, 'count': len(violations)}
@app.post('/save/game')
async def save_game(req: SaveGameRequest):
    G = get_narrative_dag(req.session_id)
    data = {
        'session_id': req.session_id,
        'nodes': [{'id': n, 'scene_text': G.nodes[n]['scene_text'], 'choices_json': G.nodes[n]['choices_json']} for n in G.nodes()],
        'edges': [{'source': u, 'target': v, 'label': G.edges[u, v].get('label')} for u, v in G.edges()],
        'timestamp': datetime.utcnow().isoformat()
    }
    json_bytes = json.dumps(data).encode('utf-8')
    encrypted = encrypt_data(json_bytes)
    conn = get_db()
    c = conn.cursor()
    c.execute('''
        INSERT OR REPLACE INTO saves (save_id, encrypted_data)
        VALUES (?, ?)
    ''', (req.save_name, encrypted))
    conn.commit()
    conn.close()
    return {'message': f'Game saved as {req.save_name}'}
@app.post('/load/game')
async def load_game(req: LoadGameRequest):
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT encrypted_data FROM saves WHERE save_id = ?', (req.save_name,))
    row = c.fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail='Save not found')
    decrypted = decrypt_data(row['encrypted_data'])
    data = json.loads(decrypted)
    return data
@app.get('/health')
async def health():
    return {'status': 'ok'}

