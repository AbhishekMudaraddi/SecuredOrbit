# Jenkins CI/CD - Next Steps Checklist

Complete step-by-step guide to finish setting up your Jenkins CI/CD pipeline.

---

## 🎯 Overview

You have:
- ✅ Jenkinsfile created
- ✅ AWS infrastructure ready (ECR, SSM, EC2)
- ✅ Docker image in ECR
- ✅ EC2 instance configured

**Now**: Set up Jenkins to automate builds and deployments.

---

## 📋 Step-by-Step Action Plan

### Phase 1: Jenkins Server Setup (30-45 minutes)

#### Step 1.1: Install Jenkins Server

**Option A: On EC2 Instance (Recommended)**

```bash
# SSH into a new EC2 instance (or use existing)
# Install Jenkins (Ubuntu/Debian)
sudo apt-get update
sudo apt-get install -y openjdk-11-jdk
wget -q -O - https://pkg.jenkins.io/debian-stable/jenkins.io-2023.key | sudo apt-key add -
sudo sh -c 'echo deb http://pkg.jenkins.io/debian-stable binary/ > /etc/apt/sources.list.d/jenkins.list'
sudo apt-get update
sudo apt-get install -y jenkins

# Start Jenkins
sudo systemctl start jenkins
sudo systemctl enable jenkins

# Get initial admin password
sudo cat /var/lib/jenkins/secrets/initialAdminPassword
```

**Option B: On Local Machine**

- Download Jenkins from https://www.jenkins.io/download/
- Follow installation instructions for your OS

#### Step 1.2: Initial Jenkins Configuration

1. **Access Jenkins**: `http://your-jenkins-ip:8080`
2. **Unlock Jenkins**: Enter initial admin password
3. **Install Suggested Plugins**: Click "Install suggested plugins"
4. **Create Admin User**: Set up admin account
5. **Instance Configuration**: Use default URL or customize

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

---

### Phase 3: Install Required Tools on Jenkins Server (15 minutes)

SSH into your Jenkins server and run:

```bash
# Install Python 3.11+
sudo apt-get update
sudo apt-get install -y python3 python3-pip python3-venv

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker jenkins
sudo systemctl restart jenkins

# Install AWS CLI
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# Install Make
sudo apt-get install -y build-essential

# Verify installations
python3 --version
docker --version
aws --version
make --version
```

---

### Phase 4: Configure Credentials (15 minutes)

#### Step 4.1: Configure AWS Credentials

1. Go to: **Jenkins → Manage Jenkins → Credentials → System → Global credentials**
2. Click: **Add Credentials**
3. Select: **AWS Credentials**
4. Fill in:
   - **ID**: `aws-credentials`
   - **Description**: `AWS credentials for ECR push`
   - **Access Key ID**: Your AWS access key
   - **Secret Access Key**: Your AWS secret key
5. Click: **OK**

**Or use IAM Role** (if Jenkins is on EC2):
- Attach IAM role with ECR push permissions (from `aws_bootstrap.sh` Jenkins policy)

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
5. Click: **OK**

**Test SSH connection**:
```bash
# From Jenkins server, test SSH
ssh -i /path/to/key.pem ec2-user@YOUR_EC2_IP
```

---

### Phase 5: Configure SonarQube (Optional - 20 minutes)

**Skip this if you don't want code quality analysis.**

#### Step 5.1: Install SonarQube Server

```bash
# Download SonarQube
wget https://binaries.sonarsource.com/Distribution/sonarqube/sonarqube-9.9.zip
unzip sonarqube-9.9.zip
cd sonarqube-9.9/bin/linux-x86-64
./sonar.sh start
```

Access: `http://your-server:9000` (default login: admin/admin)

#### Step 5.2: Configure SonarQube in Jenkins

1. Go to: **Jenkins → Manage Jenkins → Configure System**
2. Find: **SonarQube servers** section
3. Click: **Add SonarQube**
4. Fill in:
   - **Name**: `sonar-local`
   - **Server URL**: `http://your-sonarqube-server:9000`
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

**Line 8**: Replace `<ACCOUNT_ID>`
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
  - Example: `https://github.com/yourusername/password-manager.git`
- **Credentials**: Add if repository is private
- **Branches to build**: `*/main` or `*/master`
- **Script Path**: `Jenkinsfile`
- **Lightweight checkout**: ❌ Unchecked (needed for full workspace)

**Build Triggers:**
- ✅ **GitHub hook trigger for GITScm polling** (if using GitHub webhooks)

Click: **Save**

---

### Phase 8: Configure IAM Permissions for Jenkins (10 minutes)

Jenkins needs permissions to push to ECR. Use the **Jenkins Role/User Policy** from `aws_bootstrap.sh` output.

**Go to AWS Console → IAM → Users** (or Roles if using IAM role):

1. Find your Jenkins IAM user/role
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

#### Step 10.1: GitHub Webhook

