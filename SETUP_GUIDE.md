# Password Manager - Setup Guide

## 📋 Prerequisites

- Python 3.9+
- AWS Account with DynamoDB access
- AWS Credentials configured
- Docker (for containerized deployment)
- Jenkins (for CI/CD - optional)

---

## 🚀 Quick Start

### Step 1: Clone Repository

```bash
git clone <your-repo-url>
cd password-manager
```

### Step 2: Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Configure AWS Credentials

Create a `.env` file from `env.example`:

```bash
cp env.example .env
```

Edit `.env` and add your AWS credentials:

```env
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_REGION=us-east-1
SESSION_SECRET=your-session-secret-key
PORT=5001
```

### Step 5: Run Application

```bash
python app.py
```

Application will be available at `http://localhost:5000`

---

## 🐳 Docker Setup

### Build Docker Image

```bash
docker build -t password-manager:local .
```

### Run with Docker Compose

```bash
# Ensure .env file exists with AWS credentials
docker-compose up
```

Application will be available at `http://localhost:5001`

---

## ☁️ AWS Setup

### 1. Create DynamoDB Tables

Tables are created automatically when you first run the application:

- `PasswordManager-Users` - User accounts
- `PasswordManager-Accounts` - Account settings
- `PasswordManager-Passwords` - Encrypted passwords

### 2. Configure SSM Parameters

Run the bootstrap script:

```bash
cd infra
ACCOUNT_ID=your-account-id AWS_REGION=us-east-1 ./aws_bootstrap.sh
```

This creates:
- ECR repository
- SSM parameters for configuration

### 3. EC2 Deployment

See `PROJECT_ARCHITECTURE.md` for detailed EC2 deployment instructions.

---

## 🧪 Testing

### Run Tests

```bash
make test
```

Or manually:

```bash
pytest tests/ -v
```

### Test Coverage

```bash
pytest --cov=app --cov-report=html
```

---

## 📝 Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `AWS_ACCESS_KEY_ID` | AWS access key | Yes |
| `AWS_SECRET_ACCESS_KEY` | AWS secret key | Yes |
| `AWS_REGION` | AWS region | Yes |
| `SESSION_SECRET` | Flask session secret | Yes |
| `PORT` | Application port | No (default: 5000) |
| `DYNAMODB_USERS_TABLE` | Users table name | No (default: PasswordManager-Users) |
| `DYNAMODB_ACCOUNTS_TABLE` | Accounts table name | No (default: PasswordManager-Accounts) |
| `DYNAMODB_PASSWORDS_TABLE` | Passwords table name | No (default: PasswordManager-Passwords) |

---

## 🔧 Troubleshooting

### AWS Credentials Error

**Error**: `Unable to locate credentials`

**Solution**: Ensure `.env` file exists with AWS credentials, or set environment variables.

### Port Already in Use

Change port in `.env`:
```env
PORT=5001
```

### Docker Build Fails

Ensure Docker is running:
```bash
docker ps
```

---

## 📚 Additional Documentation

- **README.md**: Main project documentation
- **PROJECT_OVERVIEW.md**: Project overview and features
- **PROJECT_ARCHITECTURE.md**: Complete architecture documentation

---

**Setup complete! See README.md for usage instructions.** ✅

