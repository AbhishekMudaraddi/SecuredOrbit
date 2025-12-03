# Quick Start Guide

Follow these steps to get your Password Manager V2 running locally:

## Step 1: Create Virtual Environment

```bash
cd /Users/abhishekmudaraddi/Desktop/DEVSECOPSv2
python3 -m venv venv
source venv/bin/activate
```

## Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

## Step 3: Configure AWS Credentials

Create a `.env` file:

```bash
cp env.example .env
```

Then edit `.env` and add your AWS credentials:

```env
SECRET_KEY=your-secret-key-here
PORT=5000

AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
AWS_REGION=us-east-1

DYNAMODB_USERS_TABLE=PasswordManagerV2-Users
DYNAMODB_PASSWORDS_TABLE=PasswordManagerV2-Passwords
```

## Step 4: Run the Application

```bash
python app.py
```

You should see:
```
🚀 Initializing DynamoDB tables...
✅ Starting Flask application...
 * Running on http://0.0.0.0:5000
```

## Step 5: Access the Application

Open your browser:
- **Home**: http://localhost:5000
- **Register**: http://localhost:5000/register

## What Happens Next?

1. **First Run**: DynamoDB tables will be created automatically
2. **Register**: Create a new user account
3. **Login**: Login with your credentials
4. **Add Passwords**: Store your first password

## Troubleshooting

### "NoCredentialsError"
- Make sure your `.env` file has correct AWS credentials
- Or set environment variables: `export AWS_ACCESS_KEY_ID=...`

### "Table already exists"
- This is normal if you've run the app before
- The app will continue normally

### Port 5000 already in use
- Change `PORT=5001` in your `.env` file
- Or stop the other application using port 5000

## Notes

- ✅ Uses **NEW table names** (`PasswordManagerV2-*`) - won't conflict with existing app
- ✅ All passwords are **encrypted** before storing
- ✅ Runs **locally** - no deployment needed for now

## Next Steps

Once running, you can:
1. Register a user
2. Add passwords
3. View/edit/delete passwords
4. Learn how the code works step by step!