1. Go to: **GitHub → Your Repository → Settings → Webhooks**
2. Click: **Add webhook**
3. Fill in:
   - **Payload URL**: `http://your-jenkins-url/github-webhook/`
   - **Content type**: `application/json`
   - **Events**: Select **Just the push event**
4. Click: **Add webhook**

#### Step 10.2: Jenkins Configuration

1. Go to: **Jenkins → password-manager-pipeline → Configure**
2. Under **Build Triggers**:
   - ✅ **GitHub hook trigger for GITScm polling**
3. Click: **Save**

**Test**: Push a commit to your repository, Jenkins should automatically build.

---

## ✅ Final Checklist

### Jenkins Server
- [ ] Jenkins installed and running
- [ ] Required plugins installed
- [ ] Python 3.11+ installed
- [ ] Docker installed (Jenkins user in docker group)
- [ ] AWS CLI installed
- [ ] Make installed

### Credentials
- [ ] AWS credentials configured (ID: `aws-credentials`)
- [ ] SSH credentials configured (ID: `ec2-ssh`)
- [ ] SonarQube configured (if using)

### Configuration Files
- [ ] Jenkinsfile updated (`<ACCOUNT_ID>` replaced)
- [ ] Jenkinsfile updated (`<EC2_PUBLIC_IP>` replaced)
- [ ] sonar-project.properties created (if using SonarQube)

### Pipeline Job
- [ ] Pipeline job created
- [ ] Git repository configured
- [ ] Script path set to `Jenkinsfile`
- [ ] Build triggers configured

### IAM Permissions
- [ ] Jenkins IAM user/role has ECR push permissions
- [ ] EC2 IAM role has ECR pull permissions

### Testing
- [ ] Manual build successful
- [ ] All stages complete
- [ ] Docker image pushed to ECR
- [ ] Deployment to EC2 works (on main branch)
- [ ] Health check passes
- [ ] Application accessible

### Webhooks (Optional)
- [ ] GitHub webhook configured
- [ ] Automatic builds on push work

---

## 🚀 Quick Start Commands

### Test Pipeline Manually

```bash
# On Jenkins server, test AWS access
aws sts get-caller-identity

# Test Docker
docker ps

# Test SSH to EC2
ssh ec2-user@YOUR_EC2_IP "echo 'SSH works!'"
```

### Verify Pipeline Configuration

```bash
# Check Jenkinsfile syntax
# (Jenkins will validate when you save the job)
```

---

## 🐛 Troubleshooting

### Build Fails at Checkout
- **Check**: Git repository URL is correct
- **Check**: Credentials are set if repo is private
- **Check**: Jenkins has network access to Git repository

### Build Fails at Docker Build
- **Check**: Docker is installed and Jenkins user is in docker group
- **Check**: `sudo systemctl restart jenkins` after adding to docker group
- **Check**: Docker daemon is running

### Build Fails at ECR Push
- **Check**: AWS credentials are correct
- **Check**: IAM permissions include ECR push actions
- **Check**: ECR repository exists in correct region

### Deployment Fails
- **Check**: SSH credentials are correct
- **Check**: EC2 security group allows SSH from Jenkins IP
- **Check**: EC2 has correct IAM role attached
- **Check**: `/opt/password-manager/fetch-env.sh` exists and is executable

### Health Check Fails
- **Check**: Application logs: `docker compose logs` on EC2
- **Check**: Port 80 is accessible
- **Check**: Security group allows HTTP traffic

---

## 📊 Expected Timeline

- **Phase 1-3**: 1 hour (Jenkins setup + plugins + tools)
- **Phase 4**: 15 minutes (Credentials)
- **Phase 5**: 20 minutes (SonarQube - optional)
- **Phase 6**: 5 minutes (Update Jenkinsfile)
- **Phase 7**: 10 minutes (Create pipeline job)
- **Phase 8**: 10 minutes (IAM permissions)
- **Phase 9**: 15 minutes (Test pipeline)
- **Phase 10**: 10 minutes (Webhooks - optional)

**Total**: ~2.5 hours (without SonarQube) or ~3 hours (with SonarQube)

---

## 🎯 Success Criteria

Your CI/CD is complete when:
1. ✅ Push to repository triggers automatic build
2. ✅ Tests run automatically
3. ✅ Docker image builds and pushes to ECR
4. ✅ Deployment to EC2 happens automatically (on main branch)
5. ✅ Health checks verify deployment success
6. ✅ Application is accessible after deployment

---

## 📚 Reference Documents

- **Jenkinsfile**: `/Jenkinsfile` - Pipeline definition
- **Setup Guide**: `/JENKINS_SETUP.md` - Detailed setup instructions
- **CI/CD Plan**: `/CI_CD_PLAN.md` - Overview and checklist

---

**Follow these steps in order, and you'll have a complete CI/CD pipeline!** 🚀

Start with **Phase 1** and work through each phase systematically.

