# Password Manager - Flask & DynamoDB

A simple password manager application built with Flask, HTML, CSS, JavaScript, and Amazon DynamoDB.

## Features

- 🔐 User authentication with unique email enforcement
- 📲 Google Authenticator (TOTP) two-factor authentication
- 🔁 Recovery words (5-word phrase) for password resets
- 📊 Live password strength indicators (registration & vault)
- 💾 Encrypted password storage in DynamoDB (Fernet symmetric encryption)
- 🔍 Instant search across saved passwords (website / username / notes)
- 🎨 Clean, responsive HTML/CSS/JS frontend

## Prerequisites

- Python 3.9+
- AWS Account with DynamoDB access
- AWS Credentials configured

## Installation

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd password-manager
```

### 2. Create virtual environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure AWS Credentials

You can configure AWS credentials in one of the following ways:

#### Option A: Environment variables

```bash
export AWS_ACCESS_KEY_ID=your-access-key
export AWS_SECRET_ACCESS_KEY=your-secret-key
export AWS_REGION=eu-north-1
```

#### Option B: AWS credentials file

Create `~/.aws/credentials`:

```ini
[default]
aws_access_key_id = your-access-key
aws_secret_access_key = your-secret-key
region = eu-north-1
```

#### Option C: .env file

Create a `.env` file from `.env.example`:

```bash
cp .env.example .env
```

Edit `.env` and add your AWS credentials:

```env
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_REGION=eu-north-1
SECRET_KEY=your-secret-key-for-flask-sessions
```

### 5. Initialize DynamoDB Tables

The tables will be created automatically when you first run the application. The following tables will be created:

- `PasswordManager-Users` - Stores user accounts
- `PasswordManager-Accounts` - Reserved for future use
- `PasswordManager-Passwords` - Stores encrypted passwords

### 6. Run the application

```bash
python app.py
```

The application will be available at `http://localhost:5000`

## Usage

### 1. Register a new account

1. Navigate to `http://localhost:5000/register`
2. Enter email, username, and password (watch the live strength indicator)
3. Scan the QR code with Google Authenticator and verify the 6-digit code
4. Save the 5 recovery words in a secure location

### 2. Login

1. Navigate to `http://localhost:5000/login`
2. Enter your username and password
3. Enter the 6-digit code from Google Authenticator
4. Click "Login"

### 3. Manage Passwords

1. After login, your passwords load automatically
2. Click "Add New Password" to store new credentials
3. Use "Edit" or "Delete" to manage existing entries

## Project Structure

```
password-manager/
├── app.py                 # Flask application
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
├── templates/            # HTML templates
│   ├── base.html
│   ├── login.html
│   ├── register.html
│   └── dashboard.html
├── static/               # Static files
│   ├── css/
│   │   └── style.css
│   └── js/
│       ├── main.js
│       └── dashboard.js
└── README.md
```

## DynamoDB Tables

### PasswordManager-Users
- **Primary Key**: `username` (String)
- **Attributes**: 
  - `user_id` (String)
  - `email` (String)
  - `email_lower` (String)
  - `password_hash` (String)
  - `totp_secret` (String)
  - `totp_enabled` (Boolean)
  - `encryption_key` (String)
  - `recovery_phrase_hash` (String)
  - `created_at` (String)

### PasswordManager-Passwords
- **Primary Key**: 
  - `password_id` (String) - Partition Key
  - `user_id` (String) - Sort Key
- **Attributes**:
  - `website` (String)
  - `username` (String)
  - `encrypted_password` (String)
  - `notes` (String)
  - `created_at` (String)

## Security Features

- **Password Hashing**: Uses bcrypt for secure password hashing
- **Encryption Key**: Each user has a dedicated Fernet encryption key (password resets do not affect stored data)
- **Two-Factor Authentication**: Google Authenticator (TOTP) required at registration and login
- **Recovery Phrase**: Five recovery words hashed and stored for account recovery
- **Session Management**: Flask sessions for user authentication

## Configuration

### Environment Variables

- `FLASK_ENV`: Flask environment (development/production)
- `SECRET_KEY`: Secret key for Flask sessions
- `PORT`: Port to run the application on (default: 5000)
- `AWS_ACCESS_KEY_ID`: AWS access key
- `AWS_SECRET_ACCESS_KEY`: AWS secret key
- `AWS_REGION`: AWS region (default: eu-north-1)
- `AWS_ENDPOINT`: Optional endpoint for local DynamoDB
- `DYNAMODB_USERS_TABLE`: Users table name (default: PasswordManager-Users)
- `DYNAMODB_ACCOUNTS_TABLE`: Accounts table name (default: PasswordManager-Accounts)
- `DYNAMODB_PASSWORDS_TABLE`: Passwords table name (default: PasswordManager-Passwords)

## Local DynamoDB (Optional)

To use DynamoDB Local for development:

1. Download DynamoDB Local from AWS
2. Start DynamoDB Local:
   ```bash
   java -Djava.library.path=./DynamoDBLocal_lib -jar DynamoDBLocal.jar -sharedDb
   ```
3. Set `AWS_ENDPOINT=http://localhost:8000` in your `.env` file

## Troubleshooting

### AWS Credentials Error

Make sure your AWS credentials are configured correctly. Check:
- Environment variables are set
- AWS credentials file exists and is correct
- IAM user has DynamoDB permissions

### Table Creation Error

If tables already exist, the application will continue normally. If you see errors, check:
- AWS credentials
- IAM permissions for DynamoDB
- Region configuration

### Port Already in Use

Change the port in your `.env` file:
```env
PORT=5001
```

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

