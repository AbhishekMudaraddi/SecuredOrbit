# Quick Deployment Reference

## 🚀 Deploy to Production in 3 Steps

### Step 1: Ensure GitHub Secrets are Configured

Go to: **GitHub Repository → Settings → Secrets and variables → Actions**

Required secrets:
- `AWS_ACCESS_KEY_ID` - Your AWS access key
- `AWS_SECRET_ACCESS_KEY` - Your AWS secret key
- `AWS_REGION` (optional) - Defaults to `us-east-1`

### Step 2: Merge Latest Changes to Production

```bash
# Option A: Merge from main
git checkout production
git pull origin production
git merge main
git push origin production

# Option B: If you're already on main with changes
git checkout production
git merge main
git push origin production
```

### Step 3: Monitor Deployment

1. Go to: **https://github.com/YOUR_USERNAME/SecuredOrbit/actions**
2. Watch "Deploy Pipeline" workflow run
3. Wait ~5-10 minutes for deployment to complete

## 📋 Pre-Deployment Checklist

- [ ] GitHub Secrets configured (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`)
- [ ] Elastic Beanstalk environment exists (`secured-orbit-env`)
- [ ] Environment variables set in EB (SECRET_KEY, AWS_REGION, etc.)
- [ ] IAM permissions configured (DynamoDB access)
- [ ] All code changes committed
- [ ] Ready to push to `production` branch

## 🔍 Verify Deployment

After deployment:

1. **Check EB Environment Health**:
   - AWS Console → Elastic Beanstalk → `secured-orbit-env`
   - Health should be "Ok" (green)

2. **Test Application**:
   ```bash
   # Get URL from Elastic Beanstalk dashboard
   curl http://YOUR_APP_URL/health
   # Expected: {"ok": true}
   ```

3. **Access Application**:
   - Open browser: `http://YOUR_APP_URL/`
   - Test login/register functionality

## ⚡ Quick Commands

```bash
# Check current branch
git branch

# Switch to production
git checkout production

# Merge main into production
git merge main

# Push to trigger deployment
git push origin production

# Check deployment status (if EB CLI installed)
eb status -e secured-orbit-env

# View logs (if EB CLI installed)
eb logs -e secured-orbit-env
```

## 🆘 Troubleshooting

**Workflow not triggering?**
- Ensure you're pushing to `production` branch
- Check branch name is exactly `production`

**Deployment failing?**
- Check GitHub Actions logs for error details
- Verify AWS credentials in GitHub Secrets
- Ensure EB environment name matches: `secured-orbit-env`

**Application not working?**
- Check EB environment health status
- Verify environment variables are set
- Check EB logs for errors

---

**Ready?** Run the commands in Step 2 to deploy! 🚀

