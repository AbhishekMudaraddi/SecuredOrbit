
import os
import json
import io
import base64
import hashlib
import re
from datetime import datetime
from uuid import uuid4


from flask_wtf import CSRFProtect

import pyotp
import qrcode

import boto3
import bcrypt
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key, Attr
from cryptography.fernet import Fernet
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from dotenv import load_dotenv


load_dotenv()

app = Flask(__name__)


secret_key = os.getenv('SECRET_KEY') or os.environ.get('SECRET_KEY')


if not secret_key:
 
    import sys
    print("ERROR: SECRET_KEY environment variable is not set!", file=sys.stderr)
    print(f"Available environment variables: {sorted(list(os.environ.keys()))}", file=sys.stderr)
    print(f"SECRET_KEY value: {repr(os.getenv('SECRET_KEY'))}", file=sys.stderr)
    print(f"FLASK_ENV: {os.getenv('FLASK_ENV')}", file=sys.stderr)
    print(f"AWS_REGION: {os.getenv('AWS_REGION')}", file=sys.stderr)
    raise ValueError("SECRET_KEY is required. Please set it in Elastic Beanstalk environment variables using: eb setenv SECRET_KEY=your-key -e secured-orbit-env")

app.secret_key = secret_key


csrf = CSRFProtect(app)
# AWS Config
AWS_REGION = os.getenv('AWS_REGION', 'us-east-1')
AWS_ENDPOINT = os.getenv('AWS_ENDPOINT', None)
DYNAMODB_USERS_TABLE = os.getenv('DYNAMODB_USERS_TABLE', 'PasswordManagerV2-Users')
DYNAMODB_PASSWORDS_TABLE = os.getenv('DYNAMODB_PASSWORDS_TABLE', 'PasswordManagerV2-Passwords')

# DynamoDB 
dynamodb_config = {
    'region_name': AWS_REGION
}
if AWS_ENDPOINT:
    dynamodb_config['endpoint_url'] = AWS_ENDPOINT

dynamodb = boto3.resource('dynamodb', **dynamodb_config)
dynamodb_client = boto3.client('dynamodb', **dynamodb_config)

# Tables
users_table = dynamodb.Table(DYNAMODB_USERS_TABLE)
passwords_table = dynamodb.Table(DYNAMODB_PASSWORDS_TABLE)


def init_dynamodb_tables():
    """Initialize DynamoDB tables if they don't exist"""
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
            dynamodb_client.create_table(**table_def)
            print(f"✅ Created table: {table_def['TableName']}")
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceInUseException':
                print(f"ℹ️  Table {table_def['TableName']} already exists")
            else:
                print(f"⚠️  Error creating table {table_def['TableName']}: {e}")


def hash_password(password):
    """Hash password using bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def check_password(hashed_password, password):
    """Check password against hash"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))


def get_encryption_key(user_id, password):
    """Generate encryption key from user_id and password"""
    key_material = f"{user_id}:{password}".encode('utf-8')
    key = base64.urlsafe_b64encode(hashlib.sha256(key_material).digest())
    return key


def encrypt_password(password_text, encryption_key):
    """Encrypt password using Fernet"""
    f = Fernet(encryption_key)
    return f.encrypt(password_text.encode('utf-8')).decode('utf-8')


def decrypt_password(encrypted_password, encryption_key):
    """Decrypt password using Fernet"""
    f = Fernet(encryption_key)
    return f.decrypt(encrypted_password.encode('utf-8')).decode('utf-8')


def generate_id():
    """Generate a unique ID"""
    return str(uuid4())


def generate_totp_secret():
    """Generate a TOTP secret"""
    return pyotp.random_base32()


def get_totp_uri(username, secret, issuer_name='Password Manager V2'):
    """Generate TOTP provisioning URI for QR code"""
    totp = pyotp.TOTP(secret)
    return totp.provisioning_uri(
        name=username,
        issuer_name=issuer_name
    )


def generate_qr_code(uri):
    """Generate QR code as base64 string"""
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(uri)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    img_str = base64.b64encode(buffer.getvalue()).decode()
    return f"data:image/png;base64,{img_str}"


def verify_totp(secret, token):
    """Verify TOTP token"""
    totp = pyotp.TOTP(secret)
    return totp.verify(token, valid_window=2)


