# Local Jenkins CI/CD Setup Guide

Complete guide for setting up Jenkins CI/CD pipeline using **Jenkins running on your local PC**.

---

## 🎯 Overview

You have:
- ✅ Jenkins running locally on port 8080
- ✅ AWS infrastructure ready (ECR, SSM, EC2)
- ✅ Docker image in ECR
- ✅ EC2 instance configured

**Now**: Configure local Jenkins to automate builds and deployments.

---

## 📋 Step-by-Step Setup

### Phase 1: Verify Local Jenkins (5 minutes)

#### Step 1.1: Access Jenkins

1. Open browser: `http://localhost:8080`
2. Verify Jenkins is running
3. Complete initial setup if not done:
   - Unlock with initial admin password
   - Install suggested plugins
   - Create admin user

#### Step 1.2: Check Jenkins Version

Go to: **Jenkins → Manage Jenkins → About Jenkins**

Note your Jenkins version (should be 2.400+ for best compatibility).

---

### Phase 2: Install Required Plugins (10 minutes)

Go to: **Jenkins → Manage Jenkins → Manage Plugins → Available**

Install these plugins:
- ✅ **Pipeline** (usually pre-installed)
- ✅ **Docker Pipeline**
- ✅ **SSH Agent Plugin**
- ✅ **JUnit Plugin**
- ✅ **HTML Publisher Plugin**
- ✅ **SonarQube Scanner** (optional - for code quality)
- ✅ **GitHub Plugin** (if using GitHub)
- ✅ **AWS Steps** (optional - for better AWS integration)

**After installing**: Restart Jenkins if prompted.

**To restart**: Go to **Jenkins → Manage Jenkins → Restart Jenkins**

---

### Phase 3: Install Required Tools on Local Machine (15 minutes)

#### Step 3.1: Verify Python

```bash
# Check Python version (need 3.11+)
python3 --version

# If not installed (macOS)
brew install python@3.11

# If not installed (Linux)
sudo apt-get install python3 python3-pip python3-venv
```

#### Step 3.2: Verify Docker

```bash
# Check Docker
docker --version

# If not installed (macOS)
brew install docker

# If not installed (Linux)
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Start Docker Desktop (macOS) or Docker service (Linux)
```

#### Step 3.3: Verify AWS CLI

```bash
# Check AWS CLI
aws --version

# If not installed (macOS)
brew install awscli

# If not installed (Linux)
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# Configure AWS credentials
aws configure
```

#### Step 3.4: Verify Make

```bash
# Check Make
make --version

# If not installed (macOS)
xcode-select --install

# If not installed (Linux)
sudo apt-get install build-essential
```

#### Step 3.5: Verify Git

```bash
# Check Git
git --version

# If not installed (macOS)
brew install git

# If not installed (Linux)
sudo apt-get install git
```

---

### Phase 4: Configure Credentials (15 minutes)

#### Step 4.1: Configure AWS Credentials

**Option A: Use AWS CLI Configuration (Recommended)**

If you've run `aws configure`, Jenkins can use those credentials automatically. But for explicit configuration:

1. Go to: **Jenkins → Manage Jenkins → Credentials → System → Global credentials**
2. Click: **Add Credentials**
3. Select: **AWS Credentials**
4. Fill in:
   - **ID**: `aws-credentials`
   - **Description**: `AWS credentials for ECR push`
   - **Access Key ID**: Your AWS access key
   - **Secret Access Key**: Your AWS secret key
5. Click: **OK**

**Option B: Use Environment Variables**

Jenkins can also use AWS credentials from environment variables:
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `AWS_DEFAULT_REGION`

#### Step 4.2: Configure SSH Credentials for EC2

1. Go to: **Jenkins → Manage Jenkins → Credentials → System → Global credentials**
2. Click: **Add Credentials**
3. Select: **SSH Username with private key**
4. Fill in:
   - **ID**: `ec2-ssh`
   - **Description**: `SSH key for EC2 deployment`
   - **Username**: `ec2-user` (or `ubuntu` depending on your EC2 AMI)
   - **Private Key**: 
     - Select **Enter directly**
     - Paste your EC2 private key (.pem file content)
     - Or select **From the Jenkins master ~/.ssh** if key is already there
5. Click: **OK**

**Test SSH connection**:
```bash
# From your local machine, test SSH
ssh -i /path/to/key.pem ec2-user@YOUR_EC2_IP
```

---

### Phase 5: Configure SonarQube (Optional - 20 minutes)

**Skip this if you don't want code quality analysis.**

#### Step 5.1: Install SonarQube Server Locally

**macOS**:
```bash
brew install sonarqube
brew services start sonarqube
```

**Linux**:
```bash
wget https://binaries.sonarsource.com/Distribution/sonarqube/sonarqube-9.9.zip
unzip sonarqube-9.9.zip
cd sonarqube-9.9/bin/linux-x86-64
./sonar.sh start
```

Access: `http://localhost:9000` (default login: admin/admin)

#### Step 5.2: Configure SonarQube in Jenkins

