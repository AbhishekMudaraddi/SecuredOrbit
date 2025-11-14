# Access Your Deployed Application

## 🎉 Deployment Successful!

Your application is now deployed on EC2. Here's how to access it:

---

## 🌐 Access the Application

### Option 1: Web Browser (Recommended)

Open your web browser and go to:

```
http://54.198.152.202
```

**Or** if you have a domain name configured:

```
http://your-domain.com
```

### Option 2: Health Check Endpoint

Test if the application is running:

```
http://54.198.152.202/health
```

Should return: `{"ok": true}`

---

## 🔍 Verify Deployment Status

### Check via SSH

```bash
# SSH to EC2
ssh ec2-user@54.198.152.202

# Check container status
cd /opt/password-manager
docker compose ps

# Check logs
docker compose logs -f password-manager

# Test health endpoint
curl http://localhost/health
```

### Check via AWS Console

1. Go to: **EC2 Console** → **Instances**
2. Find your instance: `i-055cdfaed83cd7614` (or search by IP)
3. Check: **Status checks** should show "2/2 checks passed"
4. Check: **Security group** - port 80 should be open

---

## 📊 Application URLs

### Main Application
- **URL**: `http://54.198.152.202`
- **Login**: `http://54.198.152.202/login`
- **Register**: `http://54.198.152.202/register`

### Health Check
- **URL**: `http://54.198.152.202/health`
- **Expected**: `{"ok": true}`

---

## 🔧 Troubleshooting

### Application Not Accessible

**Check 1: Security Group**
- Go to: **EC2 Console** → **Security Groups**
- Find your instance's security group
- Verify **Inbound Rules**:
  - Port **80** (HTTP) - Source: `0.0.0.0/0` or your IP
  - Port **443** (HTTPS) - If using SSL

**Check 2: Container Status**
```bash
ssh ec2-user@54.198.152.202
cd /opt/password-manager
docker compose ps
# Should show: password-manager | Up
```

**Check 3: Application Logs**
```bash
ssh ec2-user@54.198.152.202
cd /opt/password-manager
docker compose logs password-manager
# Look for errors or startup messages
```

**Check 4: Port Mapping**
```bash
ssh ec2-user@54.198.152.202
docker compose ps
# Should show: 0.0.0.0:80->5001/tcp
```

### Health Check Fails

```bash
# Test locally on EC2
ssh ec2-user@54.198.152.202
curl http://localhost/health

# If this works but external doesn't, check security group
```

---

## 📝 Next Steps

### 1. Test the Application

1. **Register a new user**:
   - Go to: `http://54.198.152.202/register`
   - Create an account
   - Set up TOTP (Google Authenticator)
   - Save recovery phrase

2. **Login**:
   - Go to: `http://54.198.152.202/login`
   - Enter credentials
   - Enter TOTP code

3. **Add passwords**:
   - Use the dashboard to store passwords
   - Test search functionality
   - Test password strength checker

### 2. Monitor Deployment

**Jenkins Console**:
- Go to: `http://localhost:8080`
- Open: `password-manager-pipeline`
- View: Latest build → Console Output
- Check: Deploy stage logs

**EC2 Logs**:
```bash
ssh ec2-user@54.198.152.202
cd /opt/password-manager
docker compose logs -f password-manager
```

### 3. Set Up HTTPS (Optional)

For production, set up SSL/TLS:

1. **Get SSL Certificate** (Let's Encrypt)
2. **Configure Nginx** as reverse proxy
3. **Update Security Group** to allow port 443
4. **Update Application** to use HTTPS

---

## 🎯 Quick Access Commands

```bash
# Open in browser (macOS)
open http://54.198.152.202

# Test health endpoint
curl http://54.198.152.202/health

# SSH to EC2
ssh ec2-user@54.198.152.202

# View logs
ssh ec2-user@54.198.152.202 "cd /opt/password-manager && docker compose logs -f"
```

---

## ✅ Success Indicators

Your deployment is successful when:

- ✅ Application accessible at `http://54.198.152.202`
- ✅ Health endpoint returns `{"ok": true}`
- ✅ Login/Register pages load
- ✅ Container is running (`docker compose ps` shows "Up")
- ✅ No errors in logs

---

**Your application is live! Access it at: http://54.198.152.202** 🚀

