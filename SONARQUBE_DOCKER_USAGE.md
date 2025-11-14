# Using SonarQube Scanner with Docker

## ✅ Your Setup

- **SonarQube Server**: Running in Docker on `localhost:9000`
- **SonarQube Scanner**: Will use Docker (no local installation needed)

## 🔧 What Changed

The Jenkinsfile has been updated to use **Docker to run sonar-scanner** instead of requiring a local installation.

### How It Works

1. **SonarQube Server** (already running):
   ```bash
   docker run -d --name sonarqube -p 9000:9000 sonarqube:lts-community
   ```

2. **SonarQube Scanner** (via Docker in Jenkins):
   - Uses `sonarsource/sonar-scanner-cli:latest` Docker image
   - No local installation needed
   - Automatically mounts your code directory
   - Uses environment variables from Jenkins SonarQube configuration

## ✅ Verify SonarQube Server is Running

```bash
# Check if SonarQube container is running
docker ps | grep sonarqube

# Check if SonarQube is accessible
curl http://localhost:9000/api/system/status

# Or open in browser
open http://localhost:9000
```

## 🔧 Jenkins Configuration

Make sure SonarQube is configured in Jenkins:

1. Go to: **Jenkins → Manage Jenkins → Configure System**
2. Find: **SonarQube servers** section
3. Verify:
   - **Name**: `sonar-local`
   - **Server URL**: `http://localhost:9000`
   - **Server authentication token**: Your SonarQube token

## 🧪 Test SonarQube Scanner via Docker

Test manually before running Jenkins pipeline:

```bash
cd /Users/abhishekmudaraddi/Final

# Set SonarQube token (get from SonarQube UI)
export SONAR_TOKEN="your-token-here"

# Run scanner via Docker
docker run --rm \
    -v "$(pwd):/usr/src" \
    -w /usr/src \
    -e SONAR_HOST_URL="http://host.docker.internal:9000" \
    -e SONAR_TOKEN="${SONAR_TOKEN}" \
    sonarsource/sonar-scanner-cli:latest
```

**Note**: Use `host.docker.internal:9000` instead of `localhost:9000` when running from Docker, as Docker containers can't access `localhost` on the host.

## 🔧 Update Jenkinsfile for Docker Network

If SonarQube is running in Docker, we need to use `host.docker.internal` to access it from the scanner container.

The Jenkinsfile uses `${SONAR_HOST_URL}` which Jenkins sets automatically. If you encounter connection issues, you may need to:

1. **Option 1**: Use host network mode for SonarQube:
   ```bash
   docker run -d --name sonarqube --network host sonarqube:lts-community
   ```

2. **Option 2**: Update SonarQube server URL in Jenkins to use `host.docker.internal:9000`

3. **Option 3**: Use Docker Compose with a shared network

## ✅ Benefits

- ✅ **No local installation** - Everything runs in Docker
- ✅ **Consistent environment** - Same scanner version every time
- ✅ **Easy updates** - Just pull new Docker image
- ✅ **Isolated** - Doesn't affect your local system

---

## 🐛 Troubleshooting

### Scanner Can't Connect to SonarQube

**Error**: `Unable to connect to SonarQube server`

**Solution**: Use `host.docker.internal:9000` instead of `localhost:9000`:

1. Update Jenkins SonarQube configuration:
   - **Server URL**: `http://host.docker.internal:9000`

2. Or restart SonarQube with host network:
   ```bash
   docker stop sonarqube
   docker rm sonarqube
   docker run -d --name sonarqube --network host sonarqube:lts-community
   ```

### Docker Not Available in Jenkins

**Error**: `docker: command not found`

**Solution**: Ensure Docker is installed and Jenkins can access it:

```bash
# Check Docker
docker --version

# On macOS, Docker Desktop must be running
# Jenkins should be able to access Docker socket
```

### SonarQube Token Issues

**Error**: `Authentication failed`

**Solution**: 
1. Generate new token in SonarQube: **My Account → Security → Generate Tokens**
2. Update token in Jenkins: **Manage Jenkins → Configure System → SonarQube servers**

---

**Your SonarQube setup is ready! The Jenkinsfile will use Docker for scanning.** 🎉

