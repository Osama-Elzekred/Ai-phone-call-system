"""Data encryption utilities."""

import base64
import secrets
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from ..config.settings import get_settings


class EncryptionManager:
    """Data encryption and decryption manager."""
    
    def __init__(self):
        """Initialize encryption manager."""
        self.settings = get_settings()
        self._fernet = None
    
    def _get_fernet(self) -> Fernet:
        """Get Fernet instance for encryption/decryption."""
        if self._fernet is None:
            # Use the secret key as the base for encryption key
            password = self.settings.security.secret_key.encode()
            salt = b'ai_hotline_salt'  # In production, use a random salt stored securely
            
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(password))
            self._fernet = Fernet(key)
        
        return self._fernet
    
    def encrypt_data(self, data: str) -> str:
        """Encrypt string data.
        
        Args:
            data: Plain text data to encrypt
            
        Returns:
            Base64 encoded encrypted data
        """
        fernet = self._get_fernet()
        encrypted_data = fernet.encrypt(data.encode('utf-8'))
        return base64.urlsafe_b64encode(encrypted_data).decode('utf-8')
    
    def decrypt_data(self, encrypted_data: str) -> str:
        """Decrypt encrypted string data.
        
        Args:
            encrypted_data: Base64 encoded encrypted data
            
        Returns:
            Plain text data
            
        Raises:
            ValueError: If decryption fails
        """
        try:
            fernet = self._get_fernet()
            decoded_data = base64.urlsafe_b64decode(encrypted_data.encode('utf-8'))
            decrypted_data = fernet.decrypt(decoded_data)
            return decrypted_data.decode('utf-8')
        except Exception as e:
            raise ValueError(f"Failed to decrypt data: {str(e)}")
    
    def generate_secure_token(self, length: int = 32) -> str:
        """Generate a cryptographically secure random token.
        
        Args:
            length: Length of the token in bytes
            
        Returns:
            URL-safe base64 encoded token
        """
        return secrets.token_urlsafe(length)


# Global instance
encryption_manager = EncryptionManager()

# Convenience functions
def encrypt_data(data: str) -> str:
    """Encrypt string data."""
    return encryption_manager.encrypt_data(data)


def decrypt_data(encrypted_data: str) -> str:
    """Decrypt encrypted string data."""
    return encryption_manager.decrypt_data(encrypted_data)
