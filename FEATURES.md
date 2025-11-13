# Password Manager - Features

## ✅ Implemented Features

### 1. **User Registration with TOTP Setup**
- Users register with username and password
- Automatic TOTP (Google Authenticator) setup during registration
- QR code generation for easy setup
- Manual secret entry option
- TOTP verification required before completing registration

### 2. **Recovery Words (4-5 words)**
- Automatic generation of 5 recovery words during registration
- Words are displayed clearly for the user to save
- Users must confirm they've saved the words before proceeding
- Recovery words are hashed and stored securely
- Used for password reset if user loses access

### 3. **TOTP Two-Factor Authentication**
- Required during registration
- Required during login (if enabled)
- Google Authenticator compatible
- Auto-submit when 6-digit code is entered
- Visual feedback during TOTP verification

### 4. **Enhanced Login Flow**
- Username and password authentication
- TOTP verification (if enabled)
- Session-based authentication
- Password stored in session for encryption (not master password)
- Smooth UX with auto-focus and auto-submit

### 5. **Password Management**
- **No Master Password Required**: Uses login password for encryption
- Automatic password loading on dashboard
- Add, edit, and delete passwords
- Encrypted storage in DynamoDB
- Show/hide password functionality
- Clean, modern UI

### 6. **Password Reset**
- Reset password using recovery words
- Username + recovery words verification
- Secure password update
- Automatic redirect to login after reset

### 7. **Security Features**
- Bcrypt password hashing
- Fernet encryption for stored passwords
- TOTP two-factor authentication
- Recovery phrase for account recovery
- Session-based authentication
- Secure password storage in DynamoDB

## 🔄 User Flow

### Registration Flow
1. User enters username and password
2. System generates TOTP secret
3. User scans QR code with Google Authenticator
4. User enters TOTP code to verify
5. System generates 5 recovery words
6. User saves recovery words and confirms
7. Account created and user logged in

### Login Flow
1. User enters username and password
2. If TOTP is enabled:
   - System verifies password
   - System prompts for TOTP code
   - User enters TOTP code from Google Authenticator
   - System verifies TOTP code
3. User is logged in and redirected to dashboard
4. Passwords are automatically loaded (no master password needed)

### Password Reset Flow
1. User clicks "Forgot password"
2. User enters username
3. User enters recovery words (5 words)
4. User enters new password
5. System verifies recovery words
6. System updates password
7. User is redirected to login

## 🎨 UI/UX Improvements

- **Clean, modern design** with gradient background
- **Responsive layout** that works on all devices
- **Auto-submit** for TOTP codes (when 6 digits entered)
- **Auto-focus** on relevant input fields
- **Visual feedback** for actions (success/error messages)
- **Hide/show passwords** functionality
- **Modal dialogs** for adding/editing passwords
- **Notifications** for successful operations
- **Loading states** for better UX

## 🔒 Security Best Practices

1. **Password Hashing**: Bcrypt with automatic salt generation
2. **Encryption**: Fernet symmetric encryption for stored passwords
3. **TOTP**: Time-based one-time passwords for 2FA
4. **Recovery Words**: Hashed storage of recovery phrases
5. **Session Security**: Secure session management
6. **No Plaintext Storage**: All sensitive data is encrypted/hashed

## 📋 DynamoDB Tables

### PasswordManager-Users
- `username` (Primary Key)
- `user_id`
- `password_hash`
- `totp_secret`
- `totp_enabled`
- `recovery_phrase_hash`
- `created_at`

### PasswordManager-Passwords
- `user_id` (Partition Key)
- `password_id` (Sort Key)
- `website`
- `username`
- `encrypted_password`
- `notes`
- `created_at`
- `updated_at`

## 🚀 Getting Started

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure AWS credentials** in `.env` file

3. **Create DynamoDB tables**:
   ```bash
   python setup.py
   ```

4. **Run the application**:
   ```bash
   python app.py
   ```

5. **Register a new account**:
   - Go to `http://localhost:5000/register`
   - Enter username and password
   - Scan QR code with Google Authenticator
   - Enter TOTP code
   - Save recovery words
   - Start using the password manager!

## 📝 Notes

- **Login Password = Encryption Key**: The password you use to login is also used to encrypt/decrypt your stored passwords. This eliminates the need for a separate master password.
- **TOTP is Required**: All users must set up TOTP during registration for enhanced security.
- **Recovery Words**: Save your recovery words in a safe place! You'll need them to reset your password.
- **Session Storage**: Your login password is stored in the session only while you're logged in. It's cleared when you logout.

## 🔮 Future Enhancements

- Password strength checker
- Password generator
- Categories/tags for passwords
- Export/import passwords
- Browser extension
- Mobile app
- Password sharing (secure)
- Audit logs
- Backup and restore

