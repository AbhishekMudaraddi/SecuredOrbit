#!/usr/bin/env bash

# AWS Bootstrap Script for Password Manager
# Automates initial AWS setup: ECR repository, SSM parameters, and IAM policy snippets

set -euo pipefail

# Default values
AWS_REGION="${AWS_REGION:-eu-north-1}"
APP_NAME="${APP_NAME:-password-manager}"

# Validate required variables
if [ -z "${ACCOUNT_ID:-}" ]; then
    echo "ERROR: ACCOUNT_ID environment variable must be set"
    echo "Usage: ACCOUNT_ID=123456789012 ./infra/aws_bootstrap.sh"
    exit 1
fi

echo "=========================================="
echo "AWS Bootstrap Script"
echo "=========================================="
echo "Account ID: ${ACCOUNT_ID}"
echo "Region: ${AWS_REGION}"
echo "App Name: ${APP_NAME}"
echo ""

# ============================================================================
# 1. ECR REPOSITORY
# ============================================================================
echo "--- Step 1: Checking ECR Repository ---"

ECR_REPO_NAME="${APP_NAME}"
ECR_REPO_URI="${ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${ECR_REPO_NAME}"

# Check if ECR repository exists
if aws ecr describe-repositories \
    --repository-names "${ECR_REPO_NAME}" \
    --region "${AWS_REGION}" \
    >/dev/null 2>&1; then
    echo "✓ ECR repository '${ECR_REPO_NAME}' already exists"
else
    echo "Creating ECR repository '${ECR_REPO_NAME}'..."
    aws ecr create-repository \
        --repository-name "${ECR_REPO_NAME}" \
        --region "${AWS_REGION}" \
        --image-scanning-configuration scanOnPush=true \
        --encryption-configuration encryptionType=AES256
    echo "✓ Created ECR repository '${ECR_REPO_NAME}'"
fi

echo "ECR Repository URI: ${ECR_REPO_URI}"
echo ""

# ============================================================================
# 2. SSM PARAMETER STORE
# ============================================================================
echo "--- Step 2: Setting up SSM Parameters ---"

SSM_PREFIX="/password-manager"

# Function to check if SSM parameter exists
ssm_param_exists() {
    local param_name="$1"
    aws ssm get-parameter \
        --name "${param_name}" \
        --region "${AWS_REGION}" \
        >/dev/null 2>&1
}

# Function to create or update SSM parameter (String type)
create_or_update_ssm_string() {
    local param_name="$1"
    local param_value="$2"
    local description="$3"
    
    if ssm_param_exists "${param_name}"; then
        echo "  SSM param ${param_name} already exists, updating..."
        aws ssm put-parameter \
            --name "${param_name}" \
            --value "${param_value}" \
            --type "String" \
            --description "${description}" \
            --overwrite \
            --region "${AWS_REGION}" \
            >/dev/null
        echo "  ✓ Updated SSM param ${param_name}"
    else
        echo "  Creating SSM param ${param_name}..."
        aws ssm put-parameter \
            --name "${param_name}" \
            --value "${param_value}" \
            --type "String" \
            --description "${description}" \
            --region "${AWS_REGION}" \
            >/dev/null
        echo "  ✓ Created SSM param ${param_name}"
    fi
}

# Function to create SSM SecureString parameter (only if doesn't exist)
create_ssm_secure_string_if_not_exists() {
    local param_name="$1"
    local param_value="$2"
    local description="$3"
    
    if ssm_param_exists "${param_name}"; then
        echo "  SSM param ${param_name} already exists (skipping - will not overwrite)"
    else
        echo "  Creating SSM param ${param_name}..."
        aws ssm put-parameter \
            --name "${param_name}" \
            --value "${param_value}" \
            --type "SecureString" \
            --description "${description}" \
            --region "${AWS_REGION}" \
            >/dev/null
        echo "  ✓ Created SSM param ${param_name}"
    fi
}

# SESSION_SECRET - Generate random 32-byte hex string if doesn't exist
SESSION_SECRET_PARAM="${SSM_PREFIX}/SESSION_SECRET"
if ssm_param_exists "${SESSION_SECRET_PARAM}"; then
    echo "  SSM param ${SESSION_SECRET_PARAM} already exists (skipping - will not overwrite)"
else
    echo "  Generating SESSION_SECRET..."
    SESSION_SECRET_VALUE=$(openssl rand -hex 32)
    create_ssm_secure_string_if_not_exists \
        "${SESSION_SECRET_PARAM}" \
        "${SESSION_SECRET_VALUE}" \
        "Session secret key for Flask application"
