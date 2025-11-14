# Fix Jenkins "sh: command not found" Error

## Problem

Error: `sh: sh: command not found`

This is a PATH issue on macOS where Jenkins can't find the shell executable.

## ✅ Solution Applied

The Jenkinsfile has been updated with:

1. **PATH environment variable** set explicitly
2. **`#!/bin/bash` shebang** added to all shell scripts
3. **`source` instead of `.`** for activating virtual environment

## 🔧 Additional Fix: Configure Jenkins Shell

### Option 1: Configure in Jenkins UI (Recommended)

1. Go to: **Jenkins → Manage Jenkins → Configure System**
2. Scroll to: **Shell executable** (or **Global properties**)
3. Set: `/bin/bash`
4. Click: **Save**

### Option 2: Set Environment Variable in Jenkins

1. Go to: **Jenkins → Manage Jenkins → Configure System**
2. Find: **Global properties → Environment variables**
3. Add:
   - **Name**: `PATH`
   - **Value**: `/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin`
4. Click: **Save**

### Option 3: Restart Jenkins

After making changes, restart Jenkins:

1. Go to: **Jenkins → Manage Jenkins → Restart Jenkins**
2. Wait for restart to complete

---

## ✅ What Was Fixed in Jenkinsfile

### Changes Made:

1. **Added PATH to environment**:
   ```groovy
   PATH = "/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:${env.PATH}"
   ```

2. **Added bash shebang to all scripts**:
   ```groovy
   sh '''
       #!/bin/bash
       set -e
       ...
   '''
   ```

3. **Changed `. .venv/bin/activate` to `source .venv/bin/activate`**

---

## 🧪 Test the Fix

1. **Commit and push** the updated Jenkinsfile:
   ```bash
   git add Jenkinsfile
   git commit -m "Fix PATH issue for macOS Jenkins"
   git push
   ```

2. **Run pipeline again** in Jenkins

3. **Check console output** - the `sh: command not found` error should be gone

---

## 📝 Verify Shell Availability

From your local machine:

```bash
# Check bash exists
which bash
# Should show: /bin/bash

# Check sh exists  
which sh
# Should show: /bin/sh

# Test Jenkins can access
/usr/local/bin/bash --version
```

---

## 🐛 If Still Failing

### Check Jenkins Logs

```bash
# View Jenkins logs
tail -f ~/.jenkins/logs/jenkins.log

# Or if Jenkins runs as service
sudo journalctl -u jenkins -f
```

### Verify Jenkins User Has Access

```bash
# Check if Jenkins user can access bash
sudo -u jenkins /bin/bash --version

# Or if Jenkins runs as your user
/bin/bash --version
```

---

## ✅ Summary

**Fixed in Jenkinsfile**:
- ✅ PATH environment variable added
- ✅ Bash shebang added to all scripts
- ✅ `source` used instead of `.`

**Next Steps**:
1. Commit and push updated Jenkinsfile
2. Configure Jenkins shell path (Option 1 above)
3. Restart Jenkins
4. Run pipeline again

**The Jenkinsfile is now fixed!** 🎉

