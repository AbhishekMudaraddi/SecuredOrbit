# Password Manager - Project Architecture

## 📋 Table of Contents

1. [Overview](#overview)
2. [System Architecture](#system-architecture)
3. [Technology Stack](#technology-stack)
4. [Infrastructure Components](#infrastructure-components)
5. [CI/CD Pipeline](#cicd-pipeline)
6. [Data Flow](#data-flow)
7. [Security Architecture](#security-architecture)
8. [Deployment Architecture](#deployment-architecture)

---

## 🎯 Overview

This Password Manager application is a full-stack web application built with Flask (Python) backend and deployed on AWS infrastructure using Docker containers. The project implements a complete CI/CD pipeline using Jenkins for automated testing, building, and deployment.

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Developer Machine                        │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐      │
│  │   Git Repo   │───▶│   Jenkins    │───▶│   Docker     │      │
│  │  (GitHub)    │    │   (Local)    │    │   Build     │      │
│  └──────────────┘    └──────────────┘    └──────────────┘      │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ Push Image
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                          AWS Cloud                               │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │              ECR (Elastic Container Registry)            │   │
│  │  ┌──────────────────────────────────────────────────┐   │   │
│  │  │  password-manager:latest                         │   │   │
│  │  │  password-manager:<commit-hash>                   │   │   │
│  │  └──────────────────────────────────────────────────┘   │   │
│  └──────────────────────────────────────────────────────────┘   │
│                              │                                   │
│                              │ Pull Image                        │
│                              ▼                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                    EC2 Instance                          │   │
│  │  ┌──────────────────────────────────────────────────┐   │   │
│  │  │  Docker Container: password-manager              │   │   │
│  │  │  Port: 80 → 5001                                 │   │   │
│  │  │  Health Check: /health                            │   │   │
│  │  └──────────────────────────────────────────────────┘   │   │
│  └──────────────────────────────────────────────────────────┘   │
│                              │                                   │
│                              │ Read/Write                       │
│                              ▼                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │              DynamoDB (NoSQL Database)                    │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │   │
│  │  │   Users      │  │  Accounts    │  │  Passwords   │   │   │
│  │  └──────────────┘  └──────────────┘  └──────────────┘   │   │
│  └──────────────────────────────────────────────────────────┘   │
│                              │                                   │
│                              │ Read Config                       │
│                              ▼                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │         SSM Parameter Store (Configuration)               │   │
│  │  ┌──────────────────────────────────────────────────┐   │   │
│  │  │  /password-manager/SESSION_SECRET                │   │   │
│  │  │  /password-manager/AWS_REGION                    │   │   │
│  │  │  /password-manager/PORT                          │   │   │
│  │  │  /password-manager/DYNAMODB_*_TABLE             │   │   │
│  │  └──────────────────────────────────────────────────┘   │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Technology Stack

### Backend
- **Framework**: Flask (Python 3.11)
- **Server**: Gunicorn (WSGI HTTP Server)
- **Database**: Amazon DynamoDB (NoSQL)
- **Encryption**: Fernet (Symmetric Encryption)
- **Authentication**: 
  - bcrypt (Password Hashing)
  - pyotp (TOTP 2FA)
  - QR Code Generation

### Frontend
- **HTML5**: Structure
- **CSS3**: Styling (Responsive Design)
- **JavaScript**: Client-side Logic
- **AJAX**: Asynchronous Requests

### Infrastructure
- **Containerization**: Docker
- **Orchestration**: Docker Compose
- **CI/CD**: Jenkins
- **Cloud Provider**: AWS
  - EC2 (Compute)
  - ECR (Container Registry)
  - DynamoDB (Database)
  - SSM Parameter Store (Configuration)
  - IAM (Access Control)

### Testing & Quality
- **Testing**: pytest, pytest-cov
- **Code Quality**: SonarQube (Optional)
- **Linting**: flake8 (Optional)

---

## 🏛️ Infrastructure Components

### 1. Jenkins (CI/CD Server)

**Location**: Local Machine (Port 8080)

**Purpose**: 
- Automated build and deployment pipeline
- Code quality checks
- Docker image building and pushing

**Key Files**:
- `Jenkinsfile`: Pipeline definition (Declarative Pipeline)
- Configuration: `http://localhost:8080`

**Pipeline Stages**:
1. **Checkout**: Clone code from Git repository
2. **Setup Python**: Create virtual environment, install dependencies
3. **Lint & Tests**: Run tests, generate coverage reports
4. **SonarQube Analysis**: Code quality analysis (optional)
5. **Docker Build & Push**: Build Docker image, push to ECR
6. **Deploy to EC2**: SSH to EC2, pull image, deploy container

**Configuration**:
- AWS Credentials: Configured in Jenkins credentials store
- SSH Credentials: EC2 SSH key (`ec2-ssh`)
- SonarQube: Configured for code quality (optional)

---

### 2. Docker

**Purpose**: Containerization of the application

**Key Files**:
- `Dockerfile`: Defines Docker image
- `docker-compose.yml`: Local development setup
- `.dockerignore`: Excludes unnecessary files from build

**Dockerfile Details**:
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5001
HEALTHCHECK CMD curl http://localhost:5001/health
CMD ["gunicorn", "--bind", "0.0.0.0:5001", "app:app"]
```

**Image Tags**:
- `latest`: Latest stable version
- `<commit-hash>`: Specific commit version (12 characters)

**Build Process**:
- Built on `linux/amd64` platform (for EC2 compatibility)
- Multi-stage caching for faster builds
- Health check included

---

### 3. AWS ECR (Elastic Container Registry)

**Location**: AWS Cloud (`us-east-1`)

**Repository**: `password-manager`

**Full URI**: `503561414328.dkr.ecr.us-east-1.amazonaws.com/password-manager`

**Purpose**:
- Store Docker images
- Version control for deployments
- Secure image distribution

**Access**:
- **Jenkins**: Push images (via AWS credentials)
- **EC2**: Pull images (via IAM role)

**Image Management**:
- Images tagged with Git commit hash
- `latest` tag for current stable version
- Image scanning enabled

---

### 4. AWS EC2 (Elastic Compute Cloud)

**Location**: AWS Cloud

**Instance Details**:
- **Public IP**: `54.198.152.202`
- **User**: `ec2-user`
- **Application Directory**: `/opt/password-manager`

**Purpose**: Host the application container

**Setup Files**:
- `infra/ec2_setup.sh`: Initial EC2 setup script
- `infra/fetch-env.sh`: Fetches environment variables from SSM
- `infra/docker-compose.ec2.yml`: Docker Compose for EC2

**Deployment Process**:
1. SSH to EC2 instance
2. Login to ECR
3. Fetch environment variables from SSM
4. Update `docker-compose.yml` with new image tag
5. Pull Docker image from ECR
6. Start container with `docker compose up -d`
7. Health check on `/health` endpoint
8. Rollback on failure

**Container Configuration**:
- Port Mapping: `80:5001` (HTTP port 80 → Container port 5001)
- Health Check: `/health` endpoint
- Restart Policy: `unless-stopped`
- Logging: JSON file driver

**IAM Role**: 
- ECR pull permissions
- DynamoDB access
- SSM parameter read access

---

### 5. AWS DynamoDB

**Location**: AWS Cloud (`us-east-1`)

**Tables**:

1. **PasswordManager-Users**
   - **Primary Key**: `user_id` (String)
   - **Attributes**: 
     - `username`, `email`, `email_lower`
     - `password_hash` (bcrypt)
     - `encryption_key` (Fernet key, encrypted)
     - `recovery_phrase` (encrypted)
   - **GSI**: `EmailIndex` on `email_lower`

2. **PasswordManager-Accounts**
   - **Primary Key**: `account_id` (String)
   - **Attributes**:
     - `user_id`, `totp_secret`, `totp_enabled`
     - `recovery_words` (encrypted)

3. **PasswordManager-Passwords**
   - **Primary Key**: `password_id` (String)
   - **Attributes**:
     - `user_id`, `service`, `username`
     - `encrypted_password`, `notes`
     - `created_at`, `updated_at`

**Access**:
- EC2 instance via IAM role
- Application uses `boto3` library

---

### 6. AWS SSM Parameter Store

**Location**: AWS Cloud

**Purpose**: Secure configuration management

**Parameters** (under `/password-manager/`):
- `SESSION_SECRET`: Flask session secret (SecureString)
- `AWS_REGION`: AWS region (`us-east-1`)
- `PORT`: Application port (`5001`)
- `DYNAMODB_USERS_TABLE`: Table name
- `DYNAMODB_ACCOUNTS_TABLE`: Table name
- `DYNAMODB_PASSWORDS_TABLE`: Table name

**Access**:
- EC2 instance reads via IAM role
- `fetch-env.sh` script pulls parameters
- Creates `.env` file for Docker Compose

---

## 🔄 CI/CD Pipeline

### Pipeline Flow

```
┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│   Git    │────▶│ Jenkins  │────▶│  Docker  │────▶│   ECR    │
│  Push    │     │  Build   │     │   Build  │     │   Push   │
└──────────┘     └──────────┘     └──────────┘     └──────────┘
                                                          │
                                                          │ Pull
                                                          ▼
                                                 ┌──────────┐
                                                 │   EC2    │
                                                 │  Deploy  │
                                                 └──────────┘
```

### Detailed Pipeline Stages

1. **Checkout**
   - Clones repository from GitHub
   - Checks out specific branch/commit

2. **Setup Python**
   - Creates virtual environment (`.venv`)
   - Installs dependencies from `requirements.txt`

3. **Lint & Tests**
   - Runs pytest with coverage
   - Generates `coverage.xml` and `reports/junit.xml`
   - Publishes test results

4. **SonarQube Analysis** (Optional)
   - Runs SonarQube scanner via Docker
   - Code quality analysis
   - Quality gate check

5. **Docker Build & Push**
   - Builds Docker image for `linux/amd64`
   - Tags with commit hash and `latest`
   - Pushes to ECR

6. **Deploy to EC2** (Only on `main` branch)
   - SSH to EC2 instance
   - Login to ECR
   - Fetch environment variables
   - Pull and deploy new image
   - Health check
   - Rollback on failure

---

## 📊 Data Flow

### User Registration Flow

```
User → Browser → Flask App → DynamoDB (Users Table)
                    ↓
              Generate TOTP Secret
                    ↓
              Generate Recovery Words
                    ↓
              Encrypt & Store
```

### Password Storage Flow

```
User → Dashboard → Flask App → Encrypt Password (Fernet)
                                    ↓
                              DynamoDB (Passwords Table)
```

### Login Flow

```
User → Login Page → Flask App → Verify Password (bcrypt)
                                    ↓
                              Verify TOTP (pyotp)
                                    ↓
                              Create Session
                                    ↓
                              Redirect to Dashboard
```

### Deployment Flow

```
Developer → Git Push → Jenkins → Build Docker Image
                                    ↓
                              Push to ECR
                                    ↓
                              SSH to EC2
                                    ↓
                              Pull Image from ECR
                                    ↓
                              Start Container
                                    ↓
                              Health Check
```

---

## 🔒 Security Architecture

### Encryption

1. **Password Hashing**: bcrypt (one-way hashing)
2. **Password Storage**: Fernet symmetric encryption
3. **Session Management**: Flask sessions with secret key
4. **TOTP**: Time-based One-Time Password (Google Authenticator)

### Authentication

1. **Primary**: Username/Password
2. **2FA**: TOTP via Google Authenticator
3. **Recovery**: 5-word recovery phrase

### AWS Security

1. **IAM Roles**: Least privilege access
2. **SSM Parameter Store**: Secure configuration storage
3. **ECR**: Private container registry
4. **Security Groups**: Network-level access control

---

## 🚀 Deployment Architecture

### Local Development

```
Developer Machine
├── Flask App (Port 5001)
├── Docker Compose
└── Local DynamoDB (Optional)
```

### Production Deployment

```
AWS Cloud
├── EC2 Instance
│   ├── Docker Container
│   │   ├── Flask App (Port 5001)
│   │   └── Gunicorn Server
│   └── Docker Compose
├── ECR
│   └── Docker Images
├── DynamoDB
│   └── Data Tables
└── SSM Parameter Store
    └── Configuration
```

### Network Flow

```
Internet → EC2 Security Group (Port 80) → Docker Container (Port 5001)
                                                      ↓
                                            Flask Application
                                                      ↓
                                            DynamoDB / SSM
```

---

## 📁 Project Structure

```
password-manager/
├── app.py                      # Main Flask application
├── requirements.txt            # Python dependencies
├── Dockerfile                  # Docker image definition
├── docker-compose.yml          # Local development
├── Jenkinsfile                 # CI/CD pipeline definition
├── Makefile                    # Build automation
├── pytest.ini                  # Test configuration
├── sonar-project.properties    # SonarQube configuration
│
├── templates/                  # HTML templates
│   ├── base.html
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   └── ...
│
├── static/                     # Static files
│   ├── css/
│   ├── js/
│   └── ...
│
├── tests/                      # Test files
│   ├── test_app.py
│   ├── test_health.py
│   └── ...
│
├── infra/                      # Infrastructure scripts
│   ├── aws_bootstrap.sh        # AWS initial setup
│   ├── ec2_setup.sh            # EC2 setup script
│   ├── fetch-env.sh            # SSM parameter fetcher
│   └── docker-compose.ec2.yml  # EC2 deployment config
│
└── reports/                    # Test reports
    └── junit.xml
```

---

## 🔧 Key Configuration Files

### Jenkinsfile
- **Location**: Repository root
- **Purpose**: Defines CI/CD pipeline
- **Stages**: Checkout, Setup, Tests, SonarQube, Docker Build, Deploy

### Dockerfile
- **Location**: Repository root
- **Purpose**: Defines Docker image
- **Base Image**: `python:3.11-slim`
- **Port**: 5001
- **Health Check**: `/health` endpoint

### docker-compose.yml
- **Location**: Repository root (local) and `/opt/password-manager/` (EC2)
- **Purpose**: Container orchestration
- **Port Mapping**: `80:5001` (EC2), `5001:5001` (local)

### pytest.ini
- **Location**: Repository root
- **Purpose**: Test configuration
- **Output**: `coverage.xml`, `reports/junit.xml`

---

## 📝 Environment Variables

### Local Development
- `.env` file (not committed)
- AWS credentials
- Flask configuration

### Production (EC2)
- Fetched from SSM Parameter Store
- Generated by `fetch-env.sh`
- Stored in `.env` file for Docker Compose

---

## 🎯 Summary

This project demonstrates:

1. **Full-Stack Development**: Flask backend with HTML/CSS/JS frontend
2. **Cloud Infrastructure**: AWS EC2, ECR, DynamoDB, SSM
3. **Containerization**: Docker for consistent deployments
4. **CI/CD**: Jenkins pipeline for automation
5. **Security**: Encryption, authentication, secure configuration
6. **DevOps**: Infrastructure as code, automated deployment

**Key Technologies**: Flask, Docker, Jenkins, AWS (EC2, ECR, DynamoDB, SSM), Python, pytest

---

**Architecture designed for scalability, security, and maintainability.** 🏗️

