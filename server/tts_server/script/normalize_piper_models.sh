#!/usr/bin/env bash

set -euo pipefail

log() {
  printf "%s | %s\n" "$(date '+%Y-%m-%d %H:%M:%S')" "$*"
}

banner() {
  echo "---------------------------------------------------------------------"
  echo "$*"
  echo "---------------------------------------------------------------------"
}

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"

# Local bind-mounted directory relative to repo root
LOCAL_DIR_REL="server/tts_server/models/piper-onnx-kss-korean"
LOCAL_DIR_ABS="$REPO_ROOT/$LOCAL_DIR_REL"

# Target filenames expected by OpenTTS
TARGET_MODEL="model.onnx"
TARGET_CONFIG="model.onnx.json"

# Possible source filenames (from HF/model card examples)
SRC_MODELS=(
  "piper-kss-korean.onnx"
  "ko_KR-kss-low.onnx"
)
SRC_CONFIGS=(
  "piper-kss-korean.onnx.json"
  "ko_KR-kss-low.onnx.json"
)

banner "Goal: Ensure Piper voice folders contain $TARGET_MODEL and $TARGET_CONFIG"
log "Repo root: $REPO_ROOT"
log "Local model dir (relative): $LOCAL_DIR_REL"
log "Local model dir (absolute): $LOCAL_DIR_ABS"

ensure_target_files() {
  local folder="$1"
  log "Processing folder: $folder"
  mkdir -p "$folder"

  local src_model=""
  for cand in "${SRC_MODELS[@]}"; do
    if [[ -f "$folder/$cand" ]]; then src_model="$cand"; break; fi
  done

  local src_config=""
  for cand in "${SRC_CONFIGS[@]}"; do
    if [[ -f "$folder/$cand" ]]; then src_config="$cand"; break; fi
  done

  log "Detected src model: ${src_model:-<none>}"
  log "Detected src config: ${src_config:-<none>}"

  if [[ -n "$src_model" ]]; then
    if [[ "$src_model" != "$TARGET_MODEL" ]]; then
      log "Creating/overwriting $folder/$TARGET_MODEL from $src_model"
      cp -f "$folder/$src_model" "$folder/$TARGET_MODEL"
    else
      log "$TARGET_MODEL already present"
    fi
  fi

  if [[ -n "$src_config" ]]; then
    if [[ "$src_config" != "$TARGET_CONFIG" ]]; then
      log "Creating/overwriting $folder/$TARGET_CONFIG from $src_config"
      cp -f "$folder/$src_config" "$folder/$TARGET_CONFIG"
    else
      log "$TARGET_CONFIG already present"
    fi
  fi

  log "Folder contents after normalization:" 
  (cd "$folder" && ls -al | sed 's/^/  /')

  # Verification
  local ok=1
  if [[ -f "$folder/$TARGET_MODEL" && -f "$folder/$TARGET_CONFIG" ]]; then
    ok=0
  fi

  if [[ $ok -eq 0 ]]; then
    log "Verification: SUCCESS — both $TARGET_MODEL and $TARGET_CONFIG exist"
  else
    log "Verification: FAILURE — missing target files"
    return 1
  fi
}

# 1) Normalize local bind-mounted directory (if exists)
banner "Step 1/2: Normalize local bind-mounted directory"
if [[ -d "$LOCAL_DIR_ABS" ]]; then
  ensure_target_files "$LOCAL_DIR_ABS"
else
  log "Local directory not found. Skipping: $LOCAL_DIR_ABS"
fi

# 2) Normalize files inside the Docker named volume for folder ko_KR-kss-low
banner "Step 2/2: Normalize files inside Docker volume (folder: ko_KR-kss-low)"