def is_valid_email(email):
    """Validate email format"""
    if not email:
        return False
    email_regex = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'
    return re.match(email_regex, email) is not None


def email_exists(email_lower):
    """Check if email is already registered"""
    if not email_lower:
        return False
    try:
        response = users_table.query(
            IndexName='EmailIndex',
            KeyConditionExpression=Key('email_lower').eq(email_lower)
        )
        return len(response.get('Items', [])) > 0
    except ClientError as e:
        if e.response['Error']['Code'] in ('ValidationException', 'ResourceNotFoundException'):
            # If index doesn't exist yet, scan the table
            scan_response = users_table.scan(
                FilterExpression=Attr('email_lower').eq(email_lower)
            )
            return len(scan_response.get('Items', [])) > 0
        raise


# Routes
@app.route('/')
def index():
    """Landing page"""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email', '').strip()
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # Validate 
        if not username or not email or not password or not confirm_password:
            return render_template('register.html', error='Please fill in all fields', username=username, email=email)
       
        if not is_valid_email(email):
            return render_template('register.html', error='Please enter a valid email address', username=username, email=email)
        
        # Check password 
        if password != confirm_password:
            return render_template('register.html', error='Passwords do not match', username=username, email=email)
        
        # Validate 
        if len(password) < 6:
            return render_template('register.html', error='Password must be at least 6 characters', username=username, email=email)
        
        try:
            email_lower = email.lower()
            
            #  mail exist or no 
            if email_exists(email_lower):
                return render_template('register.html', error='Email is already registered', username=username, email=email)
            
            #  usernme exist or no 
            response = users_table.get_item(Key={'username': username})
            if 'Item' in response:
                return render_template('register.html', error='Username already exists', username=username, email=email)
            
            # Generate TOTP 
            totp_secret = generate_totp_secret()
            
            session['reg_username'] = username
            session['reg_email'] = email
            session['reg_email_lower'] = email_lower
            session['reg_password'] = password
            session['reg_totp_secret'] = totp_secret
            
            # Redirect to TOTP 
            return redirect(url_for('setup_totp'))
        except ClientError as e:
            return render_template('register.html', error=f'Database error: {str(e)}')
    
    return render_template('register.html')


@app.route('/setup-totp', methods=['GET', 'POST'])
def setup_totp():
    """TOTP setup page - step 2: Setup Google Authenticator"""
    if 'reg_username' not in session or 'reg_totp_secret' not in session:
        return redirect(url_for('register'))
    
    username = session['reg_username']
    totp_secret = session['reg_totp_secret']
    
    if request.method == 'POST':
        totp_token = request.form.get('totp_token')
        
        if not totp_token:
            return render_template('setup_totp.html', 
                                 username=username,
                                 totp_secret=totp_secret,
                                 error='Please enter the TOTP code')
        
        # Verify TOTP
        if not verify_totp(totp_secret, totp_token):
            return render_template('setup_totp.html', 
                                 username=username,
                                 totp_secret=totp_secret,
                                 error='Invalid TOTP code. Please try again.')
        
        # TOTP verified, proceed to complete registration
        return redirect(url_for('complete_registration'))
    
    # Generate QR code
    totp_uri = get_totp_uri(username, totp_secret)
    qr_code = generate_qr_code(totp_uri)
    
    return render_template('setup_totp.html', 
                         username=username,
                         totp_secret=totp_secret,
                         qr_code=qr_code)


