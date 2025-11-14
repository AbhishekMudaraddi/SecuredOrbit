# CI/CD Setup Plan - Jenkins Pipeline

## 📋 Overview

This document outlines the complete plan for setting up Jenkins CI/CD pipeline for the Password Manager application.

---

## 🎯 Goals

1. **Automated Testing**: Run tests on every commit
2. **Code Quality**: SonarQube analysis (optional)
3. **Automated Build**: Build Docker images automatically
4. **Automated Deployment**: Deploy to EC2 on main branch
5. **Health Checks**: Verify deployment success
6. **Rollback**: Automatic rollback on failure

---

## 📁 Files Created

### 1. Jenkinsfile ✅
- **Location**: `/Jenkinsfile` (repo root)
- **Purpose**: Declarative Jenkins pipeline definition
- **Status**: ✅ Created with all required stages

### 2. JENKINS_SETUP.md ✅
- **Location**: `/JENKINS_SETUP.md`
- **Purpose**: Complete setup guide for Jenkins
- **Status**: ✅ Created with step-by-step instructions

---

## 🔧 What Needs to Be Done

### Phase 1: Jenkins Server Setup

#### 1.1 Install Jenkins
- [ ] Install Jenkins server (Ubuntu/Debian/Amazon Linux)
- [ ] Configure Jenkins on port 8080 (or custom)
- [ ] Complete initial setup wizard
- [ ] Install recommended plugins

#### 1.2 Install Required Plugins
- [ ] Pipeline plugin
- [ ] Docker Pipeline plugin
- [ ] SSH Agent Plugin
- [ ] JUnit Plugin
- [ ] HTML Publisher Plugin
- [ ] SonarQube Scanner (optional)
- [ ] AWS Steps (optional)

#### 1.3 Install Required Tools on Jenkins Server
- [ ] Python 3.11+
- [ ] Docker
- [ ] AWS CLI
- [ ] Make
- [ ] Git

---

### Phase 2: Configure Credentials

#### 2.1 AWS Credentials
- [ ] Create AWS IAM user for Jenkins (or use existing)
- [ ] Generate access keys
- [ ] Add credentials to Jenkins (ID: `aws-credentials`)
- [ ] Attach Jenkins IAM policy (ECR push permissions)

#### 2.2 SSH Credentials
- [ ] Get EC2 private key (.pem file)
- [ ] Add SSH credentials to Jenkins (ID: `ec2-ssh`)
- [ ] Test SSH connection manually

#### 2.3 SonarQube (Optional)
- [ ] Install SonarQube server
- [ ] Configure SonarQube in Jenkins
- [ ] Create `sonar-project.properties` file
- [ ] Generate SonarQube token

---

### Phase 3: Update Configuration Files

#### 3.1 Update Jenkinsfile
- [ ] Replace `<ACCOUNT_ID>` with actual AWS Account ID
- [ ] Replace `<EC2_PUBLIC_IP>` with EC2 instance IP
- [ ] Verify `AWS_REGION` is correct (`us-east-1`)
- [ ] Verify `APP_NAME` is correct (`password-manager`)

#### 3.2 Create sonar-project.properties (Optional)
- [ ] Create file in repo root
- [ ] Configure SonarQube project settings

---

### Phase 4: Create Jenkins Pipeline Job

#### 4.1 Create Pipeline
- [ ] Create new Pipeline job in Jenkins
- [ ] Configure Git repository URL
- [ ] Set branch to build (`main` or `master`)
- [ ] Set script path to `Jenkinsfile`
- [ ] Save configuration

#### 4.2 Test Pipeline
- [ ] Run manual build
- [ ] Check console output
- [ ] Verify all stages complete successfully
- [ ] Fix any errors

---

### Phase 5: Configure Webhooks (Optional)

#### 5.1 GitHub/GitLab Webhook
- [ ] Go to repository settings
- [ ] Add webhook URL: `http://your-jenkins-url/github-webhook/`
- [ ] Set trigger: Push events
- [ ] Test webhook

