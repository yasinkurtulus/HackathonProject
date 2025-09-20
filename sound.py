import torch
from transformers import SpeechT5Processor, SpeechT5ForTextToSpeech, SpeechT5HifiGan
import io
import numpy as np
import soundfile as sf
from functools import lru_cache

# Modelleri tembel (lazy) yükleyelim ki import sırasında bloklamasın
_processor = None
_model = None
_vocoder = None
_speaker_embedding = None

def _ensure_models_loaded():
    global _processor, _model, _vocoder, _speaker_embedding
    if _processor is None:
        _processor = SpeechT5Processor.from_pretrained("microsoft/speecht5_tts")
    if _model is None:
        _model = SpeechT5ForTextToSpeech.from_pretrained("microsoft/speecht5_tts")
    if _vocoder is None:
        _vocoder = SpeechT5HifiGan.from_pretrained("microsoft/speecht5_hifigan")
    if _speaker_embedding is None:
        # Deterministic speaker embedding for consistent voice
        torch.manual_seed(42)
        _speaker_embedding = torch.randn(1, 512)

def _normalize_text(text: str) -> str:
     return (text or "").strip()

@lru_cache(maxsize=256)
def _synthesize_core(text_norm: str) -> bytes:
    _ensure_models_loaded()
    # For very short tokens (e.g., "go"), end punctuation helps articulation
    tts_text = text_norm if len(text_norm) > 2 else f"{text_norm}."
    inputs = _processor(text=tts_text, return_tensors="pt")
    with torch.no_grad():
        speech = _model.generate_speech(inputs["input_ids"], _speaker_embedding, vocoder=_vocoder)

    waveform = speech.cpu().numpy()  # shape: (T,)
    if waveform.ndim > 1:
        waveform = waveform.squeeze()

    # Simple post-processing: peak normalize and add short fade-in/out
    if waveform.size > 0:
        peak = max(abs(waveform.max()), abs(waveform.min())) or 1.0
        target_peak = 0.9
        waveform = (waveform / peak) * target_peak
        # 10ms fade
        sr = 16000
        fade_len = max(1, int(0.01 * sr))
        fade_in = np.linspace(0.0, 1.0, fade_len)
        fade_out = np.linspace(1.0, 0.0, fade_len)
        waveform[:fade_len] *= fade_in
        waveform[-fade_len:] *= fade_out

    # WAV'e yaz
    buffer = io.BytesIO()
    sf.write(buffer, waveform.astype(np.float32), 16000, format='WAV')
    buffer.seek(0)
    return buffer.read()

def synthesize_wav_bytes(text: str) -> bytes:
    """Verilen metnin WAV ses verisini bytes olarak döndürür (16kHz, mono). Sonuçlar cache'lenir."""
    text_norm = _normalize_text(text)
    if not text_norm:
        return b""
    return _synthesize_core(text_norm)