@app.route('/complete-registration', methods=['GET'])
def complete_registration():
    """Complete registration - step 3: Save user to database"""
    if 'reg_username' not in session or 'reg_password' not in session or 'reg_email' not in session:
        return redirect(url_for('register'))
    
    username = session['reg_username']
    email = session['reg_email']
    email_lower = session.get('reg_email_lower', email.lower())
    password = session['reg_password']
    totp_secret = session.get('reg_totp_secret')
    
    try:
        # Create new user
        user_id = generate_id()
        users_table.put_item(Item={
            'username': username,
            'user_id': user_id,
            'email': email,
            'email_lower': email_lower,
            'password_hash': hash_password(password),
            'totp_secret': totp_secret,
            'totp_enabled': True,
            'created_at': datetime.utcnow().isoformat()
        })
        
        # Clear registration session
        session.pop('reg_username', None)
        session.pop('reg_password', None)
        session.pop('reg_email', None)
        session.pop('reg_email_lower', None)
        session.pop('reg_totp_secret', None)
        
        # Set user session
        session['user_id'] = user_id
        session['username'] = username
        session['user_password'] = password  # Store temporarily for encryption key
        
        return redirect(url_for('dashboard'))
    except ClientError as e:
        return render_template('register.html', error=f'Database error: {str(e)}')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login with TOTP verification"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        totp_token = request.form.get('totp_token')
        stored_username = session.get('login_username')
        stored_password = session.get('pending_password')
        
        # Use password stored in session during TOTP verification step
        if (not password or password.strip() == '') and stored_username and stored_password and stored_username == username:
            password = stored_password
        
        if not username or not password:
            return render_template('login.html', error='Please fill in all fields', username=username, totp_required=bool(stored_username))
        
        try:
            response = users_table.get_item(Key={'username': username})
            if 'Item' not in response:
                # Clear any stored login session data
                session.pop('login_username', None)
                session.pop('pending_password', None)
                return render_template('login.html', error='Invalid username or password')
            
            user = response['Item']
            
            # Validate user has required fields
            if 'password_hash' not in user:
                import traceback
                print(f"ERROR: User {username} missing password_hash field", file=__import__('sys').stderr)
                traceback.print_exc()
                return render_template('login.html', error='Account data error. Please contact support.')
            
            # Verify password
            if not check_password(user['password_hash'], password):
                session.pop('login_username', None)
                session.pop('pending_password', None)
                return render_template('login.html', error='Invalid username or password')
            
            # Check if TOTP is enabled
            if user.get('totp_enabled', False):
                if not totp_token:
                    # Store username and password in session for TOTP verification
                    session['login_username'] = username
                    session['pending_password'] = password
                    return render_template('login.html', 
                                         username=username, 
                                         totp_required=True)
                
                # When TOTP token is provided, use stored session credentials if available
                if stored_username and stored_password:
                    if stored_username != username or not check_password(user['password_hash'], stored_password):
                        session.pop('login_username', None)
                        session.pop('pending_password', None)
                        return render_template('login.html', error='Session expired. Please login again.')
                    # Use stored password
                    password = stored_password
                
                # Verify TOTP
                totp_secret = user.get('totp_secret')
                if not totp_secret or not verify_totp(totp_secret, totp_token):
                    return render_template('login.html', 
                                         username=username, 
                                         totp_required=True,
                                         error='Invalid TOTP code. Please try again.')
            
            # Login successful
            # Clear temporary login session
            session.pop('login_username', None)
            session.pop('pending_password', None)
            
            # Set session
            if 'user_id' not in user:
                import traceback
                print(f"ERROR: User {username} missing user_id field", file=__import__('sys').stderr)
                traceback.print_exc()
                return render_template('login.html', error='Account data error. Please contact support.')
            
            session['user_id'] = user['user_id']
            session['username'] = user.get('username', username)
            session['user_password'] = password  # Store temporarily for encryption key
            
            return redirect(url_for('dashboard'))
        except ClientError as e:
            import traceback
            error_code = e.response.get('Error', {}).get('Code', '')
            error_message = str(e)
            
            print(f"Database error during login: {error_message}", file=__import__('sys').stderr)
            traceback.print_exc()
            
            # Check for IAM/permission errors
            if 'AccessDeniedException' in error_code or 'AccessDenied' in error_message:
                print("CRITICAL: IAM permissions issue detected!", file=__import__('sys').stderr)
                print("The EC2 instance role needs DynamoDB permissions.", file=__import__('sys').stderr)
                return render_template('login.html', error='Configuration error. Please contact the administrator.')
            else:
                return render_template('login.html', error='Database error. Please try again later.')
        except Exception as e:
            import traceback
            print(f"Unexpected error during login: {str(e)}", file=__import__('sys').stderr)
            traceback.print_exc()
            return render_template('login.html', error='An unexpected error occurred. Please try again.')
    
    return render_template('login.html')


