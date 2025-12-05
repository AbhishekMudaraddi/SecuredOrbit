# Deployment Guide - Secured Orbit

This guide will walk you through deploying your application to AWS Elastic Beanstalk using the production deployment pipeline.

## Prerequisites

Before deploying, ensure you have:

1. ✅ AWS Account with Elastic Beanstalk access
2. ✅ Elastic Beanstalk environment created: `secured-orbit-env`
3. ✅ GitHub Secrets configured (see Step 1)
4. ✅ Production branch exists in your repository

## Step 1: Configure GitHub Secrets

Go to your GitHub repository → **Settings** → **Secrets and variables** → **Actions** → **New repository secret**

Add these secrets:

| Secret Name | Description | Example |
|-------------|-------------|---------|
| `AWS_ACCESS_KEY_ID` | Your AWS access key ID | `AKIAIOSFODNN7EXAMPLE` |
| `AWS_SECRET_ACCESS_KEY` | Your AWS secret access key | `wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY` |
| `AWS_REGION` | AWS region (optional, defaults to us-east-1) | `us-east-1` |

**Important**: These secrets are used by the GitHub Actions workflow to deploy to Elastic Beanstalk.

## Step 2: Verify Elastic Beanstalk Environment

Your Elastic Beanstalk environment should already be created. Verify:

```bash
# If you have EB CLI installed locally:
eb list

# Or check in AWS Console:
# https://console.aws.amazon.com/elasticbeanstalk
```

Environment details:
- **Application Name**: `secured-orbit`
- **Environment Name**: `secured-orbit-env`
- **Region**: `us-east-1` (or your configured region)

## Step 3: Set Environment Variables in Elastic Beanstalk

Set these environment variables in your Elastic Beanstalk environment:

**Via AWS Console:**
1. Go to Elastic Beanstalk → Your Environment → Configuration
2. Click "Edit" on "Software" category
3. Add environment properties:

```
SECRET_KEY=<your-production-secret-key>
AWS_REGION=us-east-1
DYNAMODB_USERS_TABLE=PasswordManagerV2-Users
DYNAMODB_PASSWORDS_TABLE=PasswordManagerV2-Passwords
FLASK_DEBUG=false
PORT=5000
```

**Via EB CLI:**
```bash
eb setenv SECRET_KEY=your-production-secret-key \
          AWS_REGION=us-east-1 \
          DYNAMODB_USERS_TABLE=PasswordManagerV2-Users \
          DYNAMODB_PASSWORDS_TABLE=PasswordManagerV2-Passwords \
          FLASK_DEBUG=false \
          PORT=5000 \
          -e secured-orbit-env
```

## Step 4: Ensure IAM Permissions

Your Elastic Beanstalk EC2 instance role needs DynamoDB permissions. Verify:

1. Go to IAM → Roles → `aws-elasticbeanstalk-ec2-role`
2. Attach policy with DynamoDB permissions (if not already attached)

Required permissions:
- `dynamodb:GetItem`
- `dynamodb:PutItem`
- `dynamodb:UpdateItem`
- `dynamodb:DeleteItem`
- `dynamodb:Query`
- `dynamodb:Scan`
- `dynamodb:CreateTable`
- `dynamodb:DescribeTable`

## Step 5: Merge Changes to Production Branch

### Option A: Merge from main (Recommended)

```bash
# 1. Ensure you're on main branch with latest changes
git checkout main
git pull origin main

# 2. Merge main into production
git checkout production
git pull origin production
git merge main

# 3. Push to trigger deployment
git push origin production
```

### Option B: Direct Push to Production

```bash
# 1. Checkout production branch
git checkout production

# 2. Merge or cherry-pick your changes
git merge main  # or cherry-pick specific commits

# 3. Push to trigger deployment
git push origin production
```

## Step 6: Monitor Deployment

After pushing to `production` branch:

1. **Go to GitHub Actions**: https://github.com/YOUR_USERNAME/SecuredOrbit/actions
2. **Watch the workflow run**: Look for "Deploy Pipeline" workflow
3. **Monitor the steps**:
   - ✅ Quick Validation (runs first)
   - ✅ Deploy to AWS Elastic Beanstalk (runs after validation)

