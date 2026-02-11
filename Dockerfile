# Use a slim Python image with CUDA support
FROM runpod/pytorch:2.1.0-py3.10-cuda11.8.0-devel-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONPATH="/app"

# Install system dependencies for audio and soundfile
RUN apt-get update && apt-get install -y \
    libsndfile1 \
    ffmpeg \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app
# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir runpod
# Copy the handler code
COPY src/ ./src/

# --- Hugging Face Authentication & Model Pre-download ---
# We use an ARG so the token isn't hardcoded in the final image layers
ARG HF_TOKEN
ENV HF_TOKEN=${HF_TOKEN}

# # This command logs in and pre-downloads the model so the Pod starts instantly
# RUN python3 -c "import os; \
# from huggingface_hub import login, snapshot_download; \
# from chatterbox.mtl_tts import ChatterboxMultilingualTTS; \
# login(token=os.getenv('HF_TOKEN')); \
# snapshot_download(repo_id='ResembleAI/chatterbox'); \
# ChatterboxMultilingualTTS.from_pretrained(device='cpu')"

# Set the entrypoint to your handler
CMD ["python", "-u", "src/handler.py"]
