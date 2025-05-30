#!/bin/bash
set -e

# Define file paths
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DOCKER_ROOT="$PROJECT_ROOT/docker"

echo "==> Copying build files into Docker context..."
cp "$PROJECT_ROOT/pyproject.toml" "$DOCKER_ROOT/"
cp "$PROJECT_ROOT/poetry.lock" "$DOCKER_ROOT/" 2>/dev/null || echo "poetry.lock not found, skipping"
cp "$PROJECT_ROOT/environment.yml" "$DOCKER_ROOT/"

echo "==> Building Docker image with Docker Compose..."
HOST_UID=$(id -u)
HOST_GID=$(id -g)
HOST_UID=$HOST_UID HOST_GID=$HOST_GID docker compose -f "$DOCKER_ROOT/docktuna/docker-compose.yml" build

echo "==> Cleaning up temporary files..."
rm -f "$DOCKER_ROOT/pyproject.toml" "$DOCKER_ROOT/poetry.lock" "$DOCKER_ROOT/environment.yml"

echo "✅ Build completed."
