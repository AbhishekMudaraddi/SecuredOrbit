# Complete Next Steps Guide - CI/CD Pipeline

## 🎯 Current Status

✅ **Pipeline is working!**
- ✅ Checkout: Working
- ✅ Setup Python: Working
- ✅ Lint & Tests: All 7 tests passing
- ✅ SonarQube: Optional (skips gracefully)
- ✅ Docker Build & Push: Working (image pushed to ECR)
- ⏭️ Deploy to EC2: Skipped (needs verification)

---

## 🔍 Why Deploy to EC2 Didn't Run

The Deploy stage only runs when:
1. **Branch is `main` or `master`** ✅ (You're on `main`)
2. **Previous stages succeeded** ✅ (All passed)
3. **Jenkins detects the branch correctly** ⚠️ (May need verification)

### Check Jenkins Console Output

Look for this message in the Jenkins console:
- `Stage "Deploy to EC2" skipped due to earlier failure(s)` - Previous stage failed
- `Stage "Deploy to EC2" skipped due to when condition` - Branch condition not met
- No message = Stage should have run

---

## 🚀 Next Steps to Complete Deployment

### Step 1: Verify Jenkins Pipeline Configuration

1. **Go to Jenkins**: `http://localhost:8080`
2. **Open**: `password-manager-pipeline` → **Configure**
3. **Check**: **Pipeline** section
   - **Branches to build**: Should include `*/main` or `*/master`
   - **Script Path**: `Jenkinsfile`
4. **Save** if needed

### Step 2: Verify EC2 Setup

Before deploying, ensure EC2 is ready:

#### 2.1: Check EC2 Instance

```bash
# Verify EC2 is running (from AWS Console or CLI)
aws ec2 describe-instances --instance-ids i-055cdfaed83cd7614 --query 'Reservations[0].Instances[0].State.Name'
# Should return: "running"
```

#### 2.2: Verify Security Group

Security group should allow:
- **Port 80 (HTTP)**: From `0.0.0.0/0` (or your IP)
- **Port 443 (HTTPS)**: If using SSL
- **Port 22 (SSH)**: Restricted to your IP only

#### 2.3: Verify EC2 Setup Scripts

SSH to EC2 and verify:

```bash
# SSH to EC2
ssh ec2-user@54.198.152.202

# Check application directory
ls -la /opt/password-manager/

# Should see:
# - fetch-env.sh
# - docker-compose.yml

# Check scripts are executable
chmod +x /opt/password-manager/fetch-env.sh
```

### Step 3: Verify Jenkins SSH Credentials

1. **Go to**: Jenkins → **Manage Jenkins** → **Credentials** → **System** → **Global credentials**
2. **Find**: `ec2-ssh`
3. **Verify**:
   - Username: `ec2-user` (or `ubuntu` depending on your AMI)
   - Private key: Your EC2 `.pem` file content

### Step 4: Run Pipeline Again

1. **Go to**: Jenkins → `password-manager-pipeline`
2. **Click**: **Build Now**
3. **Watch**: Console Output
4. **Look for**: Deploy to EC2 stage

If it still doesn't run, check the console output for the skip reason.

---

## 📋 Complete Deployment Checklist

### Pre-Deployment

- [ ] EC2 instance is running
- [ ] Security group configured (ports 80, 443, 22)
- [ ] IAM role attached with permissions:
  - ECR pull access
  - DynamoDB access
  - SSM parameter read access
- [ ] Docker installed on EC2
- [ ] Docker Compose installed on EC2
- [ ] AWS CLI installed on EC2
- [ ] `/opt/password-manager/` directory exists
- [ ] `fetch-env.sh` copied to EC2
- [ ] `docker-compose.yml` copied to EC2
- [ ] Scripts are executable

### Jenkins Configuration

- [ ] Pipeline configured to build from `main` branch
- [ ] SSH credentials (`ec2-ssh`) configured
- [ ] EC2 IP address correct in Jenkinsfile (`54.198.152.202`)
- [ ] EC2 username correct (`ec2-user` or `ubuntu`)

### AWS Configuration

- [ ] ECR repository exists
- [ ] Docker image pushed to ECR
- [ ] SSM parameters configured:
  - `/password-manager/SESSION_SECRET`
  - `/password-manager/AWS_REGION`
  - `/password-manager/PORT`
  - `/password-manager/DYNAMODB_USERS_TABLE`
  - `/password-manager/DYNAMODB_ACCOUNTS_TABLE`
  - `/password-manager/DYNAMODB_PASSWORDS_TABLE`

---

## 🔧 Manual Deployment (Alternative)

If Jenkins deployment doesn't work, deploy manually:

### Step 1: SSH to EC2

```bash
ssh ec2-user@54.198.152.202
```

### Step 2: Navigate to Application Directory

```bash
cd /opt/password-manager
```

### Step 3: Fetch Environment Variables

```bash
./fetch-env.sh
```

This creates `.env` file from SSM parameters.

### Step 4: Login to ECR

```bash
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin \
  503561414328.dkr.ecr.us-east-1.amazonaws.com
```

### Step 5: Update Docker Compose

Edit `docker-compose.yml` and ensure image is correct:

```yaml
services:
  password-manager:
    image: 503561414328.dkr.ecr.us-east-1.amazonaws.com/password-manager:latest
    ports:
      - "80:5001"
    # ... rest of config
```

### Step 6: Pull and Start

```bash
docker compose pull
docker compose up -d
```

### Step 7: Verify Deployment

```bash
# Check container status
docker compose ps

# Check logs
docker compose logs -f password-manager

# Test health endpoint
curl http://localhost/health
# Should return: {"ok": true}
```

### Step 8: Access Application

Open browser: `http://54.198.152.202` (or your EC2 public IP)

---

## 🎯 What Happens During Automated Deployment

When the Deploy stage runs, Jenkins will:

1. **SSH to EC2**: Connect using configured credentials
2. **Login to ECR**: Authenticate with AWS ECR
3. **Fetch Environment**: Run `fetch-env.sh` to get SSM parameters
4. **Update Image**: Update `docker-compose.yml` with new image tag
5. **Pull Image**: Download latest Docker image from ECR
6. **Start Container**: Run `docker compose up -d`
7. **Health Check**: Wait for `/health` endpoint (up to 20 tries)
8. **Rollback**: If health check fails, rollback to `latest` tag

---

## 🐛 Troubleshooting

### Deploy Stage Still Not Running

**Check Jenkins Console**:
- Look for skip messages
- Check branch name in console output
- Verify `env.BRANCH_NAME` value

**Force Run on Main**:
```bash
# Ensure you're on main
git checkout main
git push origin main

# Trigger Jenkins build
# Or configure webhook for automatic builds
```

### Deployment Fails

**Check SSH Connection**:
```bash
# Test from your local machine
ssh -i /path/to/key.pem ec2-user@54.198.152.202
```

**Check EC2 Logs**:
```bash
ssh ec2-user@54.198.152.202
cd /opt/password-manager
docker compose logs -f
```

**Check Health Endpoint**:
```bash
curl http://54.198.152.202/health
```

**Check Security Group**:
- Ensure port 80 is open
- Check inbound rules

---

## 📊 Pipeline Summary

### What's Working ✅

1. **Code Checkout**: Git repository cloned
2. **Python Setup**: Virtual environment created, dependencies installed
3. **Testing**: All 7 tests passing, coverage generated
4. **SonarQube**: Optional analysis (skips gracefully if not configured)
5. **Docker Build**: Image built successfully
6. **Docker Push**: Image pushed to ECR

### What's Next ⏭️

1. **Deploy to EC2**: Run on `main` branch
2. **Verify Deployment**: Check application is accessible
3. **Monitor**: Watch logs and health checks

---

## ✅ Quick Action Items

1. **Verify EC2 is ready**:
   ```bash
   ssh ec2-user@54.198.152.202 "cd /opt/password-manager && ls -la"
   ```

2. **Run Jenkins pipeline on main branch**:
   - Go to Jenkins → password-manager-pipeline
   - Click Build Now
   - Watch console output

3. **If Deploy stage skips**:
   - Check console output for skip reason
   - Verify branch is `main`
   - Check previous stages didn't fail

4. **After deployment**:
   - Test: `http://54.198.152.202/health`
   - Access application: `http://54.198.152.202`

---

## 🎉 Success Criteria

Your CI/CD is complete when:

- ✅ Code pushed to Git triggers automatic build
- ✅ Tests run automatically
- ✅ Docker image builds and pushes to ECR
- ✅ Deployment to EC2 happens automatically (on main branch)
- ✅ Health checks verify deployment success
- ✅ Application is accessible at EC2 public IP

---

**You're almost there! The pipeline is working - just need to ensure Deploy stage runs on main branch.** 🚀

