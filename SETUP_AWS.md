# Setting Up AWS Credentials for DynamoDB

## Quick Setup Guide

### Option 1: Using .env File (Recommended for Development)

1. **Edit your `.env` file**:
   ```bash
   nano .env
   # or
   open .env
   ```

2. **Replace the placeholder values** with your actual AWS credentials:
   ```env
   AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
   AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
   AWS_REGION=eu-north-1
   ```

3. **Save the file** and run setup again:
   ```bash
   python setup.py
   ```

### Option 2: Get AWS Credentials

If you don't have AWS credentials yet:

1. **Create an AWS Account** (if you don't have one):
   - Go to https://aws.amazon.com/
   - Sign up for an account

2. **Create an IAM User**:
   - Go to AWS Console → IAM → Users
   - Click "Add users"
   - Enter a username (e.g., `password-manager-user`)
   - Select "Programmatic access"
   - Click "Next"

3. **Attach DynamoDB Permissions**:
   - Click "Attach existing policies directly"
   - Search for "DynamoDB" and select:
     - `AmazonDynamoDBFullAccess` (for full access)
     - OR create a custom policy with these permissions:
       ```json
       {
         "Version": "2012-10-17",
         "Statement": [
           {
             "Effect": "Allow",
             "Action": [
               "dynamodb:CreateTable",
               "dynamodb:DescribeTable",
               "dynamodb:PutItem",
               "dynamodb:GetItem",
               "dynamodb:UpdateItem",
               "dynamodb:DeleteItem",
               "dynamodb:Query",
               "dynamodb:Scan",
               "dynamodb:ListTables"
             ],
             "Resource": "*"
           }
         ]
       }
       ```

4. **Create Access Key**:
   - After creating the user, go to "Security credentials" tab
   - Click "Create access key"
   - Choose "Application running outside AWS"
   - Click "Next" and then "Create access key"
   - **IMPORTANT**: Copy both the Access Key ID and Secret Access Key
   - You won't be able to see the secret key again!

5. **Add Credentials to .env**:
   ```env
   AWS_ACCESS_KEY_ID=your-access-key-id-here
   AWS_SECRET_ACCESS_KEY=your-secret-access-key-here
   AWS_REGION=eu-north-1
   ```

### Option 3: Use AWS CLI

1. **Install AWS CLI**:
   ```bash
   pip install awscli
   # or
   brew install awscli  # on macOS
   ```

2. **Configure AWS CLI**:
   ```bash
   aws configure
   ```
   
   Enter:
   - AWS Access Key ID: `your-access-key`
   - AWS Secret Access Key: `your-secret-key`
   - Default region: `eu-north-1`
   - Default output format: `json`

3. **Verify Configuration**:
   ```bash
   aws dynamodb list-tables
   ```

### Option 4: Use DynamoDB Local (For Development)

If you want to develop without AWS:

1. **Download DynamoDB Local**:
   ```bash
   # Create a directory for DynamoDB Local
   mkdir -p ~/dynamodb-local
   cd ~/dynamodb-local
   
   # Download (macOS/Linux)
   curl -O https://s3.us-west-2.amazonaws.com/dynamodb-local/dynamodb_local_latest.tar.gz
   tar -xzf dynamodb_local_latest.tar.gz
   ```

2. **Start DynamoDB Local**:
   ```bash
   java -Djava.library.path=./DynamoDBLocal_lib -jar DynamoDBLocal.jar -sharedDb
   ```

3. **Update .env file**:
   ```env
   AWS_ENDPOINT=http://localhost:8000
   AWS_ACCESS_KEY_ID=dummy
   AWS_SECRET_ACCESS_KEY=dummy
   AWS_REGION=us-east-1
   ```

4. **Run setup**:
   ```bash
   python setup.py
   ```

## Troubleshooting

### Error: "UnrecognizedClientException" or "InvalidClientTokenId"
- Your AWS credentials are invalid or incorrect
- Check that you copied the credentials correctly
- Make sure there are no extra spaces

### Error: "AccessDeniedException"
- Your IAM user doesn't have DynamoDB permissions
- Add DynamoDB permissions to your IAM user (see Option 2)

### Error: "Region not found"
- Make sure AWS_REGION is set correctly
- Valid regions: `us-east-1`, `eu-north-1`, `ap-south-1`, etc.

### Error: "Table already exists"
- This is normal if tables were already created
- You can continue using the application

## Security Best Practices

1. **Never commit .env file to git** (it's already in .gitignore)
2. **Use IAM users with minimal permissions** (not root account)
3. **Rotate access keys regularly**
4. **Use environment variables in production** instead of .env file
5. **For production**, use AWS IAM roles instead of access keys

## Next Steps

After setting up credentials:

1. Run `python setup.py` to create tables
2. Run `python app.py` to start the application
3. Open `http://localhost:5000` in your browser

## Need Help?

- Check AWS IAM documentation: https://docs.aws.amazon.com/iam/
- Check DynamoDB documentation: https://docs.aws.amazon.com/dynamodb/
- Check boto3 documentation: https://boto3.amazonaws.com/v1/documentation/api/latest/index.html

