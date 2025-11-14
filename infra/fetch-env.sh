#!/usr/bin/env bash

# Fetch Environment Variables from SSM Parameter Store
# Pulls SSM parameters and writes them to .env file for docker-compose
# Run this script on EC2 instance to populate environment variables

set -euo pipefail

# Default values
AWS_REGION="${AWS_REGION:-eu-north-1}"
SSM_PREFIX="/password-manager"
ENV_FILE="${ENV_FILE:-.env}"

echo "=========================================="
echo "Fetching Environment Variables from SSM"
echo "=========================================="
echo "Region: ${AWS_REGION}"
echo "SSM Prefix: ${SSM_PREFIX}"
echo "Output file: ${ENV_FILE}"
echo ""

# Check if AWS CLI is available
if ! command -v aws &> /dev/null; then
    echo "ERROR: AWS CLI is not installed"
    echo "Run: ./ec2_setup.sh"
    exit 1
fi

# Check if we can access SSM
if ! aws ssm get-parameter --name "${SSM_PREFIX}/AWS_REGION" --region "${AWS_REGION}" &> /dev/null; then
    echo "ERROR: Cannot access SSM Parameter Store"
    echo "Check:"
    echo "  1. IAM role is attached to EC2 instance"
    echo "  2. IAM role has ssm:GetParameter permission"
    echo "  3. SSM parameters exist (run aws_bootstrap.sh first)"
    exit 1
fi

echo "Fetching parameters from SSM..."
echo ""

# Function to get SSM parameter value
get_ssm_param() {
    local param_name="$1"
    local decrypt="${2:-false}"
    
    if [ "$decrypt" = "true" ]; then
        aws ssm get-parameter \
            --name "${param_name}" \
            --region "${AWS_REGION}" \
            --with-decryption \
            --query 'Parameter.Value' \
            --output text
    else
        aws ssm get-parameter \
            --name "${param_name}" \
            --region "${AWS_REGION}" \
            --query 'Parameter.Value' \
            --output text
    fi
}

# Create .env file
cat > "${ENV_FILE}" <<EOF
# Environment variables fetched from SSM Parameter Store
# Generated on: $(date)
# Region: ${AWS_REGION}

# Flask Configuration
FLASK_ENV=production
SESSION_SECRET=$(get_ssm_param "${SSM_PREFIX}/SESSION_SECRET" true)
PORT=$(get_ssm_param "${SSM_PREFIX}/PORT")

# AWS Configuration
AWS_REGION=$(get_ssm_param "${SSM_PREFIX}/AWS_REGION")
# Note: AWS credentials come from EC2 IAM role, not env vars

# DynamoDB Tables
DYNAMODB_USERS_TABLE=$(get_ssm_param "${SSM_PREFIX}/DYNAMODB_USERS_TABLE")
DYNAMODB_ACCOUNTS_TABLE=$(get_ssm_param "${SSM_PREFIX}/DYNAMODB_ACCOUNTS_TABLE")
DYNAMODB_PASSWORDS_TABLE=$(get_ssm_param "${SSM_PREFIX}/DYNAMODB_PASSWORDS_TABLE")
EOF

echo "✓ Created ${ENV_FILE} file"
echo ""

# Display summary (without sensitive values)
echo "Parameters fetched:"
echo "  - SESSION_SECRET: [REDACTED]"
echo "  - PORT: $(get_ssm_param "${SSM_PREFIX}/PORT")"
echo "  - AWS_REGION: $(get_ssm_param "${SSM_PREFIX}/AWS_REGION")"
echo "  - DYNAMODB_USERS_TABLE: $(get_ssm_param "${SSM_PREFIX}/DYNAMODB_USERS_TABLE")"
echo "  - DYNAMODB_ACCOUNTS_TABLE: $(get_ssm_param "${SSM_PREFIX}/DYNAMODB_ACCOUNTS_TABLE")"
echo "  - DYNAMODB_PASSWORDS_TABLE: $(get_ssm_param "${SSM_PREFIX}/DYNAMODB_PASSWORDS_TABLE")"
echo ""

echo "=========================================="
echo "Environment file ready!"
echo "=========================================="
echo "File location: $(pwd)/${ENV_FILE}"
echo ""
echo "Next step: docker-compose up -d"
echo ""