@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """Step 1: User enters username/email for password reset"""
    if request.method == 'POST':
        username_or_email = request.form.get('username_or_email', '').strip()
        
        if not username_or_email:
            return render_template('forgot_password.html', error='Please enter your username or email')
        
        try:
            # Try to find user by username first
            user = None
            response = users_table.get_item(Key={'username': username_or_email})
            
            if 'Item' in response:
                user = response['Item']
            else:
                # Try to find by email
                email_lower = username_or_email.lower()
                try:
                    email_response = users_table.query(
                        IndexName='EmailIndex',
                        KeyConditionExpression=Key('email_lower').eq(email_lower)
                    )
                    if email_response.get('Items'):
                        user = email_response['Items'][0]
                except ClientError:
                    # If index doesn't exist, scan the table
                    scan_response = users_table.scan(
                        FilterExpression=Attr('email_lower').eq(email_lower)
                    )
                    if scan_response.get('Items'):
                        user = scan_response['Items'][0]
            
            if not user:
                # Don't reveal if user exists or not (security)
                return render_template('forgot_password.html', 
                                     message='If an account exists, you will be able to reset your password.')
            
            # Check if TOTP is enabled
            if not user.get('totp_enabled', False):
                return render_template('forgot_password.html', 
                                     error='Password reset requires TOTP to be enabled. Please contact support.')
            
            # Store user info in session for next step
            session['reset_username'] = user['username']
            session['reset_user_id'] = user['user_id']
            
            return redirect(url_for('reset_password_verify'))
            
        except ClientError:
            return render_template('forgot_password.html', error='An error occurred. Please try again.')
    
    return render_template('forgot_password.html')


@app.route('/reset-password-verify', methods=['GET', 'POST'])
def reset_password_verify():
    """Step 2: User verifies TOTP code"""
    if 'reset_username' not in session:
        return redirect(url_for('forgot_password'))
    
    username = session['reset_username']
    
    if request.method == 'POST':
        totp_token = request.form.get('totp_token')
        
        if not totp_token:
            return render_template('reset_password_verify.html', 
                                 username=username,
                                 error='Please enter the TOTP code')
        
        try:
            # Get user to verify TOTP
            response = users_table.get_item(Key={'username': username})
            if 'Item' not in response:
                session.pop('reset_username', None)
                session.pop('reset_user_id', None)
                return redirect(url_for('forgot_password'))
            
            user = response['Item']
            
            # Verify TOTP
            totp_secret = user.get('totp_secret')
            if not totp_secret or not verify_totp(totp_secret, totp_token):
                return render_template('reset_password_verify.html', 
                                     username=username,
                                     error='Invalid TOTP code. Please try again.')
            
            # TOTP verified, allow password reset
            session['reset_verified'] = True
            return redirect(url_for('reset_password'))
            
        except ClientError:
            return render_template('reset_password_verify.html', 
                                 username=username,
                                 error='An error occurred. Please try again.')
    
    return render_template('reset_password_verify.html', username=username)


@app.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    """Step 3: User sets new password"""
    if 'reset_username' not in session or 'reset_verified' not in session:
        return redirect(url_for('forgot_password'))
    
    username = session['reset_username']
    user_id = session.get('reset_user_id')
    
    if request.method == 'POST':
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if not password or not confirm_password:
            return render_template('reset_password.html', 
                                 username=username,
                                 error='Please fill in all fields')
        
        if password != confirm_password:
            return render_template('reset_password.html', 
                                 username=username,
                                 error='Passwords do not match')
        
        if len(password) < 6:
            return render_template('reset_password.html', 
                                 username=username,
                                 error='Password must be at least 6 characters')
        
        try:
            # Update password in database
            users_table.update_item(
                Key={'username': username},
                UpdateExpression='SET password_hash = :ph, updated_at = :upd',
                ExpressionAttributeValues={
                    ':ph': hash_password(password),
                    ':upd': datetime.utcnow().isoformat()
                }
            )
            
            # Clear reset session
            session.pop('reset_username', None)
            session.pop('reset_user_id', None)
            session.pop('reset_verified', None)
            
            return redirect(url_for('login'))
            
        except ClientError:
            return render_template('reset_password.html', 
                                 username=username,
                                 error='Failed to reset password. Please try again.')
    
    return render_template('reset_password.html', username=username)


@app.route('/logout')
def logout():
    """Logout user"""
    session.clear()
    return redirect(url_for('index'))