### Expected Timeline:
- Validation: ~1-2 minutes
- Deployment: ~5-10 minutes (depends on Elastic Beanstalk)

## Step 7: Verify Deployment

After deployment completes:

1. **Check Elastic Beanstalk Health**:
   - Go to AWS Console → Elastic Beanstalk → Your Environment
   - Verify health status is "Ok" (green)

2. **Test the Application**:
   ```bash
   # Get your application URL from Elastic Beanstalk
   # It should look like: http://secured-orbit-env.elasticbeanstalk.com
   
   # Test health endpoint
   curl http://YOUR_APP_URL/health
   # Expected: {"ok": true}
   ```

3. **Access the Application**:
   - Landing page: `http://YOUR_APP_URL/`
   - Login: `http://YOUR_APP_URL/login`
   - Register: `http://YOUR_APP_URL/register`

## Deployment Pipeline Overview

```
┌─────────────────────────────────────────────────────┐
│  DEPLOYMENT PIPELINE FLOW                          │
├─────────────────────────────────────────────────────┤
│                                                     │
│  1. Push to production branch                       │
│           ↓                                         │
│  2. GitHub Actions triggers                         │
│           ↓                                         │
│  3. Quick Validation Job                            │
│     • Checkout code                                 │
│     • Install dependencies                          │
│     • Validate Python syntax                        │
│     • Test imports                                  │
│           ↓                                         │
│  4. Deploy Job (if validation passes)               │
│     • Checkout code                                 │
│     • Install EB CLI                                │
│     • Configure AWS credentials                     │
│     • Deploy to Elastic Beanstalk                   │
│           ↓                                         │
│  5. Application deployed!                           │
│                                                     │
└─────────────────────────────────────────────────────┘
```

## Troubleshooting

### Deployment Fails - AWS Credentials Error

**Error**: `Unable to locate credentials`

**Solution**: 
- Verify GitHub Secrets are correctly set (Step 1)
- Check secret names match exactly: `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`

### Deployment Fails - Environment Not Found

**Error**: `Environment secured-orbit-env not found`

**Solution**:
- Verify environment name in deploy.yml matches your EB environment
- Create environment if it doesn't exist: `eb create secured-orbit-env`

### Application Health Check Fails

**Error**: Application returns 502 or health check fails

**Solution**:
- Check Elastic Beanstalk logs: `eb logs` or AWS Console
- Verify environment variables are set correctly
- Check SECRET_KEY is set in EB environment
- Verify DynamoDB IAM permissions are attached

### Database Connection Errors

**Error**: `UnrecognizedClientException` or `NoCredentialsError`

**Solution**:
- Verify EC2 instance role has DynamoDB permissions
- Check IAM role is attached to Elastic Beanstalk environment
- Verify environment variables are set (AWS_REGION, table names)

## Quick Deployment Checklist

Before deploying, ensure:

- [ ] GitHub Secrets configured (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`)
- [ ] Elastic Beanstalk environment exists (`secured-orbit-env`)
- [ ] Environment variables set in Elastic Beanstalk
- [ ] IAM permissions configured for DynamoDB
- [ ] All code changes committed and ready
- [ ] Production branch is up to date

## Next Steps After Deployment

1. **Monitor Application**: Check logs for any errors
2. **Test All Features**: Register, login, password management
3. **Verify Security**: Check security headers are working
4. **Set Up Monitoring**: Configure CloudWatch alarms if needed

## Rollback (If Needed)

If deployment causes issues, rollback:

```bash
# Via AWS Console:
# Go to Elastic Beanstalk → Environment → Application versions → Deploy previous version

# Via EB CLI:
eb deploy secured-orbit-env --version previous-version-label
```

## Support

If you encounter issues:
1. Check GitHub Actions logs for detailed error messages
2. Check Elastic Beanstalk logs: `eb logs` or AWS Console
3. Verify all prerequisites are met (Steps 1-4)

---

**Ready to deploy?** Follow Steps 5-7 to push to production branch and monitor the deployment!

