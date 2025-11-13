"""
Simple Password Manager with Flask, DynamoDB, TOTP, and Recovery Words
"""
import os
import re
import io
import base64
import json
import secrets
import hashlib
from datetime import datetime

import boto3
import bcrypt
import pyotp
import qrcode
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key, Attr
from cryptography.fernet import Fernet
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

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

dynamodb = boto3.resource('dynamodb', **dynamodb_config)
dynamodb_client = boto3.client('dynamodb', **dynamodb_config)

# Get table references
users_table = dynamodb.Table(DYNAMODB_USERS_TABLE)
accounts_table = dynamodb.Table(DYNAMODB_ACCOUNTS_TABLE)
passwords_table = dynamodb.Table(DYNAMODB_PASSWORDS_TABLE)

# Recovery words list (simplified - use common words)
RECOVERY_WORDS = [
    "apple", "banana", "cherry", "dolphin", "elephant", "forest", "garden", "hammer",
    "island", "jaguar", "kitten", "lion", "mountain", "nature", "ocean", "penguin",
    "quasar", "rabbit", "sunset", "tiger", "umbrella", "violin", "water", "xylophone",
    "yellow", "zebra", "alpha", "bravo", "charlie", "delta", "echo", "foxtrot"
]


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
            dynamodb_client.create_table(**table_def)
            print(f"Created table: {table_def['TableName']}")
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceInUseException':
                print(f"Table {table_def['TableName']} already exists")
            else:
                print(f"Error creating table {table_def['TableName']}: {e}")


def hash_password(password):
    """Hash password using bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def check_password(hashed_password, password):
    """Check password against hash"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))


def get_session_encryption_key():
    """Retrieve encryption key from session"""
    encryption_key = session.get('encryption_key')
    if not encryption_key:
        return None
    return encryption_key


def encrypt_password(password, encryption_key):
    """Encrypt password using Fernet"""
    if not encryption_key:
        raise ValueError("Encryption key is missing")
    if isinstance(encryption_key, str):
        encryption_key = encryption_key.encode('utf-8')
    f = Fernet(encryption_key)
    return f.encrypt(password.encode('utf-8')).decode('utf-8')


def decrypt_password(encrypted_password, encryption_key):
    """Decrypt password using Fernet"""
    if not encryption_key:
        raise ValueError("Encryption key is missing")
    if isinstance(encryption_key, str):
        encryption_key = encryption_key.encode('utf-8')
    f = Fernet(encryption_key)
    return f.decrypt(encrypted_password.encode('utf-8')).decode('utf-8')


def generate_id():
    """Generate a unique ID"""
    import uuid
    return str(uuid.uuid4())


def generate_totp_secret():
    """Generate a TOTP secret"""
    return pyotp.random_base32()


