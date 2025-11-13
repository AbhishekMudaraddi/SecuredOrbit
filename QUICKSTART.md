# Quick Start Guide

## Prerequisites

1. **Python 3.9+** installed
2. **AWS Account** with DynamoDB access
3. **AWS Credentials** configured

## Step 1: Install Dependencies

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Step 2: Configure AWS Credentials

### Option A: Environment Variables

```bash
export AWS_ACCESS_KEY_ID=your-access-key
export AWS_SECRET_ACCESS_KEY=your-secret-key
export AWS_REGION=eu-north-1
```

### Option B: AWS Credentials File

Create `~/.aws/credentials`:

```ini
[default]
aws_access_key_id = your-access-key
aws_secret_access_key = your-secret-key
region = eu-north-1
```

### Option C: .env File

```bash
# Copy example file
cp .env.example .env

# Edit .env and add your credentials
nano .env  # or use your preferred editor
```

## Step 3: Create DynamoDB Tables

```bash
# Run setup script
python setup.py
```

This will create the following tables:
- `PasswordManager-Users`
- `PasswordManager-Accounts`
- `PasswordManager-Passwords`

## Step 4: Run the Application

```bash
python app.py
```

The application will be available at `http://localhost:5000`

## Step 5: Use the Application

1. **Register**: Go to `http://localhost:5000/register` and create an account
2. **Login**: Go to `http://localhost:5000/login` and login with your credentials
3. **Add Passwords**: Enter your master password and start adding passwords

## Troubleshooting

### AWS Credentials Error

```
Error: Unable to locate credentials
```

**Solution**: Make sure AWS credentials are configured (see Step 2)

### Table Already Exists

```
ResourceInUseException: Table already exists
```

**Solution**: This is normal. The tables already exist, so you can proceed.

### Port Already in Use

```
Address already in use
```

**Solution**: Change the port in `.env` file:
```env
PORT=5001
```

### Module Not Found

```
ModuleNotFoundError: No module named 'flask'
```

**Solution**: Make sure you activated the virtual environment and installed dependencies:
```bash
source venv/bin/activate
pip install -r requirements.txt
```

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Customize the application to your needs
- Deploy to production (consider using AWS Elastic Beanstalk or EC2)

## Local DynamoDB (Optional)

If you want to use DynamoDB Local for development:

1. Download DynamoDB Local from AWS
2. Start DynamoDB Local:
   ```bash
   java -Djava.library.path=./DynamoDBLocal_lib -jar DynamoDBLocal.jar -sharedDb
   ```
3. Set in `.env`:
   ```env
   AWS_ENDPOINT=http://localhost:8000
   ```