1. Go to: **Jenkins → Manage Jenkins → Configure System**
2. Find: **SonarQube servers** section
3. Click: **Add SonarQube**
4. Fill in:
   - **Name**: `sonar-local`
   - **Server URL**: `http://localhost:9000`
   - **Server authentication token**: Generate token in SonarQube
5. Click: **Save**

#### Step 5.3: Create sonar-project.properties

Create file in your repo root:

```bash
cd /Users/abhishekmudaraddi/Final
cat > sonar-project.properties <<EOF
sonar.projectKey=password-manager
sonar.projectName=Password Manager
sonar.projectVersion=1.0
sonar.sources=.
sonar.exclusions=**/venv/**,**/__pycache__/**,**/tests/**,**/*.pyc,**/static/**,**/templates/**
sonar.python.version=3.11
sonar.sourceEncoding=UTF-8
sonar.python.coverage.reportPaths=coverage.xml
EOF
```

---

### Phase 6: Update Jenkinsfile (5 minutes)

Edit `/Users/abhishekmudaraddi/Final/Jenkinsfile`:

**Line 11**: Replace `<ACCOUNT_ID>`
```groovy
ACCOUNT_ID = '503561414328'  // Your AWS Account ID
```

**Line 95**: Replace `<EC2_PUBLIC_IP>`
```groovy
def EC2_HOST = '54.198.152.202'  // Your EC2 instance public IP
```

**Verify other values**:
- `AWS_REGION = 'us-east-1'` ✅ (should be correct)
- `APP_NAME = 'password-manager'` ✅ (should be correct)

---

### Phase 7: Create Jenkins Pipeline Job (10 minutes)

#### Step 7.1: Create New Pipeline

1. Go to: **Jenkins → New Item**
2. Enter name: `password-manager-pipeline`
3. Select: **Pipeline**
4. Click: **OK**

#### Step 7.2: Configure Pipeline

**General Settings:**
- ✅ **Description**: "CI/CD Pipeline for Password Manager"
- ✅ **GitHub project** (if using GitHub): Add your repo URL

**Pipeline Configuration:**
- **Definition**: **Pipeline script from SCM**
- **SCM**: **Git**
- **Repository URL**: Your Git repository URL
  - **For local repo**: Use `file:///Users/abhishekmudaraddi/Final` (note: file:// protocol)
  - **For remote repo**: `https://github.com/yourusername/password-manager.git`
  - **Note**: For local repos, Jenkins may need file system access permissions
- **Credentials**: Add if repository is private
- **Branches to build**: `*/main` or `*/master`
- **Script Path**: `Jenkinsfile`
- **Lightweight checkout**: ❌ Unchecked (needed for full workspace)

**Build Triggers:**
- ✅ **Poll SCM**: `H/5 * * * *` (check every 5 minutes)
- ✅ **GitHub hook trigger** (if using GitHub webhooks)

Click: **Save**

---

### Phase 8: Configure IAM Permissions for Jenkins (10 minutes)

Jenkins needs permissions to push to ECR. Use the **Jenkins Role/User Policy** from `aws_bootstrap.sh` output.

**Go to AWS Console → IAM → Users**:

1. Find your AWS IAM user (the one Jenkins will use)
2. Attach policy with this JSON:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "ECRAuthorization",
      "Effect": "Allow",
      "Action": ["ecr:GetAuthorizationToken"],
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
      "Resource": "arn:aws:ecr:us-east-1:503561414328:repository/password-manager"
    }
  ]
}
```

---

### Phase 9: Test the Pipeline (15 minutes)

#### Step 9.1: Run Manual Build

1. Go to: **Jenkins → password-manager-pipeline**
2. Click: **Build Now**
3. Watch: **Console Output**

#### Step 9.2: Verify Each Stage

Check that each stage completes:
- ✅ **Checkout**: Code downloaded
- ✅ **Setup Python**: Virtual environment created
- ✅ **Lint & Tests**: Tests pass
- ✅ **SonarQube**: Analysis completes (if configured)
- ✅ **Docker Build & Push**: Image built and pushed to ECR
- ✅ **Deploy to EC2**: Only runs on main branch

#### Step 9.3: Check Deployment

After build completes:
```bash
# SSH to EC2
ssh ec2-user@YOUR_EC2_IP

# Check container
cd /opt/password-manager
docker compose ps

# Check logs
docker compose logs -f

# Test health
curl http://localhost/health
```

---

### Phase 10: Configure Webhooks (Optional - 10 minutes)

#### Step 10.1: Expose Jenkins to Internet (for webhooks)

**Option A: Use ngrok (Easiest for testing)**

```bash
# Install ngrok
brew install ngrok  # macOS
# or download from https://ngrok.com/

# Expose Jenkins
ngrok http 8080

# Copy the ngrok URL (e.g., https://abc123.ngrok.io)
```

**Option B: Use Port Forwarding**

If your local machine has a public IP, configure port forwarding on your router.

#### Step 10.2: GitHub Webhook

1. Go to: **GitHub → Your Repository → Settings → Webhooks**
2. Click: **Add webhook**
3. Fill in:
   - **Payload URL**: `http://your-public-url/github-webhook/`
   - **Content type**: `application/json`
   - **Events**: Select **Just the push event**
