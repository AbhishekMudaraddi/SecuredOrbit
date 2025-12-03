# Password Manager V2

A simple Flask-based password manager that stores encrypted passwords in Amazon DynamoDB.

## Features

- 🔐 User authentication (username/password)
- 💾 Encrypted password storage (Fernet encryption)
- 🌐 Store passwords for different websites/services
- 🔍 View, add, edit, and delete stored passwords
- 🔒 Secure - passwords are encrypted before storing in DynamoDB

## Prerequisites

- Python 3.9+
- AWS Account with DynamoDB access
- AWS Credentials configured

## Setup Instructions

### 1. Install Dependencies

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure AWS Credentials

Create a `.env` file from the example:

```bash
cp env.example .env
```

Edit `.env` and add your AWS credentials:

```env
# Flask Configuration
FLASK_ENV=development
SECRET_KEY=your-secret-key-here-change-in-production
PORT=5000

# AWS Configuration
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
AWS_REGION=us-east-1

# DynamoDB Tables (New tables - won't conflict with existing app)
DYNAMODB_USERS_TABLE=PasswordManagerV2-Users
DYNAMODB_PASSWORDS_TABLE=PasswordManagerV2-Passwords
```

### 3. AWS Credentials Setup

You can configure AWS credentials in one of these ways:

**Option A: Environment Variables**
```bash
export AWS_ACCESS_KEY_ID=your-access-key
export AWS_SECRET_ACCESS_KEY=your-secret-key
export AWS_REGION=us-east-1
```

**Option B: AWS Credentials File**
Create `~/.aws/credentials`:
```ini
[default]
aws_access_key_id = your-access-key
aws_secret_access_key = your-secret-key
region = us-east-1
```

**Option C: .env File (Recommended)**
Use the `.env` file as shown in step 2.

### 4. Run the Application

```bash
python app.py
```

The application will:
- Automatically create DynamoDB tables if they don't exist
- Start Flask development server on `http://localhost:5000`

### 5. Access the Application

Open your browser and go to:
- **Home**: http://localhost:5000
- **Register**: http://localhost:5000/register
- **Login**: http://localhost:5000/login
- **Health Check**: http://localhost:5000/health

## Project Structure

```
DEVSECOPSv2/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── env.example           # Environment variables template
├── .gitignore            # Git ignore file
├── README.md             # This file
├── templates/            # HTML templates
│   ├── base.html
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   └── dashboard.html
└── static/               # Static files
    ├── css/
    │   └── style.css
    └── js/
        ├── dashboard.js
        └── main.js
```

## How It Works

### User Registration
1. User registers with username and password
2. Password is hashed using bcrypt
3. User record is stored in DynamoDB `PasswordManagerV2-Users` table

### Password Storage
1. User logs in with username/password
2. Encryption key is generated from user_id + password
3. When storing a password:
   - Password is encrypted using Fernet encryption
   - Encrypted password is stored in DynamoDB `PasswordManagerV2-Passwords` table
4. When retrieving passwords:
   - Encrypted passwords are decrypted using the same key
   - Plain text passwords are displayed (only after login)

### DynamoDB Tables

**PasswordManagerV2-Users**
- Primary Key: `username` (String)
- Attributes: `user_id`, `password_hash`, `created_at`

**PasswordManagerV2-Passwords**
- Primary Key: `user_id` (String) + `password_id` (String)
- Attributes: `website`, `username`, `encrypted_password`, `notes`, `created_at`

## Security Notes

- ✅ Passwords are encrypted before storing (Fernet encryption)
- ✅ User passwords are hashed (bcrypt)
- ✅ Encryption key is derived from user credentials
- ⚠️ Session stores password temporarily (for encryption key generation)
- ⚠️ For production, consider using proper session management

## Development

### Running in Development Mode

```bash
export FLASK_ENV=development
python app.py
```

### Health Check

```bash
curl http://localhost:5000/health
# Returns: {"ok": true}
```

## Troubleshooting

### AWS Credentials Error

**Error**: `botocore.exceptions.NoCredentialsError: Unable to locate credentials`

**Solution**: Ensure AWS credentials are configured (see step 2)

### DynamoDB Table Creation Error

If tables already exist, the application will continue normally. The tables are created automatically on first run.

### Port Already in Use

Change the port in your `.env` file:
```env
PORT=5001
```

## Next Steps

- [ ] Add password reset functionality
- [ ] Add email verification
- [ ] Implement better session management
- [ ] Add password strength indicators
- [ ] Add search functionality
- [ ] Deploy to production

## License

MIT License

