# AWS Bootstrap Script - Usage Guide

## Prerequisites

1. **AWS CLI installed and configured**
   ```bash
   # Check if AWS CLI is installed
   aws --version
   
   # If not installed, install it:
   # macOS: brew install awscli
   # Linux: pip install awscli
   ```

2. **AWS credentials configured**
   ```bash
   # Check if configured
   aws sts get-caller-identity
   
   # If not configured, run:
   aws configure
   # Enter: Access Key ID, Secret Access Key, Region, Output format
   ```

3. **Required permissions**
   - ECR: `ecr:CreateRepository`, `ecr:DescribeRepositories`
   - SSM: `ssm:PutParameter`, `ssm:GetParameter`
   - IAM: Read access (for policy printing only)

## Getting Your AWS Account ID

You need your AWS Account ID to run the script. Get it using:

```bash
# Method 1: Using AWS CLI
aws sts get-caller-identity --query Account --output text

# Method 2: From AWS Console
# Top right corner → Your account name → Account ID

# Method 3: Save it to a variable
export ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
echo "Account ID: $ACCOUNT_ID"
```

## Running the Script

### Option 1: Direct execution (recommended)

```bash
# Get your Account ID first
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

# Run the script
ACCOUNT_ID=$ACCOUNT_ID ./infra/aws_bootstrap.sh
```

### Option 2: Export variables first

```bash
# Export variables
export ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
export AWS_REGION=eu-north-1  # Optional, defaults to eu-north-1
export APP_NAME=password-manager  # Optional, defaults to password-manager

# Run the script
./infra/aws_bootstrap.sh
```

### Option 3: Custom region/app name

```bash
ACCOUNT_ID=123456789012 \
AWS_REGION=us-east-1 \
APP_NAME=my-password-manager \
./infra/aws_bootstrap.sh
```

### Option 4: One-liner (quickest)

```bash
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text) ./infra/aws_bootstrap.sh
```

## What the Script Does

1. ✅ **Creates ECR Repository** (if doesn't exist)
   - Repository name: `password-manager` (or `${APP_NAME}`)
   - Enables image scanning and encryption

2. ✅ **Creates SSM Parameters** under `/password-manager/`:
   - `SESSION_SECRET` - Auto-generated secure random string
   - `AWS_REGION` - Your AWS region
   - `PORT` - Port 5001
   - `DYNAMODB_*_TABLE` - DynamoDB table names

3. ✅ **Prints IAM Policies** (for manual attachment):
   - EC2 Role Policy (for EC2 instances)
   - Jenkins Role/User Policy (for CI/CD)

## Example Output

```
==========================================
AWS Bootstrap Script
==========================================
Account ID: 123456789012
Region: eu-north-1
App Name: password-manager

--- Step 1: Checking ECR Repository ---
Creating ECR repository 'password-manager'...
✓ Created ECR repository 'password-manager'
ECR Repository URI: 123456789012.dkr.ecr.eu-north-1.amazonaws.com/password-manager

--- Step 2: Setting up SSM Parameters ---
  Generating SESSION_SECRET...
  ✓ Created SSM param /password-manager/SESSION_SECRET
  ✓ Created SSM param /password-manager/AWS_REGION
  ✓ Created SSM param /password-manager/PORT
  ✓ Created SSM param /password-manager/DYNAMODB_ACCOUNTS_TABLE
  ✓ Created SSM param /password-manager/DYNAMODB_USERS_TABLE
  ✓ Created SSM param /password-manager/DYNAMODB_PASSWORDS_TABLE
✓ SSM parameters setup complete

--- Step 3: IAM Policy Snippets ---
[Prints JSON policies...]

==========================================
Bootstrap Complete!
==========================================
```

## Troubleshooting

### Error: "ACCOUNT_ID environment variable must be set"
```bash
# Solution: Set ACCOUNT_ID before running
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text) ./infra/aws_bootstrap.sh
```

### Error: "Unable to locate credentials"
```bash
# Solution: Configure AWS credentials
aws configure
# Or set environment variables:
export AWS_ACCESS_KEY_ID=your-key
export AWS_SECRET_ACCESS_KEY=your-secret
```

### Error: "Access Denied" or permission errors
- Ensure your AWS user/role has permissions for:
  - ECR: `ecr:CreateRepository`, `ecr:DescribeRepositories`
  - SSM: `ssm:PutParameter`, `ssm:GetParameter`

### Script is not executable
```bash
# Make it executable
chmod +x infra/aws_bootstrap.sh
```

## Verifying Results

After running the script, verify everything was created:

```bash
# Check ECR repository
aws ecr describe-repositories --repository-names password-manager --region eu-north-1

# Check SSM parameters
aws ssm get-parameters-by-path --path /password-manager --region eu-north-1

# Get SESSION_SECRET (decrypted)
aws ssm get-parameter --name /password-manager/SESSION_SECRET --with-decryption --region eu-north-1
```

## Next Steps

1. **Attach IAM Policies**: Copy the printed policies and attach them to:
   - EC2 instance role (for running the app)
   - Jenkins IAM user/role (for CI/CD)

2. **Use ECR Repository**: Push your Docker image to the created ECR repository
   ```bash
   # Login to ECR
   aws ecr get-login-password --region eu-north-1 | docker login --username AWS --password-stdin $ACCOUNT_ID.dkr.ecr.eu-north-1.amazonaws.com
   
   # Tag and push
   docker tag password-manager:local $ACCOUNT_ID.dkr.ecr.eu-north-1.amazonaws.com/password-manager:latest
   docker push $ACCOUNT_ID.dkr.ecr.eu-north-1.amazonaws.com/password-manager:latest
   ```

3. **Use SSM Parameters**: Your application can read these parameters at runtime