4. Click: **Add webhook**

#### Step 10.3: Jenkins Configuration

1. Go to: **Jenkins → password-manager-pipeline → Configure**
2. Under **Build Triggers**:
   - ✅ **GitHub hook trigger for GITScm polling**
3. Click: **Save**

**Test**: Push a commit to your repository, Jenkins should automatically build.

---

## 🔧 Local Jenkins Specific Considerations

### Docker on macOS

If using Docker Desktop on macOS:
- ✅ Docker Desktop must be running
- ✅ Jenkins needs access to Docker socket
- ✅ May need to add Jenkins user to docker group (if Jenkins runs as different user)

### File Paths

When using local file paths in Jenkinsfile:
- Use absolute paths: `/Users/abhishekmudaraddi/Final`
- Or use Jenkins workspace variable: `${WORKSPACE}`

### Network Access

Ensure your local machine can:
- ✅ Access AWS services (ECR, SSM)
- ✅ SSH to EC2 instance
- ✅ Access Git repository (if remote)

---

## ✅ Final Checklist

### Local Machine Setup
- [ ] Jenkins running on port 8080
- [ ] Python 3.11+ installed
- [ ] Docker installed and running
- [ ] AWS CLI installed and configured
- [ ] Make installed
- [ ] Git installed

### Jenkins Configuration
- [ ] Required plugins installed
- [ ] AWS credentials configured
- [ ] SSH credentials configured
- [ ] SonarQube configured (if using)

### Configuration Files
- [ ] Jenkinsfile updated (`<ACCOUNT_ID>` replaced)
- [ ] Jenkinsfile updated (`<EC2_PUBLIC_IP>` replaced)
- [ ] sonar-project.properties created (if using SonarQube)

### Pipeline Job
- [ ] Pipeline job created
- [ ] Git repository configured (local or remote)
- [ ] Script path set to `Jenkinsfile`
- [ ] Build triggers configured

### IAM Permissions
- [ ] AWS IAM user has ECR push permissions
- [ ] EC2 IAM role has ECR pull permissions

### Testing
- [ ] Manual build successful
- [ ] All stages complete
- [ ] Docker image pushed to ECR
- [ ] Deployment to EC2 works (on main branch)
- [ ] Health check passes
- [ ] Application accessible

---

## 🚀 Quick Start Commands

### Verify Local Setup

```bash
# Check all tools
python3 --version
docker --version
aws --version
make --version
git --version

# Test AWS access
aws sts get-caller-identity

# Test Docker
docker ps

# Test SSH to EC2
ssh ec2-user@YOUR_EC2_IP "echo 'SSH works!'"
```

### Test Pipeline Manually

1. Go to Jenkins: `http://localhost:8080`
2. Click: **password-manager-pipeline → Build Now**
3. Watch console output

---

## 🐛 Troubleshooting

### Jenkins Can't Access Docker

**macOS**:
```bash
# If Jenkins runs as different user, add to docker group
sudo dseditgroup -o edit -a jenkins -t user _docker

# Or run Jenkins with Docker Desktop running
# Docker Desktop exposes Docker socket automatically
```

**Linux**:
```bash
sudo usermod -aG docker jenkins
sudo systemctl restart jenkins
```

### AWS Credentials Not Found

**Solution**: Configure AWS credentials in Jenkins credentials store, or ensure `aws configure` is set up for the user running Jenkins.

### SSH Connection Fails

**Check**:
- EC2 security group allows SSH from your IP
- SSH key is correct
- EC2 instance is running
- Test manually: `ssh -i key.pem ec2-user@EC2_IP`

### Docker Build Fails

**Check**:
- Docker Desktop is running (macOS)
- Docker daemon is running (Linux)
- Jenkins has permission to use Docker
- Test manually: `docker ps`

---

## 📊 Expected Timeline

- **Phase 1**: 5 minutes (Verify Jenkins)
- **Phase 2**: 10 minutes (Install Plugins)
- **Phase 3**: 15 minutes (Install Tools)
- **Phase 4**: 15 minutes (Configure Credentials)
- **Phase 5**: 20 minutes (SonarQube - optional)
- **Phase 6**: 5 minutes (Update Jenkinsfile)
- **Phase 7**: 10 minutes (Create Pipeline Job)
- **Phase 8**: 10 minutes (IAM Permissions)
- **Phase 9**: 15 minutes (Test Pipeline)
- **Phase 10**: 10 minutes (Webhooks - optional)

**Total**: ~2.5 hours (without SonarQube) or ~3 hours (with SonarQube)

---

## 🎯 Success Criteria

Your CI/CD is complete when:
1. ✅ Push to repository triggers automatic build (or manual build works)
2. ✅ Tests run automatically
3. ✅ Docker image builds and pushes to ECR
4. ✅ Deployment to EC2 happens automatically (on main branch)
5. ✅ Health checks verify deployment success
6. ✅ Application is accessible after deployment

---

**You're all set! Follow these steps to configure your local Jenkins for CI/CD.** 🚀

