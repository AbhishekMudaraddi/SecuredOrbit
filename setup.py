#!/usr/bin/env python3
"""
Setup script to initialize DynamoDB tables
"""
import os
import sys
from dotenv import load_dotenv
import boto3
from botocore.exceptions import ClientError

# Load environment variables
load_dotenv()

# AWS Configuration
AWS_REGION = os.getenv('AWS_REGION', 'eu-north-1')
AWS_ENDPOINT = os.getenv('AWS_ENDPOINT', None)
DYNAMODB_USERS_TABLE = os.getenv('DYNAMODB_USERS_TABLE', 'PasswordManager-Users')
DYNAMODB_ACCOUNTS_TABLE = os.getenv('DYNAMODB_ACCOUNTS_TABLE', 'PasswordManager-Accounts')
DYNAMODB_PASSWORDS_TABLE = os.getenv('DYNAMODB_PASSWORDS_TABLE', 'PasswordManager-Passwords')

# Initialize DynamoDB client
dynamodb_config = {
    'region_name': AWS_REGION
}
if AWS_ENDPOINT:
    dynamodb_config['endpoint_url'] = AWS_ENDPOINT

dynamodb_client = boto3.client('dynamodb', **dynamodb_config)

def create_tables():
    """Create DynamoDB tables"""
    tables = [
        {
            'TableName': DYNAMODB_USERS_TABLE,
            'KeySchema': [
                {'AttributeName': 'username', 'KeyType': 'HASH'}
            ],
            'AttributeDefinitions': [
                {'AttributeName': 'username', 'AttributeType': 'S'},
                {'AttributeName': 'email_lower', 'AttributeType': 'S'}
            ],
            'BillingMode': 'PAY_PER_REQUEST',
            'GlobalSecondaryIndexes': [
                {
                    'IndexName': 'EmailIndex',
                    'KeySchema': [
                        {'AttributeName': 'email_lower', 'KeyType': 'HASH'}
                    ],
                    'Projection': {
                        'ProjectionType': 'ALL'
                    }
                }
            ]
        },
        {
            'TableName': DYNAMODB_ACCOUNTS_TABLE,
            'KeySchema': [
                {'AttributeName': 'account_id', 'KeyType': 'HASH'}
            ],
            'AttributeDefinitions': [
                {'AttributeName': 'account_id', 'AttributeType': 'S'}
            ],
            'BillingMode': 'PAY_PER_REQUEST'
        },
        {
            'TableName': DYNAMODB_PASSWORDS_TABLE,
            'KeySchema': [
                {'AttributeName': 'user_id', 'KeyType': 'HASH'},
                {'AttributeName': 'password_id', 'KeyType': 'RANGE'}
            ],
            'AttributeDefinitions': [
                {'AttributeName': 'user_id', 'AttributeType': 'S'},
                {'AttributeName': 'password_id', 'AttributeType': 'S'}
            ],
            'BillingMode': 'PAY_PER_REQUEST'
        }
    ]
    
    for table_def in tables:
        try:
            print(f"Creating table: {table_def['TableName']}...")
            dynamodb_client.create_table(**table_def)
            print(f"✓ Table {table_def['TableName']} created successfully")
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceInUseException':
                print(f"✓ Table {table_def['TableName']} already exists")
            else:
                print(f"✗ Error creating table {table_def['TableName']}: {e}")
                sys.exit(1)

def check_aws_credentials():
    """Check if AWS credentials are configured"""
    # Check if credentials are set
    access_key = os.getenv('AWS_ACCESS_KEY_ID')
    secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
    
    if not access_key or not secret_key or access_key == 'your-aws-access-key' or secret_key == 'your-aws-secret-key':
        print("✗ AWS credentials not configured or using placeholder values")
        print("\nPlease configure AWS credentials in one of the following ways:")
        print("\n1. Edit .env file and add your AWS credentials:")
        print("   AWS_ACCESS_KEY_ID=your-actual-access-key")
        print("   AWS_SECRET_ACCESS_KEY=your-actual-secret-key")
        print("   AWS_REGION=eu-north-1")
        print("\n2. Set environment variables:")
        print("   export AWS_ACCESS_KEY_ID=your-access-key")
        print("   export AWS_SECRET_ACCESS_KEY=your-secret-key")
        print("   export AWS_REGION=eu-north-1")
        print("\n3. Create ~/.aws/credentials file:")
        print("   [default]")
        print("   aws_access_key_id = your-access-key")
        print("   aws_secret_access_key = your-secret-key")
        print("   region = eu-north-1")
        print("\n4. For local development, you can use DynamoDB Local:")
        print("   - Download DynamoDB Local from AWS")
        print("   - Start it: java -jar DynamoDBLocal.jar -sharedDb")
        print("   - Set in .env: AWS_ENDPOINT=http://localhost:8000")
        print("\nTo get AWS credentials:")
        print("1. Go to AWS Console -> IAM -> Users -> Your User -> Security Credentials")
        print("2. Create Access Key")
        print("3. Make sure your IAM user has DynamoDB permissions")
        return False
    
    try:
        dynamodb_client.list_tables()
        print("✓ AWS credentials are configured correctly")
        return True
    except ClientError as e:
        error_code = e.response.get('Error', {}).get('Code', '')
        error_message = e.response.get('Error', {}).get('Message', str(e))
        
        print(f"✗ AWS credentials error: {error_message}")
        
        if 'UnrecognizedClientException' in error_code or 'InvalidClientTokenId' in error_code:
            print("\nThe AWS credentials are invalid or expired.")
            print("Please check:")
            print("1. Your AWS_ACCESS_KEY_ID is correct")
            print("2. Your AWS_SECRET_ACCESS_KEY is correct")
            print("3. Your IAM user has DynamoDB permissions")
            print("4. Your credentials haven't expired")
        elif 'AccessDeniedException' in error_code:
            print("\nYour IAM user doesn't have permission to access DynamoDB.")
            print("Please add DynamoDB permissions to your IAM user.")
        
        return False

if __name__ == '__main__':
    print("Password Manager - DynamoDB Setup")
    print("=" * 40)
    
    if not check_aws_credentials():
        sys.exit(1)
    
    print("\nCreating DynamoDB tables...")
    create_tables()
    
    print("\n" + "=" * 40)
    print("Setup complete!")
    print("\nYou can now run the application with: python app.py")

