#!/usr/bin/env bash
set -euo pipefail

required_files=(
  ".env.example"
  "apps/web/.env.example"
  "apps/api/.env.example"
)

for file in "${required_files[@]}"; do
  if [[ ! -f "$file" ]]; then
    echo "Missing required environment template: $file" >&2
    exit 1
  fi
done

echo "Environment templates are present."
