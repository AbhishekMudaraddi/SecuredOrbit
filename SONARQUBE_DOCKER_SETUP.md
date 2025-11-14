# SonarQube Docker Setup Guide

## ✅ What You've Done

You've installed SonarQube using Docker:
```bash
docker run -d --name sonarqube \
  -p 9000:9000 \
  sonarqube:lts-community
```

## 🔧 Next Steps: Configure SonarQube

### Step 1: Access SonarQube

1. **Open browser**: `http://localhost:9000`
2. **Wait for initialization** (may take 1-2 minutes on first start)
3. **Login**:
   - Username: `admin`
   - Password: `admin` (you'll be prompted to change it)

### Step 2: Generate SonarQube Token

1. **Login** to SonarQube: `http://localhost:9000`
2. Go to: **My Account → Security**
3. Under **Generate Tokens**, enter:
   - **Name**: `jenkins-token`
   - **Type**: `User Token`
   - **Expires in**: `No expiration` (or set expiration date)
4. Click: **Generate**
5. **Copy the token** (you won't see it again!)

### Step 3: Configure SonarQube in Jenkins

1. Go to: **Jenkins → Manage Jenkins → Configure System**
2. Scroll to: **SonarQube servers** section
3. Click: **Add SonarQube**
4. Fill in:
   - **Name**: `sonar-local`
   - **Server URL**: `http://localhost:9000`
   - **Server authentication token**: Paste the token from Step 2
5. Click: **Save**

### Step 4: Install SonarQube Scanner (if needed)

**Check if sonar-scanner is installed**:
```bash
sonar-scanner --version
```

**If not installed**:

**macOS**:
```bash
brew install sonar-scanner
```

**Linux**:
```bash
# Download and install
wget https://binaries.sonarsource.com/Distribution/sonar-scanner-cli/sonar-scanner-cli-5.0.1.3006-linux.zip
unzip sonar-scanner-cli-5.0.1.3006-linux.zip
sudo mv sonar-scanner-5.0.1.3006 /opt/sonar-scanner
export PATH=$PATH:/opt/sonar-scanner/bin
```

**Or use Docker** (alternative):
```bash
# Use sonar-scanner Docker image in Jenkinsfile
```

### Step 5: Verify SonarQube is Running

```bash
# Check Docker container
docker ps | grep sonarqube

# Check logs
docker logs sonarqube

# Test access
curl http://localhost:9000/api/system/status
```

---

## 🔄 Update Jenkinsfile (if needed)

The Jenkinsfile already has SonarQube integration. It will:
- Check if `sonar-project.properties` exists
- Run SonarQube analysis if file exists
- Skip if file doesn't exist

**The `sonar-project.properties` file has been created** ✅

---

## ✅ Verification Checklist

- [ ] SonarQube container is running (`docker ps`)
- [ ] SonarQube accessible at `http://localhost:9000`
- [ ] Logged into SonarQube (admin/admin)
- [ ] Generated authentication token
- [ ] Configured SonarQube in Jenkins (`sonar-local`)
- [ ] `sonar-project.properties` file exists in repo root
- [ ] SonarQube Scanner installed (or using Docker)

---

## 🧪 Test SonarQube Integration

1. **Run Jenkins pipeline**
2. **Check SonarQube stage** in console output
3. **Verify** analysis completes successfully
4. **Check** results in SonarQube: `http://localhost:9000`

---

## 🐛 Troubleshooting

### SonarQube Not Accessible

```bash
# Check container status
docker ps -a | grep sonarqube

# Check logs
docker logs sonarqube

# Restart if needed
docker restart sonarqube
```

### SonarQube Scanner Not Found

**Option 1**: Install sonar-scanner (see Step 4 above)

**Option 2**: Use Docker in Jenkinsfile:
```groovy
sh '''
    docker run --rm \\
        -v $(pwd):/usr/src \\
        sonarsource/sonar-scanner-cli \\
        -Dsonar.projectKey=password-manager
'''
```

### Authentication Failed

- **Check**: Token is correct in Jenkins configuration
- **Check**: SonarQube server URL is `http://localhost:9000`
- **Regenerate**: Token in SonarQube if needed

---

## 📝 Notes

- **SonarQube data**: Stored in Docker volume (persists after container restart)
- **Port**: 9000 (make sure it's not used by another service)
- **Memory**: SonarQube needs at least 2GB RAM
- **First start**: May take 1-2 minutes to initialize

---

**SonarQube is ready!** Configure it in Jenkins and test the pipeline. 🎉

