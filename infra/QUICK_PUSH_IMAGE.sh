#!/usr/bin/env bash

# Quick script to push Docker image to ECR
# Run from your local machine

set -euo pipefail

ACCOUNT_ID=503561414328
REGION=us-east-1
ECR_URI="${ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com/password-manager:latest"

echo "=========================================="
echo "Pushing Docker Image to ECR"
echo "=========================================="
echo "Account ID: ${ACCOUNT_ID}"
echo "Region: ${REGION}"
echo "ECR URI: ${ECR_URI}"
echo ""

# Check if image exists locally
if ! docker images | grep -q "password-manager.*local"; then
    echo "Building Docker image..."
    docker build -t password-manager:local .
else
    echo "✓ Docker image exists locally"
fi

# Login to ECR
echo "Logging into ECR..."
aws ecr get-login-password --region $REGION | \
  docker login --username AWS --password-stdin \
  ${ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com

# Tag image (if not already tagged)
if ! docker images | grep -q "${ECR_URI}"; then
    echo "Tagging image..."
    docker tag password-manager:local $ECR_URI
else
    echo "✓ Image already tagged"
fi

# Push to ECR
echo "Pushing image to ECR..."
docker push $ECR_URI

# Verify
echo ""
echo "Verifying image in ECR..."
aws ecr describe-images \
  --repository-name password-manager \
  --region $REGION \
  --query 'imageDetails[0].{Tags:imageTags,Size:imageSizeInBytes,Pushed:imagePushedAt}' \
  --output table

echo ""
echo "=========================================="
echo "✅ Image pushed successfully!"
echo "=========================================="
echo "EC2 can now pull the image with:"
echo "  docker compose pull"
echo "  docker compose up -d"
echo ""

