# Fix IAM Permissions for DynamoDB Access

## Problem

The Elastic Beanstalk EC2 instance role doesn't have permissions to access DynamoDB, causing login errors:
```
AccessDeniedException: User is not authorized to perform: dynamodb:GetItem
```

## Solution: Grant DynamoDB Permissions to EC2 Instance Role

### Step 1: Find the Instance Profile Role Name

The role name is: `aws-elasticbeanstalk-ec2-role`

### Step 2: Attach DynamoDB Policy via AWS Console

1. Go to AWS IAM Console: https://console.aws.amazon.com/iam/
2. Click "Roles" in the left sidebar
3. Search for: `aws-elasticbeanstalk-ec2-role`
4. Click on the role
5. Click "Add permissions" → "Create inline policy"
6. Click "JSON" tab
7. Copy and paste the policy from `dynamodb-policy.json`:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "dynamodb:GetItem",
        "dynamodb:PutItem",
        "dynamodb:UpdateItem",
        "dynamodb:DeleteItem",
        "dynamodb:Query",
        "dynamodb:Scan",
        "dynamodb:CreateTable",
        "dynamodb:DescribeTable"
      ],
      "Resource": [
        "arn:aws:dynamodb:us-east-1:503561414328:table/PasswordManagerV2-Users",
        "arn:aws:dynamodb:us-east-1:503561414328:table/PasswordManagerV2-Users/index/*",
        "arn:aws:dynamodb:us-east-1:503561414328:table/PasswordManagerV2-Passwords",
        "arn:aws:dynamodb:us-east-1:503561414328:table/PasswordManagerV2-Passwords/index/*"
      ]
    }
  ]
}
```

8. Click "Next"
9. Name the policy: `DynamoDBAccessPolicy`
10. Click "Create policy"

### Step 3: Verify Permissions

After attaching the policy, try logging in again. The error should be resolved.

### Alternative: Use AWS CLI

If you have AWS CLI configured:

```bash
aws iam put-role-policy \
  --role-name aws-elasticbeanstalk-ec2-role \
  --policy-name DynamoDBAccessPolicy \
  --policy-document file://dynamodb-policy.json
```

## Verify It's Working

After attaching the policy:
1. Wait 1-2 minutes for permissions to propagate
2. Try logging in again
3. Check the error message - it should be gone

## Notes

- The policy grants read/write access to both DynamoDB tables
- It includes permissions for indexes (needed for email lookups)
- Permissions are scoped to only your specific tables for security

