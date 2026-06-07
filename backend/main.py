
from fastapi import FastAPI

app = FastAPI(title='Interactive Storyline Agent Backend')

@app.get('/health')
async def health():
    return {'status': 'ok'}

@app.get('/')
async def root():
    return {'message': 'Interactive Storyline Agent API'}

