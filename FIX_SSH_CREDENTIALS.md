# Fix SSH Credentials Error

## 🔍 Problem

**Error**: `ERROR: Failed to run ssh-add`

**Location**: Deploy to EC2 stage

**Cause**: Jenkins SSH Agent plugin can't add the SSH key to the agent.

---

## ✅ Solutions

### Solution 1: Verify SSH Credentials in Jenkins

1. **Go to**: Jenkins → **Manage Jenkins** → **Credentials** → **System** → **Global credentials**

2. **Find**: `ec2-ssh` (or check what ID you used)

3. **Verify**:
   - **Type**: SSH Username with private key
   - **Username**: `ec2-user` (or `ubuntu` depending on your EC2 AMI)
   - **Private Key**: Should contain your EC2 `.pem` file content
   - **ID**: `ec2-ssh` (must match Jenkinsfile)

4. **If missing or incorrect**:
   - Click **Add Credentials**
   - Select: **SSH Username with private key**
   - Fill in:
     - **ID**: `ec2-ssh`
     - **Description**: `SSH key for EC2 deployment`
     - **Username**: `ec2-user`
     - **Private Key**: 
       - Select **Enter directly**
       - Paste your EC2 `.pem` file content
   - Click **OK**

### Solution 2: Test SSH Connection Manually

From your local machine, test SSH:

```bash
# Test SSH connection
ssh -i /path/to/your-key.pem ec2-user@54.198.152.202

# If this works, the key is correct
# If this fails, check:
# - Key file permissions: chmod 400 /path/to/your-key.pem
# - EC2 security group allows SSH from your IP
# - EC2 instance is running
```

### Solution 3: Update Jenkinsfile to Handle SSH Errors

If SSH credentials are correct but still failing, we can add better error handling.

---

## 🔧 Quick Fix: Update SSH Credential ID

If your SSH credential has a different ID, update the Jenkinsfile:

1. **Check your credential ID** in Jenkins
2. **Update Jenkinsfile** line 268:

```groovy
sshagent(credentials: ['your-actual-credential-id']) {
```

---

## 🧪 Verify SSH Agent Plugin

1. **Go to**: Jenkins → **Manage Jenkins** → **Manage Plugins**
2. **Installed**: Search for "SSH Agent Plugin"
3. **If not installed**: Install it and restart Jenkins

---

## 📋 Complete Checklist

- [ ] SSH Agent Plugin installed
- [ ] SSH credentials configured (`ec2-ssh`)
- [ ] Credential ID matches Jenkinsfile
- [ ] Username is correct (`ec2-user` or `ubuntu`)
- [ ] Private key is correct (EC2 `.pem` file content)
- [ ] SSH connection works manually
- [ ] EC2 security group allows SSH

---

## 🚀 After Fixing

1. **Update credentials** if needed
2. **Run pipeline again**
3. **Deploy stage should work**

---

**Check your SSH credentials configuration in Jenkins first!** 🔑

