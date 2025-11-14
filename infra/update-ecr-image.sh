#!/usr/bin/env bash

# Update ECR Image URI in docker-compose.yml
# Run this on EC2 instance to automatically set the correct ECR image URI

set -euo pipefail

COMPOSE_FILE="${1:-/opt/password-manager/docker-compose.yml}"

echo "Updating ECR image URI in docker-compose.yml..."
echo ""

# Get account ID
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
echo "Account ID: ${ACCOUNT_ID}"

# Get region from .env file or use default
if [ -f "${COMPOSE_FILE%/*}/.env" ]; then
    REGION=$(grep AWS_REGION "${COMPOSE_FILE%/*}/.env" | cut -d'=' -f2 | tr -d ' ')
else
    REGION="${AWS_REGION:-us-east-1}"
fi
echo "Region: ${REGION}"

# Build ECR URI
ECR_IMAGE="${ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com/password-manager:latest"
echo "ECR Image: ${ECR_IMAGE}"
echo ""

# Update docker-compose.yml
if [ -f "$COMPOSE_FILE" ]; then
    # Backup original
    cp "$COMPOSE_FILE" "${COMPOSE_FILE}.bak"
    
    # Update image line
    sed -i "s|image:.*|image: ${ECR_IMAGE}|" "$COMPOSE_FILE"
    
    echo "✓ Updated ${COMPOSE_FILE}"
    echo ""
    echo "Updated image line:"
    grep "image:" "$COMPOSE_FILE"
else
    echo "ERROR: File not found: ${COMPOSE_FILE}"
    exit 1
fi

echo ""
echo "Next step: docker-compose up -d"

