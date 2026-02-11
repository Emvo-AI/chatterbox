import os
import io
import time
import torch
import runpod
import base64
import logging
import tempfile
import soundfile as sf
from chatterbox.mtl_tts import ChatterboxMultilingualTTS


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger("__handler__")

device = "cuda" if torch.cuda.is_available() else "cpu"
# Force all CUDA loads to CPU for local testing on Mac
if not torch.cuda.is_available():
    orig_load = torch.load
    def mocked_load(*args, **kwargs):
        kwargs['map_location'] = torch.device('cpu')
        return orig_load(*args, **kwargs)
    torch.load = mocked_load

# mtl_tts_model = ChatterboxMultilingualTTS.from_pretrained(device=device)
# In handler.py
mtl_tts_model = ChatterboxMultilingualTTS.from_pretrained(
    device='cuda'
)

def handler(event):
    input_data = event.get("input", {})
    text = input_data.get("text", "")
    audio_b64 = input_data.get("audio_b64", "")
    lang_id = input_data.get("language_id", "en")

    audio_prompt_path = None

    try:
        if not text:
            return {"error": "No text provided"}

        # Decode and save prompt audio if provided
        if audio_b64:
            try:
                audio_bytes = base64.b64decode(audio_b64, validate=True)
            except Exception as e:
                logger.error(f"Invalid base64 audio: {str(e)}")
                return {"error": "Invalid audio_b64 format"}

            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav", dir="/tmp") as tmp_file:
                tmp_file.write(audio_bytes)
                audio_prompt_path = tmp_file.name

        # Generate audio
        audio = mtl_tts_model.generate(
            text=text,
            language_id=lang_id,
            audio_prompt_path=audio_prompt_path,
        )
        logger.info("Auido Generated")
        # ta.save("test-2.wav", audio, mtl_tts_model.sr)
        audio_np = audio.detach().squeeze().cpu().numpy()

        # Write to in-memory buffer
        buffer = io.BytesIO()
        sf.write(buffer, audio_np, mtl_tts_model.sr, format="WAV")
        buffer.seek(0)
        logger.info("audio : %s", audio)
        logger.info("audio_np : %s", audio_np)
        # Encode to base64
        audio_base64 = base64.b64encode(buffer.read()).decode("utf-8")

        return {
            "audio_base64": audio_base64,
            "sample_rate": mtl_tts_model.sr,
            "format": "WAV"
        }

    except Exception as e:
        logger.exception("TTS generation failed")
        return {"error": str(e)}

    finally:
        # Cleanup temp file
        if audio_prompt_path:
            try:
                if os.path.exists(audio_prompt_path):
                    os.remove(audio_prompt_path)
            except Exception as cleanup_error:
                logger.warning(f"Temp file cleanup failed: {cleanup_error}")

# Start the Serverless function when the script is run


runpod.serverless.start({'handler': handler })