@app.route('/dashboard')
def dashboard():
    """Dashboard page"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html', username=session.get('username'))


@app.route('/api/passwords', methods=['GET'])
def get_passwords():
    """Get all passwords for the current user"""
    if 'user_id' not in session or 'user_password' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    user_id = session['user_id']
    encryption_key = get_encryption_key(user_id, session['user_password'])
    
    try:
        result = []
        response = passwords_table.query(
            KeyConditionExpression=Key('user_id').eq(user_id)
        )
        
        for item in response.get('Items', []):
            try:
                decrypted_password = decrypt_password(item['encrypted_password'], encryption_key)
                result.append({
                    'id': item['password_id'],
                    'website': item.get('website', ''),
                    'username': item.get('username', ''),
                    'password': decrypted_password,
                    'notes': item.get('notes', ''),
                    'created_at': item.get('created_at', '')
                })
            except Exception as e:
                print(f"Error decrypting password: {e}")
                continue
        
        return jsonify({'passwords': result})
    except ClientError as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/passwords', methods=['POST'])
def add_password():
    """Add a new password"""
    if 'user_id' not in session or 'user_password' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    data = request.get_json()
    website = data.get('website')
    username = data.get('username')
    password = data.get('password')
    notes = data.get('notes')
    
    if not website or not password:
        return jsonify({'error': 'Website and password are required'}), 400
    
    user_id = session['user_id']
    encryption_key = get_encryption_key(user_id, session['user_password'])
    
    try:
        encrypted_password = encrypt_password(password, encryption_key)
        password_id = generate_id()
        
        passwords_table.put_item(Item={
            'user_id': user_id,
            'password_id': password_id,
            'website': website,
            'username': username or '',
            'encrypted_password': encrypted_password,
            'notes': notes or '',
            'created_at': datetime.utcnow().isoformat()
        })
        
        return jsonify({'message': 'Password added successfully', 'id': password_id}), 201
    except ClientError as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/passwords/<password_id>', methods=['DELETE'])
def delete_password(password_id):
    """Delete a password"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    user_id = session['user_id']
    
    try:
        passwords_table.delete_item(
            Key={
                'user_id': user_id,
                'password_id': password_id
            }
        )
        return jsonify({'message': 'Password deleted successfully'})
    except ClientError as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/passwords/<password_id>', methods=['PUT'])
def update_password(password_id):
    """Update a password"""
    if 'user_id' not in session or 'user_password' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    data = request.get_json()
    user_id = session['user_id']
    encryption_key = get_encryption_key(user_id, session['user_password'])
    
    try:
        update_parts = []
        expression_attribute_values = {}
        
        if data.get('website'):
            update_parts.append('website = :website')
            expression_attribute_values[':website'] = data['website']
        
        if 'username' in data:
            update_parts.append('username = :username')
            expression_attribute_values[':username'] = data['username']
        
        if data.get('password'):
            encrypted_password = encrypt_password(data['password'], encryption_key)
            update_parts.append('encrypted_password = :encrypted_password')
            expression_attribute_values[':encrypted_password'] = encrypted_password
        
        if 'notes' in data:
            update_parts.append('notes = :notes')
            expression_attribute_values[':notes'] = data['notes']
        
        update_parts.append('updated_at = :updated_at')
        expression_attribute_values[':updated_at'] = datetime.utcnow().isoformat()
        
        if not update_parts:
            return jsonify({'error': 'No fields to update'}), 400
        
        update_expression = 'SET ' + ', '.join(update_parts)
        
        passwords_table.update_item(
            Key={
                'user_id': user_id,
                'password_id': password_id
            },
            UpdateExpression=update_expression,
            ExpressionAttributeValues=expression_attribute_values
        )
        
        return jsonify({'message': 'Password updated successfully'})
    except ClientError as e:
        return jsonify({'error': str(e)}), 500


@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({'ok': True}), 200


if __name__ == '__main__':
    # Initialize DynamoDB tables for local development
    init_dynamodb_tables()
    port = int(os.getenv('PORT', 5000))
    DEBUG_MODE = os.getenv("FLASK_DEBUG", "False").lower() == "true"
    app.run(debug=DEBUG_MODE, host='0.0.0.0', port=port)
