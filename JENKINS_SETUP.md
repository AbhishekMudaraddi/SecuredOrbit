# Jenkins CI/CD Setup Guide

Complete guide for setting up Jenkins CI/CD pipeline for Password Manager.

---

## 📋 Prerequisites

- Jenkins server installed and running
- AWS Account with appropriate permissions
- EC2 instance already deployed
- Git repository (GitHub, GitLab, Bitbucket, etc.)

---

## 🚀 Step-by-Step Setup

### Step 1: Install Required Jenkins Plugins

Go to **Jenkins → Manage Jenkins → Manage Plugins → Available**

Install these plugins:
- ✅ **Pipeline** (usually pre-installed)
- ✅ **Docker Pipeline**
- ✅ **SSH Agent Plugin**
- ✅ **JUnit Plugin**
- ✅ **HTML Publisher Plugin** (for coverage reports)
- ✅ **SonarQube Scanner** (if using SonarQube)
- ✅ **AWS Steps** (optional, for better AWS integration)

After installing, restart Jenkins.

---

### Step 2: Configure AWS Credentials in Jenkins

**Option A: AWS Credentials (Recommended)**

1. Go to **Jenkins → Manage Jenkins → Credentials → System → Global credentials**
2. Click **Add Credentials**
3. Select **AWS Credentials**
4. Fill in:
   - **ID**: `aws-credentials` (or any name)
   - **Access Key ID**: Your AWS access key
   - **Secret Access Key**: Your AWS secret key
5. Click **OK**

**Option B: IAM Role (If Jenkins is on EC2)**

If Jenkins is running on EC2, attach an IAM role with:
- ECR push permissions (from `aws_bootstrap.sh` Jenkins policy)
- EC2 describe permissions
- DynamoDB access (if needed)

---

### Step 3: Configure SSH Credentials for EC2

1. Go to **Jenkins → Manage Jenkins → Credentials → System → Global credentials**
2. Click **Add Credentials**
3. Select **SSH Username with private key**
4. Fill in:
   - **ID**: `ec2-ssh`
   - **Username**: `ec2-user` (or `ubuntu` depending on your EC2 AMI)
   - **Private Key**: Paste your EC2 private key (`.pem` file content)
5. Click **OK**

---

### Step 4: Configure SonarQube (Optional)

If you want SonarQube analysis:

1. **Install SonarQube Server** (separate from Jenkins)
2. Go to **Jenkins → Manage Jenkins → Configure System**
3. Find **SonarQube servers** section
4. Add:
   - **Name**: `sonar-local`
   - **Server URL**: `http://your-sonarqube-server:9000`
   - **Server authentication token**: Your SonarQube token
5. Save

**Create `sonar-project.properties`** in your repo root:

```properties
sonar.projectKey=password-manager
sonar.projectName=Password Manager
sonar.projectVersion=1.0
sonar.sources=.
sonar.exclusions=**/venv/**,**/__pycache__/**,**/tests/**,**/*.pyc
sonar.python.version=3.11
sonar.sourceEncoding=UTF-8
```

---

### Step 5: Update Jenkinsfile

Edit `Jenkinsfile` and replace placeholders:

1. **Replace `<ACCOUNT_ID>`**:
   ```groovy
   ACCOUNT_ID = '503561414328'  // Your AWS Account ID
   ```

2. **Replace `<EC2_PUBLIC_IP>`**:
   ```groovy
   def EC2_HOST = '54.198.152.202'  // Your EC2 public IP
   ```

3. **Verify AWS_REGION**:
   ```groovy
   AWS_REGION = 'us-east-1'  // Should match your setup
   ```

---

### Step 6: Create Jenkins Pipeline Job

1. Go to **Jenkins → New Item**
2. Enter name: `password-manager-pipeline`
3. Select **Pipeline**
4. Click **OK**

**Configure Pipeline:**

