import io
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from gtts import gTTS

from app.database.session import get_db
from app.schemas.voice import (
    VoiceCommandRequest,
    VoiceCommandResponse,
    SceneInfo
)
from app.services.device.voice import VoiceService

router = APIRouter(prefix="/voice", tags=["Voice & AI"])

# In-memory audio cache for frequent speech utterances
_AUDIO_CACHE = {}


@router.post("/command", response_model=VoiceCommandResponse)
def process_voice_command(
    request: VoiceCommandRequest,
    db: Session = Depends(get_db)
):
    """
    Process natural language or voice commands to control smart home devices,
    activate multi-device scenes, or query system status.
    """
    if not request.text or not request.text.strip():
        raise HTTPException(status_code=400, detail="Voice command text cannot be empty.")

    return VoiceService.execute_command(db, request.text, language=request.language)


@router.get("/scenes", response_model=List[SceneInfo])
def get_smart_scenes():
    """
    Get all pre-configured smart scene routines and quick voice triggers.
    """
    return VoiceService.get_available_scenes()


@router.get("/tts")
def stream_text_to_speech(
    text: str = Query(..., description="Text to synthesize to speech"),
    lang: str = Query("en", description="Target language code (te, hi, en, es, fr)")
):
    """
    Stream authentic, native spoken MP3 audio for any language (Telugu, Hindi, English, Spanish, French).
    Guarantees fluent regional pronunciation regardless of client OS or missing browser voice packs.
    """
    cleaned_text = text.strip()
    if not cleaned_text:
        raise HTTPException(status_code=400, detail="Text cannot be empty.")

    # Normalize language code to standard gTTS language keys
    lang_code = lang.split("-")[0].lower()
    supported_langs = {"te", "hi", "en", "es", "fr", "ta", "bn", "de", "it", "ja"}
    if lang_code not in supported_langs:
        lang_code = "en"

    cache_key = f"{lang_code}:{cleaned_text}"
    if cache_key in _AUDIO_CACHE:
        return StreamingResponse(io.BytesIO(_AUDIO_CACHE[cache_key]), media_type="audio/mpeg")

    try:
        tts = gTTS(text=cleaned_text, lang=lang_code, slow=False)
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        audio_bytes = fp.getvalue()
        
        # Cache for quick repeat playback (limit cache size to 200 items)
        if len(_AUDIO_CACHE) < 200:
            _AUDIO_CACHE[cache_key] = audio_bytes

        return StreamingResponse(io.BytesIO(audio_bytes), media_type="audio/mpeg")
    except Exception as e:
        # Fallback to English TTS if specific regional voice generation encountered an error
        try:
            fallback_tts = gTTS(text=cleaned_text, lang="en", slow=False)
            fp = io.BytesIO()
            fallback_tts.write_to_fp(fp)
            return StreamingResponse(io.BytesIO(fp.getvalue()), media_type="audio/mpeg")
        except Exception:
            raise HTTPException(status_code=500, detail=f"Failed to generate speech audio: {str(e)}")

