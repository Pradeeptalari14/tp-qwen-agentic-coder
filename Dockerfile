FROM nvidia/cuda:12.4.1-devel-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    python3.11 \
    python3.11-dev \
    python3-pip \
    git \
    curl \
    ripgrep \
    ca-certificates && \
    rm -rf /var/lib/apt/lists/*

RUN ln -sf /usr/bin/python3.11 /usr/bin/python3 && \
    python3 -m pip install --upgrade pip

WORKDIR /app

RUN pip install --no-cache-dir \
    vllm==0.6.3 \
    openai==1.54.0 \
    transformers>=4.46.0 \
    accelerate>=1.0.0

COPY qwen_coder_agent.py .
COPY vllm_qwen_serving.sh .
RUN chmod +x vllm_qwen_serving.sh

EXPOSE 8000
CMD ["bash", "vllm_qwen_serving.sh"]
