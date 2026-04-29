"""
Security module for handling encryption, hashing, and key management.
Uses cryptography primitives from pyca/cryptography for AES encryption.
Uses keyring for secure key storage.
"""
import os
import hashlib
import base64
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
import keyring


# Service name for keyring
KEYRING_SERVICE = "cyber-students"
KEYRING_USERNAME = "encryption-key"


def get_encryption_key():
    """
    Get or create the encryption key using keyring.
    The key is stored securely in the system keyring.
    """
    key = keyring.get_password(KEYRING_SERVICE, KEYRING_USERNAME)
    if key is None:
        # Generate a new 256-bit (32 bytes) key
        key = base64.b64encode(os.urandom(32)).decode('utf-8')
        keyring.set_password(KEYRING_SERVICE, KEYRING_USERNAME, key)
    return key


def _get_key_bytes():
    """Get the encryption key as bytes."""
    key = get_encryption_key()
    return base64.b64decode(key)


def hash_email(email):
    """
    Create a deterministic hash of the email for lookup purposes.
    This allows finding users by email without storing the email in plain text.
    """
    email_bytes = email.encode('utf-8')
    hash_obj = hashlib.sha256(email_bytes)
    return hash_obj.hexdigest()


def encrypt_field(plaintext):
    """
    Encrypt a field using AES-256-CBC with random IV.
    Returns base64-encoded IV + ciphertext.
    """
    if plaintext is None:
        return None
    
    plaintext_bytes = plaintext.encode('utf-8')
    
    # Pad the plaintext to be a multiple of 16 bytes (AES block size)
    padder = padding.PKCS7(128).padder()
    padded_data = padder.update(plaintext_bytes) + padder.finalize()
    
    # Generate a random 16-byte IV
    iv = os.urandom(16)
    
    # Create cipher
    key = _get_key_bytes()
    cipher = Cipher(
        algorithms.AES(key),
        modes.CBC(iv),
        backend=default_backend()
    )
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(padded_data) + encryptor.finalize()
    
    # Combine IV and ciphertext, then base64 encode
    combined = iv + ciphertext
    return base64.b64encode(combined).decode('utf-8')


def decrypt_field(encrypted_data):
    """
    Decrypt a field that was encrypted with encrypt_field.
    """
    if encrypted_data is None:
        return None
    
    # Decode from base64
    combined = base64.b64decode(encrypted_data)
    
    # Extract IV (first 16 bytes) and ciphertext
    iv = combined[:16]
    ciphertext = combined[16:]
    
    # Create cipher and decrypt
    key = _get_key_bytes()
    cipher = Cipher(
        algorithms.AES(key),
        modes.CBC(iv),
        backend=default_backend()
    )
    decryptor = cipher.decryptor()
    padded_plaintext = decryptor.update(ciphertext) + decryptor.finalize()
    
    # Unpad the plaintext
    unpadder = padding.PKCS7(128).unpadder()
    plaintext = unpadder.update(padded_plaintext) + unpadder.finalize()
    
    return plaintext.decode('utf-8')


def hash_password(password):
    """
    Hash a password using SHA-256 with salt.
    Returns the salt and hash as a single string.
    """
    # Generate a random 32-byte salt
    salt = os.urandom(32)
    salt_hex = salt.hex()
    
    # Hash the password with the salt
    password_bytes = password.encode('utf-8')
    hash_obj = hashlib.sha256(salt + password_bytes)
    hash_hex = hash_obj.hexdigest()
    
    # Return salt:hash format
    return f"{salt_hex}:{hash_hex}"


def verify_password(password, stored_hash):
    """
    Verify a password against a stored hash.
    """
    try:
        salt_hex, hash_hex = stored_hash.split(':')
        salt = bytes.fromhex(salt_hex)
        
        # Hash the provided password with the same salt
        password_bytes = password.encode('utf-8')
        hash_obj = hashlib.sha256(salt + password_bytes)
        computed_hash = hash_obj.hexdigest()
        
        # Use constant-time comparison to prevent timing attacks
        return hmac_compare(computed_hash, hash_hex)
    except Exception:
        return False


def hmac_compare(a, b):
    """Constant-time string comparison."""
    if len(a) != len(b):
        return False
    result = 0
    for x, y in zip(a, b):
        result |= ord(x) ^ ord(y)
    return result == 0


def hash_token(token):
    """
    Hash a token using SHA-256.
    """
    token_bytes = token.encode('utf-8')
    hash_obj = hashlib.sha256(token_bytes)
    return hash_obj.hexdigest()


def verify_token(token, stored_hash):
    """
    Verify a token against a stored hash.
    """
    computed_hash = hash_token(token)
    return hmac_compare(computed_hash, stored_hash)