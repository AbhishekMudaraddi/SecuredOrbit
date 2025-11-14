# Fix Jenkins PATH Issue on macOS

## Problem

Error: `sh: sh: command not found`

This happens because Jenkins on macOS can't find the shell executable due to PATH issues.

## Solution 1: Configure Jenkins Global Tool Locations

1. Go to: **Jenkins → Manage Jenkins → Global Tool Configuration**
2. Find: **Shell executable**
3. Set: `/bin/bash` (or `/bin/sh`)
4. Click: **Save**

## Solution 2: Update Jenkinsfile (Already Done)

The Jenkinsfile has been updated to:
- Set PATH explicitly in environment
- Use `#!/bin/bash` shebang in all shell scripts
- Use `source` instead of `.` for activating venv

## Solution 3: Configure Jenkins Node (If Using Agent)

If Jenkins is running as an agent:

1. Go to: **Jenkins → Manage Jenkins → Nodes**
2. Click on your node
3. Go to: **Configure**
4. Under **Node Properties**, add:
   - **Environment variables**:
     - `PATH` = `/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin`
     - `SHELL` = `/bin/bash`

## Solution 4: Restart Jenkins

After making changes, restart Jenkins:

1. Go to: **Jenkins → Manage Jenkins → Restart Jenkins**
2. Or from terminal:
   ```bash
   # If Jenkins runs as service
   sudo systemctl restart jenkins
   
   # If Jenkins runs via Java
   # Find Jenkins process and restart
   ```

## Verify Fix

After applying fixes, run the pipeline again. The `sh: command not found` error should be resolved.

---

## Additional macOS Considerations

### Check Shell Availability

```bash
# Verify bash exists
which bash
# Should show: /bin/bash

# Verify sh exists
which sh
# Should show: /bin/sh
```

### Jenkins Java Home

If issues persist, check Jenkins Java configuration:

1. Go to: **Jenkins → Manage Jenkins → Configure System**
2. Check: **JDK** configuration
3. Ensure Java is properly configured

---

**The Jenkinsfile has been updated with PATH fixes. Try running the pipeline again!** 🚀

