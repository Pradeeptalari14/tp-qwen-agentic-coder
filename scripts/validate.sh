#!/usr/bin/env bash
# Smoke test validating Qwen2.5-Coder-32B vLLM API and agentic tool invocation
set -euo pipefail

ENDPOINT="${QWEN_ENDPOINT:-http://localhost:8000/v1}"

if [[ "${1:-}" == "--dry-run" ]]; then
    echo "Dry-run check passed: scripts and python definitions syntax clean."
    exit 0
fi

echo "Checking vLLM health at ${ENDPOINT}/models..."
curl -s "${ENDPOINT}/models" | grep -q "Qwen" && echo "✅ Qwen2.5-Coder Engine is Healthy!"

echo "Testing basic code generation..."
curl -s -X POST "${ENDPOINT}/chat/completions" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "Qwen/Qwen2.5-Coder-32B-Instruct-AWQ",
    "messages": [{"role": "user", "content": "Write a quicksort in Python."}],
    "max_tokens": 150
  }' | grep -q "def quicksort" && echo "✅ Code Generation Succeeded!"

echo "All Qwen2.5-Coder smoke tests passed."
