# Fix Branch Detection Issue

## 🔍 Problem Identified

**Console Output Shows**:
```
Branch: null
Stage "Deploy to EC2" skipped due to when conditional
```

**Root Cause**: Jenkins isn't detecting the branch name correctly, so `env.BRANCH_NAME` is `null`. The `when` condition checks for `branch 'main'` or `branch 'master'`, but since the branch is `null`, the condition doesn't match.

## ✅ Solution Applied

Updated the Jenkinsfile to handle `null` branch names (common with manual triggers):

```groovy
stage('Deploy to EC2') {
    when {
        anyOf {
            branch 'main'
            branch 'master'
            expression { 
                // Allow deployment if branch is null (manual trigger)
                return env.BRANCH_NAME == null || 
                       env.BRANCH_NAME == 'main' || 
                       env.BRANCH_NAME == 'master' ||
                       env.GIT_BRANCH == 'origin/main' ||
                       env.GIT_BRANCH == 'origin/master'
            }
        }
    }
}
```

This allows deployment when:
- Branch is `main` or `master` ✅
- Branch is `null` (manual trigger) ✅
- Git branch is `origin/main` or `origin/master` ✅

---

## 🚀 Next Steps

### Step 1: Commit and Push Updated Jenkinsfile

```bash
cd /Users/abhishekmudaraddi/Final
git add Jenkinsfile
git commit -m "Fix branch detection - allow deployment on null branch (manual trigger)"
git push origin main
```

### Step 2: Run Pipeline Again

1. Go to: Jenkins → `password-manager-pipeline`
2. Click: **Build Now**
3. Watch: Console Output
4. **Deploy to EC2 stage should now run!** ✅

---

## 🔧 Alternative: Fix Branch Detection

If you want to ensure branch is always detected correctly:

### Option 1: Use Git Plugin Properly

1. Go to: Jenkins → `password-manager-pipeline` → **Configure**
2. Under **Pipeline**:
   - **Definition**: Pipeline script from SCM
   - **SCM**: Git
   - **Branches to build**: `*/main` or `*/master`
   - **Lightweight checkout**: ❌ Unchecked (needed for full workspace)

### Option 2: Set Branch Name Explicitly

Add this to the Jenkinsfile environment section:

```groovy
environment {
    // ... existing vars ...
    BRANCH_NAME = "${env.BRANCH_NAME ?: env.GIT_BRANCH?.replaceFirst('origin/', '') ?: 'main'}"
}
```

---

## 📋 Verify Deployment Will Work

Before running, ensure:

- [ ] EC2 instance is running
- [ ] SSH credentials configured (`ec2-ssh`)
- [ ] EC2 IP correct in Jenkinsfile (`54.198.152.202`)
- [ ] `/opt/password-manager/` exists on EC2
- [ ] `fetch-env.sh` and `docker-compose.yml` are on EC2

---

## ✅ Expected Result

After pushing the updated Jenkinsfile and running the pipeline:

1. ✅ All previous stages run (Checkout, Setup, Tests, Docker Build & Push)
2. ✅ **Deploy to EC2 stage runs** (no longer skipped!)
3. ✅ Deployment completes successfully
4. ✅ Application accessible at `http://54.198.152.202`

---

**The fix is applied! Commit and push, then run the pipeline again.** 🎉

