# EC2 Deployment Guide - Password Manager

Complete guide for deploying Password Manager on AWS EC2.

---

## 📋 Prerequisites

- AWS Account with EC2 access
- EC2 instance running (Ubuntu 20.04+, Amazon Linux 2, or Debian)
- IAM role with permissions (created via `aws_bootstrap.sh`)
- ECR repository created (via `aws_bootstrap.sh`)
- SSM parameters created (via `aws_bootstrap.sh`)

---

## 🚀 Step-by-Step Deployment

### Step 1: Launch EC2 Instance

1. **Launch EC2 Instance**
   - AMI: Ubuntu Server 22.04 LTS (or Amazon Linux 2)
   - Instance Type: t3.small or larger (recommended: t3.medium)
   - Storage: 20 GB minimum
   - Security Group: Create new (we'll configure later)

2. **Key Pair**: Create or select an existing key pair for SSH access

3. **Launch Instance**

---

### Step 2: Configure Security Group

**Inbound Rules:**
- **HTTP (Port 80)**: `0.0.0.0/0` (or restrict to your IP/load balancer)
- **HTTPS (Port 443)**: `0.0.0.0/0` (if using TLS/SSL)
- **SSH (Port 22)**: `YOUR_IP/32` (restrict to your IP only)

**Outbound Rules:**
- Allow all (default)

**Steps:**
1. Go to EC2 → Security Groups
2. Select your instance's security group
3. Edit Inbound Rules
4. Add rules as above
5. Save

---

### Step 3: Attach IAM Role to EC2 Instance

**Important**: The EC2 instance needs an IAM role with permissions to:
- Pull images from ECR
- Access DynamoDB tables
- Read SSM parameters

#### Option A: Create New IAM Role (Recommended)

1. **Go to IAM Console** → Roles → Create Role

2. **Select Trusted Entity**: AWS Service → EC2

3. **Attach Policies**: Create a custom policy using the **EC2 Role Policy** from `aws_bootstrap.sh` output

   The policy should include:
   ```json
   {
     "Version": "2012-10-17",
     "Statement": [
       {
         "Sid": "ECRAccess",
         "Effect": "Allow",
         "Action": ["ecr:GetAuthorizationToken"],
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
         "Resource": "arn:aws:ecr:REGION:ACCOUNT_ID:repository/password-manager"
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
           "arn:aws:dynamodb:REGION:ACCOUNT_ID:table/PasswordManager-Accounts",
           "arn:aws:dynamodb:REGION:ACCOUNT_ID:table/PasswordManager-Users",
           "arn:aws:dynamodb:REGION:ACCOUNT_ID:table/PasswordManager-Passwords"
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
         "Resource": "arn:aws:ssm:REGION:ACCOUNT_ID:parameter/password-manager/*"
       }
     ]
   }
   ```

4. **Name the Role**: `PasswordManagerEC2Role`

5. **Attach Role to Instance**:
   - Go to EC2 → Instances
   - Select your instance → Actions → Security → Modify IAM role
   - Select `PasswordManagerEC2Role`
   - Update IAM role

#### Option B: Use Existing Role

If you already have a role, attach it and ensure it has the above permissions.

---

### Step 4: SSH into EC2 Instance

```bash
# Replace with your key and instance details
ssh -i /path/to/your-key.pem ubuntu@YOUR_EC2_PUBLIC_IP

# Or for Amazon Linux:
ssh -i /path/to/your-key.pem ec2-user@YOUR_EC2_PUBLIC_IP
```

---

### Step 5: Install Docker, Docker Compose, and AWS CLI

**Option A: Use the automated script (Recommended)**

```bash
# Download the setup script
curl -o ec2_setup.sh https://raw.githubusercontent.com/YOUR_REPO/infra/ec2_setup.sh
# OR copy it manually via SCP:
# scp infra/ec2_setup.sh ubuntu@YOUR_EC2_IP:/tmp/

# Make executable and run
chmod +x ec2_setup.sh
sudo ./ec2_setup.sh
```

**Option B: Manual installation**

```bash
# Update system
sudo apt-get update -y  # Ubuntu/Debian
# OR
sudo yum update -y     # Amazon Linux

# Install Docker (Ubuntu/Debian)
sudo apt-get install -y docker.io docker-compose-plugin
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker $USER

# Install AWS CLI (Ubuntu/Debian)
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# Logout and login again for docker group to take effect
```

**Verify installations:**
```bash
docker --version
docker compose version
aws --version
```

---

### Step 6: Create Application Directory

```bash
# Create directory
sudo mkdir -p /opt/password-manager
sudo chown $USER:$USER /opt/password-manager
cd /opt/password-manager
```

---

### Step 7: Copy Files to EC2

**Option A: Using SCP (from your local machine)**

```bash
# Copy fetch-env.sh
scp -i /path/to/your-key.pem infra/fetch-env.sh ubuntu@YOUR_EC2_IP:/opt/password-manager/

# Copy docker-compose.ec2.yml
scp -i /path/to/your-key.pem infra/docker-compose.ec2.yml ubuntu@YOUR_EC2_IP:/opt/password-manager/docker-compose.yml
```

**Option B: Download from GitHub**

```bash
cd /opt/password-manager

# Download files
curl -o fetch-env.sh https://raw.githubusercontent.com/YOUR_REPO/infra/fetch-env.sh
curl -o docker-compose.yml https://raw.githubusercontent.com/YOUR_REPO/infra/docker-compose.ec2.yml

# Make executable
chmod +x fetch-env.sh
```

**Option C: Create files manually**

Copy the contents of `infra/fetch-env.sh` and `infra/docker-compose.ec2.yml` to the EC2 instance.

---

### Step 8: Fetch Environment Variables from SSM

```bash
cd /opt/password-manager

# Run fetch-env.sh to pull SSM parameters
./fetch-env.sh
```

This will:
- Connect to SSM Parameter Store
- Fetch all parameters under `/password-manager/`
- Create a `.env` file with all configuration

**Verify:**
```bash
cat .env
# Should show SESSION_SECRET, PORT, AWS_REGION, DYNAMODB_*_TABLE
```

---

### Step 9: Update docker-compose.yml with ECR Image

Edit `docker-compose.yml` and replace the image placeholder:

```bash
cd /opt/password-manager
nano docker-compose.yml
```

Update the image line:
```yaml
image: YOUR_ACCOUNT_ID.dkr.ecr.YOUR_REGION.amazonaws.com/password-manager:latest
```

Or set it via environment variable:
```bash
export ECR_IMAGE="YOUR_ACCOUNT_ID.dkr.ecr.YOUR_REGION.amazonaws.com/password-manager:latest"
export TAG="latest"
```

---

### Step 10: Login to ECR and Pull Image

```bash
# Get your account ID and region
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
REGION=$(aws configure get region || echo "eu-north-1")

# Login to ECR
aws ecr get-login-password --region $REGION | \
  docker login --username AWS --password-stdin \
  $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com

# Verify login
echo "✓ Logged into ECR"
```

---

### Step 11: Start the Application

```bash
cd /opt/password-manager

# Start the application
docker compose up -d

# Check status
docker compose ps

# View logs
docker compose logs -f
```

---

### Step 12: Verify Deployment

```bash
# Health check
curl http://localhost/health
# Should return: {"ok": true}

# Check from outside (use your EC2 public IP)
curl http://YOUR_EC2_PUBLIC_IP/health
```

---

## 🔧 Troubleshooting

### Issue: Cannot access SSM parameters

**Solution:**
```bash
# Verify IAM role is attached
curl http://169.254.169.254/latest/meta-data/iam/security-credentials/

# Test AWS credentials
aws sts get-caller-identity

# Check SSM permissions
aws ssm get-parameter --name /password-manager/AWS_REGION
```

### Issue: Cannot pull from ECR

**Solution:**
```bash
# Verify ECR login
aws ecr get-login-password --region YOUR_REGION | \
  docker login --username AWS --password-stdin \
  YOUR_ACCOUNT_ID.dkr.ecr.YOUR_REGION.amazonaws.com

# Check IAM role has ECR permissions
aws ecr describe-repositories --repository-names password-manager
```

### Issue: Application not starting

**Solution:**
```bash
# Check logs
docker compose logs

# Check .env file
cat /opt/password-manager/.env

# Verify health endpoint
curl http://localhost:5001/health
```

### Issue: Port 80 not accessible

**Solution:**
- Check security group allows inbound port 80
- Verify docker-compose.yml maps 80:5001
- Check if another service is using port 80:
  ```bash
  sudo netstat -tulpn | grep :80
  ```

---

## 🔄 Updating the Application

### Update Docker Image

```bash
cd /opt/password-manager

# Pull latest image
docker compose pull

# Restart with new image
docker compose up -d

# Verify
docker compose ps
curl http://localhost/health
```

### Update Environment Variables

```bash
cd /opt/password-manager

# Re-fetch from SSM
./fetch-env.sh

# Restart application
docker compose restart
```

---

## 📊 Monitoring

### View Logs

```bash
# Real-time logs
docker compose logs -f

# Last 100 lines
docker compose logs --tail=100
```

### Check Health

```bash
# Health endpoint
curl http://localhost/health

# Container status
docker compose ps
```

### Resource Usage

```bash
# Docker stats
docker stats password-manager

# System resources
htop  # or top
```

---

## 🔐 Security Best Practices

1. ✅ **Restrict SSH Access**: Only allow your IP in security group
2. ✅ **Use IAM Roles**: Don't store AWS credentials in .env
3. ✅ **Keep Updated**: Regularly update Docker images and system packages
4. ✅ **Monitor Logs**: Set up CloudWatch Logs for centralized logging
5. ✅ **Use HTTPS**: Set up Application Load Balancer with SSL certificate
6. ✅ **Regular Backups**: Backup DynamoDB tables regularly

---

## 📝 Quick Reference

```bash
# SSH into EC2
ssh -i key.pem ubuntu@EC2_IP

# Setup (one-time)
sudo ./ec2_setup.sh
cd /opt/password-manager
./fetch-env.sh

# Deploy/Update
docker compose pull
docker compose up -d

# Monitor
docker compose logs -f
curl http://localhost/health

# Restart
docker compose restart
```

---

## 🎯 Next Steps

1. **Set up Application Load Balancer** (optional, for high availability)
2. **Configure CloudWatch Logs** for centralized logging
3. **Set up Auto Scaling** if needed
4. **Configure SSL/TLS** using ACM (AWS Certificate Manager)
5. **Set up monitoring** with CloudWatch alarms

---

## 📞 Support

If you encounter issues:
1. Check logs: `docker compose logs`
2. Verify IAM role permissions
3. Check security group rules
4. Verify SSM parameters exist
5. Check ECR repository access

---

**Deployment Complete!** 🎉

Your Password Manager should now be accessible at `http://YOUR_EC2_PUBLIC_IP`