- **Definition**: Pipeline script from SCM
- **SCM**: Git
- **Repository URL**: Your Git repository URL
- **Credentials**: Add if repository is private
- **Branches to build**: `*/main` or `*/master`
- **Script Path**: `Jenkinsfile`
- **Lightweight checkout**: Unchecked (if you need full workspace)

Click **Save**

---

### Step 7: Configure IAM Permissions for Jenkins

Jenkins needs permissions to push to ECR. Use the **Jenkins Role/User Policy** from `aws_bootstrap.sh` output:

**Attach to Jenkins IAM User/Role:**

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

### Step 8: Install Required Tools on Jenkins Server

**Python 3.11+**:
```bash
# On Jenkins server
sudo apt-get update
sudo apt-get install -y python3 python3-pip python3-venv
```

**Docker**:
```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker jenkins
sudo systemctl restart jenkins
```

**AWS CLI**:
```bash
# Install AWS CLI
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install
```

**Make** (for Makefile):
```bash
sudo apt-get install -y build-essential
```

**Docker Compose** (if needed):
```bash
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-linux-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

---

### Step 9: Test the Pipeline

1. Go to your pipeline job in Jenkins
2. Click **Build Now**
3. Watch the build progress
4. Check console output for any errors

---

## 🔧 Troubleshooting

### Error: AWS credentials not found
- **Solution**: Configure AWS credentials in Jenkins credentials store

### Error: Cannot connect to EC2 via SSH
- **Solution**: 
  - Verify SSH credentials are correct
  - Check security group allows Jenkins IP
  - Test SSH manually: `ssh ec2-user@YOUR_EC2_IP`

### Error: Docker permission denied
- **Solution**: Add Jenkins user to docker group:
  ```bash
  sudo usermod -aG docker jenkins
  sudo systemctl restart jenkins
  ```

### Error: ECR push fails
- **Solution**: 
  - Verify IAM permissions include ECR push actions
  - Check AWS credentials are correct
  - Verify ECR repository exists

### Error: Health check fails
- **Solution**:
  - Check application logs: `docker compose logs` on EC2
  - Verify port 80 is accessible
  - Check security group allows HTTP traffic

---

## 📊 Pipeline Stages Explained

1. **Checkout**: Gets code from Git repository
2. **Setup Python**: Creates virtual environment and installs dependencies
3. **Lint & Tests**: Runs flake8 (if available) and pytest
4. **SonarQube**: Code quality analysis (if configured)
5. **Quality Gate**: Waits for SonarQube quality gate
6. **Docker Build & Push**: Builds and pushes image to ECR
7. **Deploy to EC2**: Only on main/master branch, deploys to EC2 with health checks

---

## 🎯 Next Steps After Setup

1. **Test Pipeline**: Run a test build
2. **Configure Webhooks**: Set up Git webhooks to trigger builds automatically
3. **Set up Notifications**: Configure email/Slack notifications for build results
4. **Monitor**: Set up monitoring and alerts for deployments

---

## 📝 Quick Reference

**Jenkinsfile Location**: `/Jenkinsfile` (repo root)

**Key Placeholders to Replace**:
- `<ACCOUNT_ID>` → Your AWS Account ID
- `<EC2_PUBLIC_IP>` → Your EC2 instance public IP

**Credentials Needed**:
- AWS Credentials (ID: `aws-credentials`)
- SSH Credentials (ID: `ec2-ssh`)

**Pipeline Triggers**:
- Manual: Click "Build Now"
- Automatic: Push to main/master branch (if webhook configured)

---

## ✅ Checklist

- [ ] Jenkins plugins installed
- [ ] AWS credentials configured
- [ ] SSH credentials configured
- [ ] SonarQube configured (optional)
- [ ] Jenkinsfile updated with correct values
- [ ] Pipeline job created
- [ ] IAM permissions configured
- [ ] Required tools installed on Jenkins server
- [ ] Test build successful
- [ ] Webhooks configured (optional)

---

**Setup Complete!** 🎉

Your CI/CD pipeline is ready to automatically build, test, and deploy your Password Manager application.