fi

# AWS_REGION - Can be updated
create_or_update_ssm_string \
    "${SSM_PREFIX}/AWS_REGION" \
    "${AWS_REGION}" \
    "AWS region for the application"

# PORT - Can be updated
create_or_update_ssm_string \
    "${SSM_PREFIX}/PORT" \
    "5001" \
    "Port number for the application"

# DynamoDB Tables - Can be updated
create_or_update_ssm_string \
    "${SSM_PREFIX}/DYNAMODB_ACCOUNTS_TABLE" \
    "PasswordManager-Accounts" \
    "DynamoDB table name for accounts"

create_or_update_ssm_string \
    "${SSM_PREFIX}/DYNAMODB_USERS_TABLE" \
    "PasswordManager-Users" \
    "DynamoDB table name for users"

create_or_update_ssm_string \
    "${SSM_PREFIX}/DYNAMODB_PASSWORDS_TABLE" \
    "PasswordManager-Passwords" \
    "DynamoDB table name for passwords"

echo "✓ SSM parameters setup complete"
echo ""

# ============================================================================
# 3. IAM POLICY SNIPPETS (PRINT ONLY)
# ============================================================================
echo "--- Step 3: IAM Policy Snippets ---"
echo ""
echo "=========================================="
echo "EC2 Role Policy"
echo "=========================================="
cat <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "ECRAccess",
      "Effect": "Allow",
      "Action": [
        "ecr:GetAuthorizationToken"
      ],
      "Resource": "*"
    },
    {
      "Sid": "ECRPullAccess",
      "Effect": "Allow",
      "Action": [
        "ecr:BatchCheckLayerAvailability",
        "ecr:GetDownloadUrlForLayer",
        "ecr:BatchGetImage"
      ],
      "Resource": "arn:aws:ecr:${AWS_REGION}:${ACCOUNT_ID}:repository/${APP_NAME}"
    },
    {
      "Sid": "DynamoDBAccess",
      "Effect": "Allow",
      "Action": [
        "dynamodb:GetItem",
        "dynamodb:PutItem",
        "dynamodb:UpdateItem",
        "dynamodb:DeleteItem",
        "dynamodb:Query",
        "dynamodb:Scan",
        "dynamodb:DescribeTable"
      ],
      "Resource": [
        "arn:aws:dynamodb:${AWS_REGION}:${ACCOUNT_ID}:table/PasswordManager-Accounts",
        "arn:aws:dynamodb:${AWS_REGION}:${ACCOUNT_ID}:table/PasswordManager-Users",
        "arn:aws:dynamodb:${AWS_REGION}:${ACCOUNT_ID}:table/PasswordManager-Passwords"
      ]
    },
    {
      "Sid": "SSMParameterAccess",
      "Effect": "Allow",
      "Action": [
        "ssm:GetParameter",
        "ssm:GetParameters",
        "ssm:GetParametersByPath"
      ],
      "Resource": "arn:aws:ssm:${AWS_REGION}:${ACCOUNT_ID}:parameter/password-manager/*"
    }
  ]
}
EOF

echo ""
echo "=========================================="
echo "Jenkins Role/User Policy"
echo "=========================================="
cat <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "ECRAuthorization",
      "Effect": "Allow",
      "Action": [
        "ecr:GetAuthorizationToken"
      ],
      "Resource": "*"
    },
    {
      "Sid": "ECRPushAccess",
      "Effect": "Allow",
      "Action": [
        "ecr:InitiateLayerUpload",
        "ecr:UploadLayerPart",
        "ecr:CompleteLayerUpload",
        "ecr:PutImage",
        "ecr:BatchCheckLayerAvailability",
        "ecr:DescribeRepositories",
        "ecr:CreateRepository",
        "ecr:GetDownloadUrlForLayer",
        "ecr:ListImages",
        "ecr:BatchGetImage"
      ],
      "Resource": "arn:aws:ecr:${AWS_REGION}:${ACCOUNT_ID}:repository/${APP_NAME}"
    }
  ]
}
EOF

echo ""
echo "=========================================="
echo "Bootstrap Complete!"
echo "=========================================="
echo "Next steps:"
echo "1. Attach the EC2 Role Policy to your EC2 instance role"
echo "2. Attach the Jenkins Role/User Policy to your Jenkins IAM user/role"
echo "3. Your ECR repository URI: ${ECR_REPO_URI}"
echo "4. SSM parameters are ready under: ${SSM_PREFIX}/*"
echo ""

