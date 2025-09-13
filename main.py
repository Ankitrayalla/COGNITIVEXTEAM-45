from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.responses import StreamingResponse
import io
import os

# local imports
from rewriter import load_rewriter_model, rewrite_text
from tts import synthesize_to_mp3_bytes, list_voices

app = FastAPI(title="EchoVerse Backend")

class RewriteRequest(BaseModel):
    text: str
    tone: str = "Neutral"
    max_tokens: int = 512

class RewriteResponse(BaseModel):
    rewritten: str

class TTSRequest(BaseModel):
    text: str
    voice: str = None
    rate: int = 150

@app.post("/rewrite", response_model=RewriteResponse)
async def rewrite_endpoint(req: RewriteRequest):
    if not req.text.strip():
        raise HTTPException(status_code=400, detail="Empty text provided")
    try:
        gen = load_rewriter_model()
        out = rewrite_text(gen, req.text, req.tone, max_length=req.max_tokens)
        return {"rewritten": out}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Rewrite failed: {e}")

@app.post("/tts")
async def tts_endpoint(req: TTSRequest):
    if not req.text.strip():
        raise HTTPException(status_code=400, detail="Empty text provided")
    try:
        mp3_bytes = synthesize_to_mp3_bytes(req.text, voice_id=req.voice, rate=req.rate)
        return StreamingResponse(io.BytesIO(mp3_bytes), media_type="audio/mpeg")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"TTS failed: {e}")

@app.get("/voices")
async def voices_endpoint():
    try:
        return list_voices()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list voices: {e}")

# optional simple root
@app.get("/")
def root():
    return {"status": "EchoVerse backend running", "model": os.getenv("MODEL_OVERRIDE", "ibm-granite/granite-3.3-2b-instruct")}
