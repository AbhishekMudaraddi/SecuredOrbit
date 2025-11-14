# Fix SonarQube Token Authentication

## Problem

Error: `Not authorized. Analyzing this project requires authentication. Please provide a user token in sonar.login`

The `SONAR_TOKEN` environment variable is empty or not being passed correctly to the Docker container.

## ✅ Solution

The Jenkinsfile has been updated to:
1. Check if SonarQube credentials are configured
2. Show debug info (first 10 chars of token)
3. Properly pass credentials to Docker container

## 🔧 Verify SonarQube Configuration in Jenkins

### Step 1: Check SonarQube Server Configuration

1. Go to: **Jenkins → Manage Jenkins → Configure System**
2. Find: **SonarQube servers** section
3. Verify:
   - **Name**: `sonar-local`
   - **Server URL**: `http://localhost:9000`
   - **Server authentication token**: Should have a token (not empty!)

### Step 2: Generate SonarQube Token

If the token is missing or invalid:

1. **Access SonarQube**: `http://localhost:9000`
2. **Login**: Use your admin credentials
3. **Go to**: **My Account → Security**
4. **Generate Token**:
   - Name: `jenkins-token`
   - Type: `User Token`
   - Expires: `No expiration` (or set a date)
5. **Click**: **Generate**
6. **Copy the token** (you won't see it again!)

### Step 3: Update Jenkins Configuration

1. Go back to: **Jenkins → Manage Jenkins → Configure System**
2. Find: **SonarQube servers** → Click **sonar-local**
3. **Paste the token** in **Server authentication token** field
4. Click: **Save**

### Step 4: Test Connection

After saving, Jenkins should test the connection. You should see:
- ✅ **Connection successful**

## 🧪 Verify Token Works

Test manually:

```bash
# Set token (replace with your actual token)
export SONAR_TOKEN="your-actual-token-here"
export SONAR_HOST_URL="http://localhost:9000"

# Test connection
curl -u "${SONAR_TOKEN}:" "${SONAR_HOST_URL}/api/system/status"
```

Should return JSON with SonarQube status.

## 🔍 Debugging

### Check if Token is Set in Jenkins

The updated Jenkinsfile will show:
- `SonarQube URL: http://host.docker.internal:9000`
- `SonarQube Token: abc1234567...` (first 10 chars)

If token shows as empty, the SonarQube configuration in Jenkins is missing the token.

### Common Issues

1. **Token not saved**: Make sure to click **Save** after entering token
2. **Token expired**: Generate a new token if it expired
3. **Wrong SonarQube server**: Make sure Jenkins is configured to use `sonar-local`
4. **Token format**: Should be a long alphanumeric string (no spaces)

## ✅ After Fixing

1. **Commit and push** updated Jenkinsfile
2. **Run pipeline again**
3. **Check console output** - should see:
   - `SonarQube Token: abc1234567...`
   - SonarQube analysis running successfully
   - Quality Gate waiting for results

---

**The Jenkinsfile now checks for credentials and provides better error messages.** 🔧