def get_totp_uri(username, secret):
    """Get TOTP provisioning URI"""
    totp = pyotp.TOTP(secret)
    return totp.provisioning_uri(
        name=username,
        issuer_name='Password Manager'
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
    return totp.verify(token, valid_window=1)


def generate_recovery_words(count=5):
    """Generate recovery words"""
    return ' '.join(secrets.choice(RECOVERY_WORDS) for _ in range(count))


def hash_recovery_phrase(phrase):
    """Hash recovery phrase"""
    return hashlib.sha256(phrase.encode('utf-8')).hexdigest()


def verify_recovery_phrase(stored_hash, phrase):
    """Verify recovery phrase"""
    phrase_hash = hashlib.sha256(phrase.encode('utf-8')).hexdigest()
    return phrase_hash == stored_hash


def is_valid_email(email):
    """Simple email validation"""
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
            scan_response = users_table.scan(
                FilterExpression=Attr('email_lower').eq(email_lower)
            )
            return len(scan_response.get('Items', [])) > 0
        raise


def migrate_user_passwords_to_new_key(user_id, legacy_password, new_encryption_key):
    """Re-encrypt existing passwords from legacy key to new key"""
    if not legacy_password or not user_id or not new_encryption_key:
        return
    try:
        legacy_key = base64.urlsafe_b64encode(
            hashlib.sha256(f"{user_id}:{legacy_password}".encode('utf-8')).digest()
        )
        legacy_fernet = Fernet(legacy_key)
        new_fernet = Fernet(new_encryption_key.encode('utf-8') if isinstance(new_encryption_key, str) else new_encryption_key)
    except Exception:
        return

    exclusive_start_key = None
    while True:
        query_kwargs = {
            'KeyConditionExpression': Key('user_id').eq(user_id)
        }
        if exclusive_start_key:
            query_kwargs['ExclusiveStartKey'] = exclusive_start_key
        try:
            response = passwords_table.query(**query_kwargs)
        except ClientError:
            break

        for item in response.get('Items', []):
            try:
                decrypted = legacy_fernet.decrypt(item['encrypted_password'].encode('utf-8'))
                re_encrypted = new_fernet.encrypt(decrypted).decode('utf-8')
                passwords_table.update_item(
                    Key={
                        'user_id': user_id,
                        'password_id': item['password_id']
                    },
                    UpdateExpression='SET encrypted_password = :ep, updated_at = :upd',
                    ExpressionAttributeValues={
                        ':ep': re_encrypted,
                        ':upd': datetime.utcnow().isoformat()
                    }
                )
            except Exception:
                continue

        exclusive_start_key = response.get('LastEvaluatedKey')
        if not exclusive_start_key:
            break


# Routes
@app.route('/')
def index():
    """Home page - redirect to login or dashboard"""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page with TOTP verification"""
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
                # This handles the case where user is verifying TOTP
                # If we have stored credentials, verify they match current user
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
            session['user_id'] = user['user_id']
            session['username'] = user['username']

            encryption_key = user.get('encryption_key')
            if not encryption_key:
                encryption_key = Fernet.generate_key().decode('utf-8')
                try:
                    users_table.update_item(
                        Key={'username': username},
                        UpdateExpression='SET encryption_key = :ek, updated_at = :upd',
                        ExpressionAttributeValues={
                            ':ek': encryption_key,
                            ':upd': datetime.utcnow().isoformat()
                        }
                    )
                except ClientError:
                    pass
                migrate_user_passwords_to_new_key(user['user_id'], password, encryption_key)
            session['encryption_key'] = encryption_key

            # Clear temporary login session
            session.pop('login_username', None)
            session.pop('pending_password', None)
            
            return redirect(url_for('dashboard'))
        except ClientError as e:
            return render_template('login.html', error=f'Database error: {str(e)}')
    
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    """Registration page - step 1: Basic info"""
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email', '').strip()
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if not username or not email or not password:
            return render_template('register.html', error='Please fill in all fields', username=username, email=email)
        
        if not is_valid_email(email):
            return render_template('register.html', error='Please enter a valid email address', username=username, email=email)
        
        if password != confirm_password:
            return render_template('register.html', error='Passwords do not match', username=username, email=email)
        
        if len(password) < 6:
            return render_template('register.html', error='Password must be at least 6 characters', username=username, email=email)
        
        try:
            email_lower = email.lower()
            # Check email uniqueness
            if email_exists(email_lower):
                return render_template('register.html', error='Email is already registered', username=username, email=email)
            
            # Check if user exists
            response = users_table.get_item(Key={'username': username})
            if 'Item' in response:
                return render_template('register.html', error='Username already exists', username=username, email=email)
            
            # Store registration data in session for next step
            session['reg_username'] = username
            session['reg_email'] = email
            session['reg_email_lower'] = email_lower
            session['reg_password'] = password
            
            # Generate TOTP secret
            totp_secret = generate_totp_secret()
            session['reg_totp_secret'] = totp_secret
            
            # Redirect to TOTP setup
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
        
        # TOTP verified, proceed to recovery words
        return redirect(url_for('recovery_words'))
    
    # Generate QR code
    totp_uri = get_totp_uri(username, totp_secret)
    qr_code = generate_qr_code(totp_uri)
    
    return render_template('setup_totp.html', 
                         username=username,
                         totp_secret=totp_secret,
                         qr_code=qr_code)


@app.route('/recovery-words', methods=['GET', 'POST'])
def recovery_words():
    """Recovery words page - step 3: Show and verify recovery words"""
    if 'reg_username' not in session:
        return redirect(url_for('register'))
    
    if request.method == 'POST':
        # User confirms they saved the words
        return redirect(url_for('complete_registration'))
    
    # Generate recovery words if not already generated
    if 'recovery_words' not in session:
        session['recovery_words'] = generate_recovery_words(5)
    
    recovery_words = session['recovery_words']
    
    return render_template('recovery_words.html', recovery_words=recovery_words)


@app.route('/complete-registration', methods=['GET'])
def complete_registration():
    """Complete registration - step 4: Save user to database"""
    if 'reg_username' not in session or 'reg_password' not in session or 'reg_email' not in session:
        return redirect(url_for('register'))
    
    username = session['reg_username']
    email = session['reg_email']
    email_lower = session.get('reg_email_lower', email.lower())
    password = session['reg_password']
    totp_secret = session.get('reg_totp_secret')
    recovery_words = session.get('recovery_words', '')
    
    try:
        # Create new user
        user_id = generate_id()
        recovery_phrase_hash = hash_recovery_phrase(recovery_words) if recovery_words else None
        encryption_key = Fernet.generate_key().decode('utf-8')
        
        users_table.put_item(Item={
            'username': username,
            'user_id': user_id,
            'email': email,
            'email_lower': email_lower,
            'password_hash': hash_password(password),
            'totp_secret': totp_secret,
            'totp_enabled': True,
            'recovery_phrase_hash': recovery_phrase_hash,
            'encryption_key': encryption_key,
            'created_at': datetime.utcnow().isoformat()
        })
        
        # Clear registration session
        session.pop('reg_username', None)
        session.pop('reg_password', None)
        session.pop('reg_email', None)
        session.pop('reg_email_lower', None)
        session.pop('reg_totp_secret', None)
        session.pop('recovery_words', None)
        
        # Set user session
        session['user_id'] = user_id
        session['username'] = username
        session['encryption_key'] = encryption_key
        
        return redirect(url_for('dashboard'))
    except ClientError as e:
        return render_template('register.html', error=f'Database error: {str(e)}')


@app.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    """Password reset using recovery words"""
    if request.method == 'POST':
        username = request.form.get('username')
        recovery_phrase = request.form.get('recovery_phrase')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        if not username or not recovery_phrase or not new_password:
            return render_template('reset_password.html', error='Please fill in all fields')
        
        if new_password != confirm_password:
            return render_template('reset_password.html', error='Passwords do not match')
        
        if len(new_password) < 6:
            return render_template('reset_password.html', error='Password must be at least 6 characters')
        
        try:
            # Get user
            response = users_table.get_item(Key={'username': username})
            if 'Item' not in response:
                return render_template('reset_password.html', error='User not found')
            
            user = response['Item']
            
            # Verify recovery phrase
            stored_hash = user.get('recovery_phrase_hash')
            if not stored_hash or not verify_recovery_phrase(stored_hash, recovery_phrase):
                return render_template('reset_password.html', error='Invalid recovery phrase')
            
            # Update password
            users_table.update_item(
                Key={'username': username},
                UpdateExpression='SET password_hash = :pwd, updated_at = :upd',
                ExpressionAttributeValues={
                    ':pwd': hash_password(new_password),
                    ':upd': datetime.utcnow().isoformat()
                }
            )
            
            return redirect(url_for('login'))
        except ClientError as e:
            return render_template('reset_password.html', error=f'Database error: {str(e)}')
    
    return render_template('reset_password.html')


@app.route('/logout')
def logout():
    """Logout user"""
    session.clear()
    return redirect(url_for('login'))


@app.route('/dashboard')
def dashboard():
    """Dashboard page"""
    if 'user_id' not in session or 'encryption_key' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html', username=session.get('username'))


@app.route('/api/passwords', methods=['GET'])
def get_passwords():
    """Get all passwords for the current user"""
    if 'user_id' not in session or 'encryption_key' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    user_id = session['user_id']
    encryption_key = get_session_encryption_key()
    if not encryption_key:
        return jsonify({'error': 'Encryption key missing'}), 401
    
    try:
        result = []
        exclusive_start_key = None
        while True:
            query_kwargs = {
                'KeyConditionExpression': Key('user_id').eq(user_id)
            }
            if exclusive_start_key:
                query_kwargs['ExclusiveStartKey'] = exclusive_start_key
            response = passwords_table.query(**query_kwargs)
            for item in response.get('Items', []):
                try:
                    decrypted = decrypt_password(item['encrypted_password'], encryption_key)
                    result.append({
                        'id': item['password_id'],
                        'website': item.get('website', ''),
                        'username': item.get('username', ''),
                        'password': decrypted,
                        'notes': item.get('notes', ''),
                        'created_at': item.get('created_at', '')
                    })
                except Exception:
                    continue
            exclusive_start_key = response.get('LastEvaluatedKey')
            if not exclusive_start_key:
                break
        
        return jsonify({'passwords': result})
    except ClientError as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/passwords', methods=['POST'])
def add_password():
    """Add a new password"""
    if 'user_id' not in session or 'encryption_key' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    data = request.get_json()
    website = data.get('website')
    username = data.get('username')
    password = data.get('password')
    notes = data.get('notes')
    
    if not website or not password:
        return jsonify({'error': 'Website and password are required'}), 400
    
    user_id = session['user_id']
    encryption_key = get_session_encryption_key()
    if not encryption_key:
        return jsonify({'error': 'Encryption key missing'}), 401
    encrypted_password = encrypt_password(password, encryption_key)
    password_id = generate_id()
    
    try:
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
    if 'user_id' not in session or 'encryption_key' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    data = request.get_json()
    website = data.get('website')
    username = data.get('username')
    password = data.get('password')
    notes = data.get('notes')
    
    user_id = session['user_id']
    encryption_key = get_session_encryption_key()
    if not encryption_key:
        return jsonify({'error': 'Encryption key missing'}), 401
    
    try:
        # Get existing item
        response = passwords_table.get_item(
            Key={
                'user_id': user_id,
                'password_id': password_id
            }
        )
        
        if 'Item' not in response:
            return jsonify({'error': 'Password not found'}), 404
        
        # Build update expression
        update_parts = []
        expression_attribute_values = {}
        
        if website:
            update_parts.append('website = :website')
            expression_attribute_values[':website'] = website
        if username is not None:
            update_parts.append('username = :username')
            expression_attribute_values[':username'] = username
        if password:
            encrypted_password = encrypt_password(password, encryption_key)
            update_parts.append('encrypted_password = :encrypted_password')
            expression_attribute_values[':encrypted_password'] = encrypted_password
        if notes is not None:
            update_parts.append('notes = :notes')
            expression_attribute_values[':notes'] = notes
        
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


if __name__ == '__main__':
    # Initialize DynamoDB tables
    print("Initializing DynamoDB tables...")
    init_dynamodb_tables()
    print("Starting Flask application...")
    port = int(os.getenv('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
