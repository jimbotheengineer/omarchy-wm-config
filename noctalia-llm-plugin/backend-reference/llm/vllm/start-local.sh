#!/usr/bin/env bash
set -euo pipefail

VLLM_HOME="$HOME/llm/vllm"
# Resolve a validated, persisted selection; do not source user-editable data.
mapfile -d '' -t choice < <(python3 "$VLLM_HOME/model-selection.py" launch)
if (( ${#choice[@]} != 3 )); then
  echo 'No valid vLLM model selection' >&2
  exit 1
fi
profile=${choice[0]}
MODEL_DIR=${choice[1]}
CHAT_TEMPLATE=${choice[2]}

extra=()
if [[ $profile == qwen-gguf ]]; then
  # Never let an extensionless GGUF fall through to the JSON loader (OOM).
  extra+=(--load-format gguf --config-format gguf
    --hf-config-path "$VLLM_HOME/models/tokenizers/local-llm"
    --tokenizer "$VLLM_HOME/models/tokenizers/local-llm"
    --max-model-len 32768)
elif [[ $profile == nvfp4 ]]; then
  extra+=(--speculative-config '{"method":"mtp","num_speculative_tokens":4}'
    --linear-backend cutlass --max-model-len 115200)
else
  echo "Unsupported profile: $profile" >&2
  exit 1
fi

cd "$VLLM_HOME"
source .venv/bin/activate

# The complete NVFP4/FP8 language model and KV cache stay on GPU. The 0.83
# executor limit reserves VRAM for the Wayland desktop; CPU weight offload and
# KV offload remain disabled. Vision is enabled so pi can send images.
exec vllm serve "$MODEL_DIR" \
  --served-model-name local-llm \
  --chat-template "$CHAT_TEMPLATE" \
  "${extra[@]}" \
  --host 127.0.0.1 \
  --port 8000 \
  --gpu-memory-utilization 0.83 \
  --cpu-offload-gb 0 \
  --enforce-eager \
  --kv-cache-dtype fp8_e4m3 \
  --max-num-seqs 4 \
  --max-num-batched-tokens 4096 \
  --enable-prefix-caching \
  --enable-chunked-prefill \
  --enable-auto-tool-choice \
  --tool-call-parser qwen3_coder \
  --reasoning-parser qwen3 \
  --seed 0
