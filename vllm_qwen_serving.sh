#!/usr/bin/env bash
# vLLM High-Throughput Serving Script for Qwen2.5-Coder-32B
set -euo pipefail

MODEL_ID="${MODEL_NAME:-Qwen/Qwen2.5-Coder-32B-Instruct-AWQ}"
PORT="${PORT:-8000}"
MAX_MODEL_LEN="${MAX_MODEL_LEN:-131072}"
GPU_MEM_UTIL="${GPU_MEM_UTIL:-0.92}"

echo "=== Starting vLLM Serving Engine for ${MODEL_ID} ==="
echo "Context Window: ${MAX_MODEL_LEN} tokens"
echo "Quantization: AWQ 4-Bit"

python3 -m vllm.entrypoints.openai.api_server \
    --model "${MODEL_ID}" \
    --port "${PORT}" \
    --host "0.0.0.0" \
    --quantization awq \
    --max-model-len "${MAX_MODEL_LEN}" \
    --gpu-memory-utilization "${GPU_MEM_UTIL}" \
    --enable-auto-tool-choice \
    --tool-call-parser qwen \
    --enforce-eager \
    --tensor-parallel-size 1
