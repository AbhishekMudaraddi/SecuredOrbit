"""
Test cases for helper functions (password hashing, email validation, etc.)
"""
import pytest
import os
import sys

# Add parent directory to path to import app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import (
    hash_password,
    check_password,
    is_valid_email,
    get_encryption_key,
    encrypt_password,
    decrypt_password,
    generate_id
)


def test_hash_password():
    """Test that password hashing works"""
    password = "test_password_123"
    hashed = hash_password(password)
    assert hashed != password  # Should be different
    assert isinstance(hashed, str)
    assert len(hashed) > 0


def test_check_password():
    """Test that password checking works"""
    password = "test_password_123"
    hashed = hash_password(password)
    assert check_password(hashed, password) is True
    assert check_password(hashed, "wrong_password") is False


def test_is_valid_email():
    """Test email validation function"""
    assert is_valid_email("test@example.com") is True
    assert is_valid_email("user.name@domain.co.uk") is True
    assert is_valid_email("invalid-email") is False
    assert is_valid_email("@example.com") is False
    assert is_valid_email("test@") is False
    assert is_valid_email("") is False


def test_generate_id():
    """Test that ID generation works"""
    id1 = generate_id()
    id2 = generate_id()
    assert isinstance(id1, str)
    assert len(id1) > 0
    assert id1 != id2  # IDs should be unique


def test_encryption_key_generation():
    """Test encryption key generation"""
    user_id = "test_user_123"
    password = "test_password"
    key = get_encryption_key(user_id, password)
    assert isinstance(key, bytes)
    assert len(key) > 0


def test_encrypt_decrypt_password():
    """Test password encryption and decryption"""
    user_id = "test_user_123"
    password = "test_password"
    plain_password = "my_secret_password"
    
    encryption_key = get_encryption_key(user_id, password)
    encrypted = encrypt_password(plain_password, encryption_key)
    decrypted = decrypt_password(encrypted, encryption_key)
    
    assert encrypted != plain_password  # Should be encrypted
    assert decrypted == plain_password  # Should decrypt correctly
    assert isinstance(encrypted, str)
    assert isinstance(decrypted, str)

