#!/usr/bin/env bash

# Quick Fix: Install Docker Compose on Amazon Linux 2
# Run this on your EC2 instance if docker compose doesn't work

set -euo pipefail

echo "Installing Docker Compose (standalone)..."

# Get latest version
DOCKER_COMPOSE_VERSION=$(curl -s https://api.github.com/repos/docker/compose/releases/latest | grep 'tag_name' | cut -d\" -f4)
echo "Installing version: ${DOCKER_COMPOSE_VERSION}"

# Detect architecture
ARCH=$(uname -m)
if [ "$ARCH" = "x86_64" ]; then
    ARCH="x86_64"
elif [ "$ARCH" = "aarch64" ]; then
    ARCH="aarch64"
else
    ARCH="x86_64"  # Default
fi

# Download and install
sudo curl -L "https://github.com/docker/compose/releases/download/${DOCKER_COMPOSE_VERSION}/docker-compose-linux-${ARCH}" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Verify
if docker-compose --version &> /dev/null; then
    echo "✓ Docker Compose installed successfully!"
    docker-compose --version
    echo ""
    echo "Usage: docker-compose up -d"
    echo "Note: Use 'docker-compose' (with hyphen) not 'docker compose'"
else
    echo "✗ Installation failed"
    exit 1
fi

