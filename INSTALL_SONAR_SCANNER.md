# Install SonarQube Scanner

## Problem

Error: `sonar-scanner: command not found`

The SonarQube Scanner is not installed on your system.

## ✅ Quick Fix: Make SonarQube Optional

The Jenkinsfile has been updated to **skip SonarQube gracefully** if the scanner is not installed. The pipeline will continue without failing.

## 🔧 Install SonarQube Scanner (Optional)

If you want to enable SonarQube analysis, install the scanner:

### macOS (Homebrew)

```bash
brew install sonar-scanner
```

### macOS (Manual)

```bash
# Download
cd /tmp
wget https://binaries.sonarsource.com/Distribution/sonar-scanner-cli/sonar-scanner-cli-5.0.1.3006-macosx.zip
unzip sonar-scanner-cli-5.0.1.3006-macosx.zip

# Install
sudo mv sonar-scanner-5.0.1.3006 /opt/sonar-scanner
sudo ln -s /opt/sonar-scanner/bin/sonar-scanner /usr/local/bin/sonar-scanner

# Verify
sonar-scanner --version
```

### Linux

```bash
# Download
cd /tmp
wget https://binaries.sonarsource.com/Distribution/sonar-scanner-cli/sonar-scanner-cli-5.0.1.3006-linux.zip
unzip sonar-scanner-cli-5.0.1.3006-linux.zip

# Install
sudo mv sonar-scanner-5.0.1.3006 /opt/sonar-scanner
export PATH=$PATH:/opt/sonar-scanner/bin

# Add to ~/.bashrc for persistence
echo 'export PATH=$PATH:/opt/sonar-scanner/bin' >> ~/.bashrc

# Verify
sonar-scanner --version
```

### Alternative: Use Docker

You can also use SonarQube Scanner via Docker (no installation needed):

```bash
# Test scanner
docker run --rm \
    -v $(pwd):/usr/src \
    sonarsource/sonar-scanner-cli \
    -Dsonar.projectKey=password-manager
```

---

## ✅ Current Status

**The Jenkinsfile now handles missing SonarQube Scanner gracefully:**

- ✅ If `sonar-scanner` is not found → Pipeline continues (skips SonarQube stage)
- ✅ If `sonar-scanner` is found → Runs SonarQube analysis
- ✅ Pipeline won't fail due to missing scanner

---

## 🧪 Test After Installation

1. **Install sonar-scanner** (using one of the methods above)
2. **Verify installation**:
   ```bash
   sonar-scanner --version
   ```
3. **Run Jenkins pipeline again**
4. **Check SonarQube stage** - should run successfully

---

## 📝 Notes

- **SonarQube is optional** - Your pipeline will work fine without it
- **Code quality analysis** - SonarQube provides additional insights but isn't required
- **Installation is optional** - Only install if you want SonarQube analysis

---

**Your pipeline is working! SonarQube is now optional.** 🎉

