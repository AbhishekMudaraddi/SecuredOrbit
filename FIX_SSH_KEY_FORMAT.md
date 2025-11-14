# Fix SSH Key Format Error

## 🔍 Problem

**Error**: `Error loading key: invalid format`

**Root Cause**: The SSH private key stored in Jenkins credentials is not in the correct format.

---

## ✅ Solution: Fix SSH Key Format in Jenkins

### Step 1: Get Your EC2 Private Key

Locate your EC2 `.pem` file. It should look like this:

```
-----BEGIN RSA PRIVATE KEY-----
MIIEpAIBAAKCAQEA...
(many lines of base64 encoded data)
...
-----END RSA PRIVATE KEY-----
```

**OR** (newer format):

```
-----BEGIN PRIVATE KEY-----
MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQC...
(many lines of base64 encoded data)
...
-----END PRIVATE KEY-----
```

### Step 2: Verify Key Format

**Correct format includes**:
- ✅ Header line: `-----BEGIN RSA PRIVATE KEY-----` or `-----BEGIN PRIVATE KEY-----`
- ✅ Footer line: `-----END RSA PRIVATE KEY-----` or `-----END PRIVATE KEY-----`
- ✅ No extra spaces or characters
- ✅ No passphrase (or remove passphrase)

**Common mistakes**:
- ❌ Missing header/footer lines
- ❌ Extra spaces or line breaks
- ❌ Wrong key format
- ❌ Encrypted key (has passphrase)

### Step 3: Convert Key Format (If Needed)

If your key is in a different format, convert it:

```bash
# If you have a .pem file, it should already be correct
# But if you need to convert:

# Convert PPK (PuTTY) to PEM format
puttygen your-key.ppk -O private-openssh -o your-key.pem

# Remove passphrase (if key is encrypted)
openssl rsa -in encrypted-key.pem -out decrypted-key.pem

# Verify key format
head -1 your-key.pem
# Should show: -----BEGIN RSA PRIVATE KEY----- or -----BEGIN PRIVATE KEY-----
```

### Step 4: Update Jenkins Credentials

1. **Go to**: Jenkins → **Manage Jenkins** → **Credentials** → **System** → **Global credentials**

2. **Find**: `ec2-ssh` credential

3. **Click**: The credential to edit (or delete and recreate)

4. **Update**:
   - **Kind**: SSH Username with private key
   - **ID**: `ec2-ssh`
   - **Description**: `SSH key for EC2 deployment`
   - **Username**: `ec2-user` (or `ubuntu`)
   - **Private Key**: 
     - Select: **Enter directly**
     - **Copy the ENTIRE key** including:
       ```
       -----BEGIN RSA PRIVATE KEY-----
       (all lines of the key)
       -----END RSA PRIVATE KEY-----
       ```
     - **Important**: 
       - Include header and footer lines
       - No extra spaces
       - Copy exactly as it appears in the file

5. **Click**: **OK** or **Save**

### Step 5: Verify Key Format in Jenkins

After saving, the key should be stored correctly. You can verify by:
- Testing SSH connection manually first
- Running the pipeline again

---

## 🔧 Alternative: Use File-Based Key

If "Enter directly" doesn't work, try using a file:

1. **Copy key to Jenkins server**:
   ```bash
   # On Jenkins server (your local machine)
   cp /path/to/your-key.pem ~/.jenkins/keys/ec2-key.pem
   chmod 600 ~/.jenkins/keys/ec2-key.pem
   ```

2. **Update Jenkins credential**:
   - **Private Key**: Select **From the Jenkins master ~/.ssh**
   - **File**: `~/.jenkins/keys/ec2-key.pem`

---

## 🧪 Test SSH Key Format

Before updating Jenkins, test the key locally:

```bash
# Test key format
ssh-keygen -l -f your-key.pem

# Test SSH connection
ssh -i your-key.pem ec2-user@54.198.152.202

# If this works, the key format is correct
```

---

## 📋 Complete Checklist

- [ ] SSH key file exists (`.pem` format)
- [ ] Key has correct header (`-----BEGIN RSA PRIVATE KEY-----`)
- [ ] Key has correct footer (`-----END RSA PRIVATE KEY-----`)
- [ ] Key has no passphrase (or passphrase removed)
- [ ] Key copied correctly to Jenkins (including header/footer)
- [ ] No extra spaces or characters
- [ ] SSH connection works manually
- [ ] Jenkins credential updated

---

## 🚀 After Fixing

1. **Update SSH credential** in Jenkins with correct format
2. **Run pipeline again**
3. **Deploy stage should work**

---

## 💡 Quick Fix Command

If you have the key file, you can quickly verify and copy:

```bash
# View first line (should be header)
head -1 your-key.pem

# View last line (should be footer)
tail -1 your-key.pem

# Copy entire key (including header/footer)
cat your-key.pem | pbcopy  # macOS
# Then paste into Jenkins credential field
```

---

**The key format is the issue. Make sure the entire key (including header/footer) is copied correctly into Jenkins credentials.** 🔑