resolve_volume_name() {
  # 1) explicit env
  if [[ -n "${VOLUME_NAME:-}" ]]; then echo "$VOLUME_NAME"; return 0; fi
  # 2) from running containers' mounts
  local c vols
  for c in tts-backend voices-fetcher; do
    if docker inspect "$c" >/dev/null 2>&1; then
      vols=$(docker inspect -f '{{range .Mounts}}{{if or (eq .Destination "/data/local/voices") (eq .Destination "/voices")}}{{.Name}} {{end}}{{end}}' "$c" 2>/dev/null | tr -d '\r')
      if [[ -n "$vols" ]]; then
        # pick first non-empty token
        for v in $vols; do
          if [[ -n "$v" ]]; then echo "$v"; return 0; fi
        done
      fi
    fi
  done
  # 3) prefer compose-scoped '*_voices'
  local cand
  cand=$(docker volume ls --format '{{.Name}}' | grep -E '_voices$' | head -n 1 || true)
  if [[ -n "$cand" ]]; then echo "$cand"; return 0; fi
  # 4) fallback to plain 'voices' if exists
  if docker volume inspect voices >/dev/null 2>&1; then echo "voices"; return 0; fi
  # none
  echo ""; return 1
}

VOLUME_NAME_RESOLVED=$(resolve_volume_name || true)

if [[ -z "${VOLUME_NAME_RESOLVED}" ]]; then
  log "No docker volume matching '*_voices' or 'voices' found. Skipping step 2."
else
  log "Using docker volume: ${VOLUME_NAME_RESOLVED}"
  docker run --rm -v "${VOLUME_NAME_RESOLVED}:/voices" alpine sh -lc '
    set -euo pipefail
    src_dir="/voices/ko_KR-kss-low"
    echo "$(date +%Y-%m-%d\ %H:%M:%S) | Source in volume: ${src_dir}"
    mkdir -p "$src_dir"
    ls -al "$src_dir" || true
    if [ -f "$src_dir/ko_KR-kss-low.onnx" ] && [ ! -f "$src_dir/model.onnx" ]; then
      echo "$(date +%Y-%m-%d\ %H:%M:%S) | Copy ko_KR-kss-low.onnx -> model.onnx"
      cp -f "$src_dir/ko_KR-kss-low.onnx" "$src_dir/model.onnx"
    fi
    if [ -f "$src_dir/ko_KR-kss-low.onnx.json" ] && [ ! -f "$src_dir/model.onnx.json" ]; then
      echo "$(date +%Y-%m-%d\ %H:%M:%S) | Copy ko_KR-kss-low.onnx.json -> model.onnx.json"
      cp -f "$src_dir/ko_KR-kss-low.onnx.json" "$src_dir/model.onnx.json"
    fi
    echo "$(date +%Y-%m-%d\ %H:%M:%S) | After copy (source dir):"; ls -al "$src_dir"

    # Ensure Piper scan path exists and contains model files
    piper_dir="/voices/piper/ko_KR-kss-low"
    echo "$(date +%Y-%m-%d\ %H:%M:%S) | Preparing Piper scan path: ${piper_dir}"
    mkdir -p "$piper_dir"
    if [ -f "$src_dir/model.onnx" ]; then cp -f "$src_dir/model.onnx" "$piper_dir/model.onnx"; fi
    if [ -f "$src_dir/model.onnx.json" ]; then cp -f "$src_dir/model.onnx.json" "$piper_dir/model.onnx.json"; fi
    echo "$(date +%Y-%m-%d\ %H:%M:%S) | Piper dir contents:"; ls -al "$piper_dir" || true

    if [ -f "$piper_dir/model.onnx" ] && [ -f "$piper_dir/model.onnx.json" ]; then
      echo "$(date +%Y-%m-%d\ %H:%M:%S) | Verification: SUCCESS — Piper path has model.onnx and model.onnx.json"
      exit 0
    else
      echo "$(date +%Y-%m-%d\ %H:%M:%S) | Verification: FAILURE — Piper path missing target files"; exit 1
    fi
  '
fi

banner "All steps completed"
log "Goal satisfied: Each voice folder now includes $TARGET_MODEL and $TARGET_CONFIG"


