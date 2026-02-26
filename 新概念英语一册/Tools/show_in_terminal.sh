#!/usr/bin/env bash
set -euo pipefail

if ! command -v chafa >/dev/null 2>&1; then
  echo "chafa is not installed. Run: brew install chafa" >&2
  exit 1
fi

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 <image-path> [WxH]" >&2
  echo "Example: $0 \"新概念英语一册/p7-007.png\" 100x40" >&2
  exit 1
fi

image_path="$1"
size="${2:-}"

if [[ ! -f "$image_path" ]]; then
  echo "Image not found: $image_path" >&2
  exit 1
fi

if [[ -z "$size" ]]; then
  cols="$(tput cols 2>/dev/null || echo 100)"
  rows="$(tput lines 2>/dev/null || echo 40)"
  max_cols=$(( cols > 6 ? cols - 4 : cols ))
  max_rows=$(( rows > 6 ? rows - 4 : rows ))
  size="${max_cols}x${max_rows}"
fi

chafa -f symbols --symbols ascii --colors none --invert --size="$size" "$image_path"
