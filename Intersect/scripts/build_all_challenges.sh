#!/usr/bin/env bash
# Builds a Docker image for every challenge under challenges/*/
# Image tag is read from each challenge's challenge.yaml (docker_image field).
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CHALLENGES_DIR="$SCRIPT_DIR/../challenges"

for dir in "$CHALLENGES_DIR"/*/; do
    slug=$(basename "$dir")
    yaml_file="$dir/challenge.yaml"
    if [[ ! -f "$yaml_file" ]]; then
        continue
    fi

    image=$(grep '^docker_image:' "$yaml_file" | sed 's/docker_image:\s*//; s/"//g')
    echo "Building $slug -> $image"
    docker build -t "$image" "$dir"
done

echo "Done. Run scripts/seed_db.py to register challenges in the database."
