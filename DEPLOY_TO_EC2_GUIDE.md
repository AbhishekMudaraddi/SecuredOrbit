# Deploy to EC2 Stage - Why It Didn't Run & Next Steps

## 🔍 Why Deploy to EC2 Didn't Run

The **Deploy to EC2** stage has a condition that only runs on specific branches:

```groovy
stage('Deploy to EC2') {
    when {
        // Only deploy on main/master branch
        anyOf {
            branch 'main'
            branch 'master'
        }
    }
}
```

### Possible Reasons:

1. **Not on main/master branch** - The pipeline only deploys when running on `main` or `master` branch
2. **Branch detection issue** - Jenkins might not be detecting the branch correctly

---

## ✅ Check Your Current Branch

Run this command to check your branch:

```bash
git branch --show-current
```

If you're on a different branch (like `develop`, `feature/*`, etc.), the Deploy stage will be skipped.

---

## 🚀 Next Steps to Deploy

### Option 1: Merge to Main Branch (Recommended)

1. **Check current branch**:
   ```bash
   git branch --show-current
   ```

2. **If on a feature branch, merge to main**:
   ```bash
   git checkout main
   git merge your-feature-branch
   git push origin main
   ```

3. **Run pipeline on main branch**:
   - Go to Jenkins → password-manager-pipeline
   - Make sure it's building from `main` branch
   - Click **Build Now**

### Option 2: Temporarily Remove Branch Restriction (For Testing)

If you want to test deployment on a different branch, you can temporarily modify the Jenkinsfile:

```groovy
stage('Deploy to EC2') {
    // Temporarily removed branch restriction for testing
    // when {
    //     anyOf {
    //         branch 'main'
    //         branch 'master'
    //     }
    // }
    steps {
        // ... deployment steps
    }
}
```

**⚠️ Warning**: Only do this for testing. In production, always deploy from `main` branch.

---

## 📋 Complete Deployment Checklist

Before deploying, ensure:

### 1. EC2 Instance Ready
- [ ] EC2 instance is running
- [ ] Security group allows:
  - Port 80 (HTTP) - from anywhere or your IP
  - Port 443 (HTTPS) - if using SSL
  - Port 22 (SSH) - restricted to your IP
- [ ] IAM role attached with ECR/DynamoDB/SSM permissions

### 2. EC2 Setup Complete
- [ ] Docker installed (`docker --version`)
- [ ] Docker Compose installed (`docker compose version`)
- [ ] AWS CLI installed (`aws --version`)
- [ ] Application directory created: `/opt/password-manager`
- [ ] Files copied:
  - `fetch-env.sh` → `/opt/password-manager/fetch-env.sh`
  - `docker-compose.yml` → `/opt/password-manager/docker-compose.yml`
- [ ] Scripts are executable: `chmod +x /opt/password-manager/fetch-env.sh`

### 3. Jenkins Configuration
- [ ] SSH credentials configured (`ec2-ssh`)
- [ ] EC2 public IP is correct in Jenkinsfile
- [ ] Pipeline is running on `main` branch

### 4. AWS Configuration
- [ ] ECR repository exists
- [ ] Docker image pushed to ECR
- [ ] SSM parameters configured:
  - `/password-manager/SESSION_SECRET`
  - `/password-manager/AWS_REGION`
  - `/password-manager/PORT`
  - `/password-manager/DYNAMODB_*_TABLE`

---

## 🔧 Manual Deployment (If Needed)

If you want to deploy manually for testing:

### Step 1: SSH to EC2

```bash
ssh ec2-user@YOUR_EC2_IP
# or
ssh ubuntu@YOUR_EC2_IP
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

### Step 4: Update Docker Compose with ECR Image

Edit `docker-compose.yml` and update the image:

```yaml
services:
  password-manager:
    image: 503561414328.dkr.ecr.us-east-1.amazonaws.com/password-manager:latest
    # ... rest of config
```

### Step 5: Login to ECR

```bash
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin \
  503561414328.dkr.ecr.us-east-1.amazonaws.com
```

### Step 6: Pull and Start Container

```bash
docker compose pull
docker compose up -d
```

### Step 7: Check Status

```bash
# Check container status
docker compose ps

# Check logs
docker compose logs -f

# Test health endpoint
curl http://localhost/health
```

---

## 🎯 Automated Deployment via Jenkins

Once you're on `main` branch:

1. **Push to main**:
   ```bash
   git checkout main
   git merge your-branch
   git push origin main
   ```

2. **Run Jenkins Pipeline**:
   - Go to Jenkins → password-manager-pipeline
   - Click **Build Now**
   - Watch console output

3. **Deploy Stage Will**:
   - SSH to EC2
   - Login to ECR
   - Fetch environment variables
   - Pull latest Docker image
   - Update and restart container
   - Run health checks
   - Rollback on failure

---

## 🐛 Troubleshooting

### Deploy Stage Still Not Running

**Check Jenkins Console Output**:
- Look for: `Stage "Deploy to EC2" skipped due to...`
- Common reasons:
  - Not on main/master branch
  - Previous stage failed
  - Branch condition not met

**Verify Branch in Jenkins**:
- Go to pipeline → Configure
- Check: **Branches to build** → Should include `*/main` or `*/master`

### Deployment Fails

**Check SSH Connection**:
```bash
# From Jenkins server, test SSH
ssh -i /path/to/key.pem ec2-user@EC2_IP
```

**Check EC2 Logs**:
```bash
# SSH to EC2
ssh ec2-user@EC2_IP
cd /opt/password-manager
docker compose logs
```

**Check Health Endpoint**:
```bash
curl http://EC2_PUBLIC_IP/health
```

---

## 📊 Expected Pipeline Flow

1. ✅ **Checkout** - Gets code from Git
2. ✅ **Setup Python** - Creates venv, installs dependencies
3. ✅ **Lint & Tests** - Runs tests, publishes results
4. ⚠️ **SonarQube** - Optional (skips if not configured)
5. ✅ **Docker Build & Push** - Builds and pushes to ECR
6. ⏭️ **Deploy to EC2** - Only runs on `main` branch

---

## ✅ Summary

**Why Deploy Didn't Run**: The stage only runs on `main` or `master` branch.

**Next Steps**:
1. Check your current branch
2. Merge to `main` branch if needed
3. Push to `main`
4. Run Jenkins pipeline on `main` branch
5. Deploy stage will run automatically

**The pipeline is working correctly!** It's just waiting for you to run it on the `main` branch. 🎉

