# Getting Started - Password Manager

## ✅ Setup Complete!

Your DynamoDB tables have been created successfully:
- ✓ PasswordManager-Users
- ✓ PasswordManager-Accounts  
- ✓ PasswordManager-Passwords

## 🚀 Running the Application

### Step 1: Activate Virtual Environment

```bash
source venv/bin/activate
```

### Step 2: Start the Application

```bash
python app.py
```

You should see:
```
Initializing DynamoDB tables...
Starting Flask application...
 * Running on http://0.0.0.0:5000
```

### Step 3: Open in Browser

Open your browser and go to:
```
http://localhost:5000
```

## 📝 First Time Usage

1. **Register a New Account**:
   - Click "Register" or go to `http://localhost:5000/register`
   - Enter a username and password
   - Click "Register"

2. **Login**:
   - Go to `http://localhost:5000/login`
   - Enter your username and password
   - Click "Login"

3. **Add Your First Password**:
   - Enter your master password (this is used to encrypt/decrypt your passwords)
   - Click "Load Passwords"
   - Click "Add New Password"
   - Fill in the website, username, password, and optional notes
   - Click "Save"

## 🔧 Troubleshooting

### Virtual Environment Not Activated

If you see `ModuleNotFoundError`, activate the virtual environment:
```bash
source venv/bin/activate
```

### Port Already in Use

If port 5000 is already in use, change it in `.env`:
```env
PORT=5001
```

### AWS Credentials Error

If you see AWS errors:
1. Check your `.env` file has valid AWS credentials
2. Make sure your IAM user has DynamoDB permissions
3. See `SETUP_AWS.md` for detailed instructions

### Tables Already Exist

If you see "Table already exists" errors, that's fine! The tables are already created and ready to use.

## 📚 Next Steps

- Read `README.md` for full documentation
- Read `SETUP_AWS.md` for AWS configuration details
- Read `QUICKSTART.md` for quick reference

## 🎉 You're Ready!

Your password manager is now set up and ready to use. Start adding your passwords securely!

