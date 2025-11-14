# Update Jenkinsfile for AWS Credentials

## Current Status

Your AWS credentials ID in Jenkins is: `aws-cred` (not `aws-credentials`)

## Analysis

Looking at the Jenkinsfile, it currently uses AWS CLI commands directly:
```groovy
aws ecr get-login-password --region ${AWS_REGION} | docker login ...
```

This means it relies on:
1. AWS CLI being configured (`aws configure`)
2. OR AWS credentials from environment variables
3. OR AWS credentials from Jenkins credentials (if bound)

## Options

### Option 1: Use AWS CLI Configuration (Current - Recommended)

If you've run `aws configure` on your local machine, Jenkins will use those credentials automatically. **No changes needed** to Jenkinsfile.

**Verify**:
```bash
aws sts get-caller-identity
# Should show your AWS account info
```

### Option 2: Use Jenkins Credentials Binding

If you want Jenkins to explicitly use the `aws-cred` credentials, update the Jenkinsfile to bind them.

**Update the "Docker Build & Push" stage**:

```groovy
stage('Docker Build & Push') {
    steps {
        script {
            // Bind AWS credentials
            withCredentials([[
                $class: 'AmazonWebServicesCredentialsBinding',
                credentialsId: 'aws-cred',  // Your credentials ID
                accessKeyVariable: 'AWS_ACCESS_KEY_ID',
                secretKeyVariable: 'AWS_SECRET_ACCESS_KEY'
            ]]) {
                // Rest of the stage code...
            }
        }
    }
}
```

### Option 3: Keep Current Setup (Simplest)

Since you're using local Jenkins and likely have `aws configure` set up, **the current Jenkinsfile should work without changes**.

The AWS CLI will automatically use your configured credentials.

---

## Recommendation

**Keep the current setup** (Option 1/3) - it's simpler and works well for local Jenkins.

Only use Option 2 if:
- You want to use different AWS credentials for Jenkins than your local machine
- You want explicit credential management in Jenkins
- You're running Jenkins in a different environment

---

## Verify AWS Access

Test that Jenkins can access AWS:

```bash
# From your local machine (where Jenkins runs)
aws sts get-caller-identity

# Should show your AWS account info
# If this works, Jenkins pipeline will work too
```

---

## Summary

- ✅ **Current Jenkinsfile**: Works with `aws configure` credentials
- ✅ **No changes needed** if AWS CLI is configured
- ✅ **Optional**: Can add credential binding if you prefer explicit Jenkins credentials

**Your setup should work as-is!** 🎉

