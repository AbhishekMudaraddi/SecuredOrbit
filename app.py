"""
Password Manager V2 - Simple Flask Application with DynamoDB
Stores encrypted passwords in DynamoDB
"""
import os
import json
import base64
import hashlib
from datetime import datetime
from uuid import uuid4

import boto3
import bcrypt
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key
from cryptography.fernet import Fernet
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

# AWS Configuration
AWS_REGION = os.getenv('AWS_REGION', 'us-east-1')
AWS_ENDPOINT = os.getenv('AWS_ENDPOINT', None)
DYNAMODB_USERS_TABLE = os.getenv('DYNAMODB_USERS_TABLE', 'PasswordManagerV2-Users')
DYNAMODB_PASSWORDS_TABLE = os.getenv('DYNAMODB_PASSWORDS_TABLE', 'PasswordManagerV2-Passwords')

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
                {'AttributeName': 'username', 'AttributeType': 'S'}
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
        password = request.form.get('password')
        
        if not username or not password:
            return render_template('register.html', error='Please fill in all fields')
        
        if len(password) < 6:
            return render_template('register.html', error='Password must be at least 6 characters')
        
        try:
            # Check if user exists
            response = users_table.get_item(Key={'username': username})
            if 'Item' in response:
                return render_template('register.html', error='Username already exists')
            
            # Create new user
            user_id = generate_id()
            users_table.put_item(Item={
                'username': username,
                'user_id': user_id,
                'password_hash': hash_password(password),
                'created_at': datetime.utcnow().isoformat()
            })
            
            # Set session
            session['user_id'] = user_id
            session['username'] = username
            session['user_password'] = password  # Store temporarily for encryption key
            
            return redirect(url_for('dashboard'))
        except ClientError as e:
            return render_template('register.html', error=f'Database error: {str(e)}')
    
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            return render_template('login.html', error='Please fill in all fields')
        
        try:
            response = users_table.get_item(Key={'username': username})
            if 'Item' not in response:
                return render_template('login.html', error='Invalid username or password')
            
            user = response['Item']
            
            # Verify password
            if not check_password(user['password_hash'], password):
                return render_template('login.html', error='Invalid username or password')
            
            # Set session
            session['user_id'] = user['user_id']
            session['username'] = user['username']
            session['user_password'] = password  # Store temporarily for encryption key
            
            return redirect(url_for('dashboard'))
        except ClientError as e:
            return render_template('login.html', error=f'Database error: {str(e)}')
    
    return render_template('login.html')


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
    # Initialize DynamoDB tables
    print("🚀 Initializing DynamoDB tables...")
    init_dynamodb_tables()
    print("✅ Starting Flask application...")
    port = int(os.getenv('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)