#### 5.2 Jenkins Configuration
- [ ] Enable "GitHub hook trigger for GITScm polling"
- [ ] Test automatic builds

---

## 📊 Pipeline Flow

```
┌─────────────┐
│   Checkout  │ ← Git repository
└──────┬──────┘
       │
┌──────▼──────────┐
│  Setup Python   │ ← Create venv, install deps
└──────┬──────────┘
       │
┌──────▼──────────┐
│ Lint & Tests    │ ← Run flake8, pytest
└──────┬──────────┘
       │
┌──────▼──────────┐
│  SonarQube      │ ← Code quality (optional)
└──────┬──────────┘
       │
┌──────▼──────────┐
│ Quality Gate    │ ← Wait for SonarQube
└──────┬──────────┘
       │
┌──────▼──────────────┐
│ Docker Build & Push │ ← Build & push to ECR
└──────┬──────────────┘
       │
┌──────▼──────────┐
│ Deploy to EC2   │ ← Only on main branch
└─────────────────┘
```

---

## 🔐 Security Checklist

- [ ] AWS credentials stored securely in Jenkins
- [ ] SSH keys stored securely in Jenkins
- [ ] IAM user has minimum required permissions
- [ ] EC2 security group restricts SSH access
- [ ] Jenkins server is secured (HTTPS, authentication)
- [ ] Webhooks use secure URLs (HTTPS)

---

## 🧪 Testing Checklist

- [ ] Test build on feature branch (should not deploy)
- [ ] Test build on main branch (should deploy)
- [ ] Verify tests run correctly
- [ ] Verify Docker image builds correctly
- [ ] Verify image pushes to ECR
- [ ] Verify deployment to EC2 works
- [ ] Verify health check passes
- [ ] Test rollback on health check failure

---

## 📝 Configuration Values

### Required Updates in Jenkinsfile

```groovy
// Line 8: Replace with your AWS Account ID
ACCOUNT_ID = '503561414328'  // ← UPDATE THIS

// Line 95: Replace with your EC2 public IP
def EC2_HOST = '54.198.152.202'  // ← UPDATE THIS
```

### Credential IDs

- **AWS Credentials**: `aws-credentials`
- **SSH Credentials**: `ec2-ssh`
- **SonarQube**: `sonar-local`

---

## 🚀 Quick Start Commands

### On Jenkins Server

```bash
# Install Jenkins (Ubuntu)
wget -q -O - https://pkg.jenkins.io/debian-stable/jenkins.io-2023.key | sudo apt-key add -
sudo sh -c 'echo deb http://pkg.jenkins.io/debian-stable binary/ > /etc/apt/sources.list.d/jenkins.list'
sudo apt-get update
sudo apt-get install jenkins

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker jenkins

# Install AWS CLI
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# Restart Jenkins
sudo systemctl restart jenkins
```

---

## 📚 Documentation References

- **Jenkinsfile**: `/Jenkinsfile` - Pipeline definition
- **Setup Guide**: `/JENKINS_SETUP.md` - Detailed setup instructions
- **AWS Bootstrap**: `/infra/aws_bootstrap.sh` - AWS resources setup
- **EC2 Deployment**: `/infra/EC2_DEPLOYMENT.md` - EC2 setup guide

---

## ✅ Success Criteria

Pipeline is successful when:
1. ✅ Code checkout works
2. ✅ Tests pass
3. ✅ Docker image builds
4. ✅ Image pushes to ECR
5. ✅ Deployment to EC2 succeeds
6. ✅ Health check passes
7. ✅ Application is accessible

---

## 🎯 Next Steps

1. **Follow JENKINS_SETUP.md** for detailed setup instructions
2. **Update Jenkinsfile** with your specific values
3. **Create pipeline job** in Jenkins
4. **Test the pipeline** with a test build
5. **Configure webhooks** for automatic builds

---

**Ready to set up Jenkins CI/CD!** 🚀

Follow the steps in `JENKINS_SETUP.md` to get started.

