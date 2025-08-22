"""
AES-256 encryption utilities for Briefcase application.
Provides secure document encryption with key management.
"""
import os
import base64
import hashlib
from typing import Tuple, Optional
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend
from app.core.config import settings


class EncryptionError(Exception):
    """Custom exception for encryption-related errors."""
    pass


class DocumentEncryption:
    """
    AES-256 encryption for document content with secure key management.
    """
    
    # AES-256 key size (32 bytes)
    KEY_SIZE = 32
    
    # AES block size (16 bytes)
    BLOCK_SIZE = 16
    
    @staticmethod
    def generate_key() -> bytes:
        """
        Generate a cryptographically secure 256-bit AES key.
        
        Returns:
            bytes: A 32-byte encryption key
        """
        return os.urandom(DocumentEncryption.KEY_SIZE)
    
    @staticmethod
    def generate_iv() -> bytes:
        """
        Generate a cryptographically secure initialization vector.
        
        Returns:
            bytes: A 16-byte initialization vector
        """
        return os.urandom(DocumentEncryption.BLOCK_SIZE)
    
    @staticmethod
    def derive_key_from_master(document_id: str, master_key: Optional[str] = None) -> bytes:
        """
        Derive a document-specific key from master key using PBKDF2.
        
        Args:
            document_id: Unique document identifier to use as salt
            master_key: Master encryption key (defaults to settings.ENCRYPTION_KEY)
            
        Returns:
            bytes: Document-specific encryption key
        """
        if master_key is None:
            master_key = settings.ENCRYPTION_KEY
        
        if not master_key:
            raise EncryptionError("Master encryption key not configured")
        
        # Use document ID as salt for key derivation
        salt = document_id.encode('utf-8')
        
        # Derive key using PBKDF2-HMAC-SHA256
        derived_key = hashlib.pbkdf2_hmac(
            'sha256',
            master_key.encode('utf-8'),
            salt,
            100000,  # 100,000 iterations
            DocumentEncryption.KEY_SIZE
        )
        
        return derived_key
    
    @staticmethod
    def encrypt_content(content: bytes, document_id: str) -> Tuple[str, str]:
        """
        Encrypt document content using AES-256-CBC with PKCS7 padding.
        
        Args:
            content: Raw document content as bytes
            document_id: Unique document identifier for key derivation
            
        Returns:
            Tuple[str, str]: (base64_encrypted_content, base64_iv)
            
        Raises:
            EncryptionError: If encryption fails
        """
        try:
            # Derive document-specific key
            key = DocumentEncryption.derive_key_from_master(document_id)
            
            # Generate random IV
            iv = DocumentEncryption.generate_iv()
            
            # Create cipher
            cipher = Cipher(
                algorithms.AES(key),
                modes.CBC(iv),
                backend=default_backend()
            )
            encryptor = cipher.encryptor()
            
            # Apply PKCS7 padding
            padder = padding.PKCS7(DocumentEncryption.BLOCK_SIZE * 8).padder()
            padded_content = padder.update(content) + padder.finalize()
            
            # Encrypt content
            encrypted_content = encryptor.update(padded_content) + encryptor.finalize()
            
            # Return base64 encoded results
            return (
                base64.b64encode(encrypted_content).decode('utf-8'),
                base64.b64encode(iv).decode('utf-8')
            )
            
        except Exception as e:
            raise EncryptionError(f"Encryption failed: {str(e)}")
    
    @staticmethod
    def decrypt_content(encrypted_content: str, iv: str, document_id: str) -> bytes:
        """
        Decrypt document content using AES-256-CBC.
        
        Args:
            encrypted_content: Base64 encoded encrypted content
            iv: Base64 encoded initialization vector
            document_id: Unique document identifier for key derivation
            
        Returns:
            bytes: Decrypted document content
            
        Raises:
            EncryptionError: If decryption fails
        """
        try:
            # Derive document-specific key
            key = DocumentEncryption.derive_key_from_master(document_id)
            
            # Decode base64 inputs
            encrypted_bytes = base64.b64decode(encrypted_content.encode('utf-8'))
            iv_bytes = base64.b64decode(iv.encode('utf-8'))
            
            # Create cipher
            cipher = Cipher(
                algorithms.AES(key),
                modes.CBC(iv_bytes),
                backend=default_backend()
            )
            decryptor = cipher.decryptor()
            
            # Decrypt content
            padded_content = decryptor.update(encrypted_bytes) + decryptor.finalize()
            
            # Remove PKCS7 padding
            unpadder = padding.PKCS7(DocumentEncryption.BLOCK_SIZE * 8).unpadder()
            content = unpadder.update(padded_content) + unpadder.finalize()
            
            return content
            
        except Exception as e:
            raise EncryptionError(f"Decryption failed: {str(e)}")
    
    @staticmethod
    def encrypt_base64_content(base64_content: str, document_id: str) -> Tuple[str, str]:
        """
        Encrypt base64-encoded content (for document uploads).
        
        Args:
            base64_content: Base64 encoded file content
            document_id: Unique document identifier
            
        Returns:
            Tuple[str, str]: (encrypted_content, iv) both base64 encoded
        """
        # Decode base64 to get original bytes
        content_bytes = base64.b64decode(base64_content.encode('utf-8'))
        
        # Encrypt the raw bytes
        return DocumentEncryption.encrypt_content(content_bytes, document_id)
    
    @staticmethod
    def decrypt_to_base64_content(encrypted_content: str, iv: str, document_id: str) -> str:
        """
        Decrypt content and return as base64 (for document downloads).
        
        Args:
            encrypted_content: Base64 encoded encrypted content
            iv: Base64 encoded initialization vector
            document_id: Unique document identifier
            
        Returns:
            str: Base64 encoded decrypted content
        """
        # Decrypt to get raw bytes
        content_bytes = DocumentEncryption.decrypt_content(encrypted_content, iv, document_id)
        
        # Encode back to base64
        return base64.b64encode(content_bytes).decode('utf-8')


class EncryptionKeyManager:
    """
    Manages encryption keys with rotation capability.
    """
    
    @staticmethod
    def generate_master_key() -> str:
        """
        Generate a new master encryption key.
        
        Returns:
            str: Base64 encoded master key
        """
        key = os.urandom(64)  # 512-bit master key
        return base64.b64encode(key).decode('utf-8')
    
    @staticmethod
    def validate_master_key(key: str) -> bool:
        """
        Validate that a master key is properly formatted.
        
        Args:
            key: Master key to validate
            
        Returns:
            bool: True if key is valid, False otherwise
        """
        try:
            decoded = base64.b64decode(key.encode('utf-8'))
            return len(decoded) >= 32  # At least 256 bits
        except Exception:
            return False
    
    @staticmethod
    def rotate_master_key() -> str:
        """
        Generate a new master key for key rotation.
        This would be used in a key rotation process.
        
        Returns:
            str: New base64 encoded master key
        """
        return EncryptionKeyManager.generate_master_key()


def benchmark_encryption(content_size_mb: float = 1) -> dict:
    """
    Benchmark encryption/decryption performance.
    
    Args:
        content_size_mb: Size of test content in MB
        
    Returns:
        dict: Performance metrics
    """
    import time
    
    # Generate test content
    test_content = os.urandom(int(content_size_mb * 1024 * 1024))
    document_id = "benchmark-test-doc"
    
    # Benchmark encryption
    start_time = time.time()
    encrypted_content, iv = DocumentEncryption.encrypt_content(test_content, document_id)
    encryption_time = time.time() - start_time
    
    # Benchmark decryption
    start_time = time.time()
    decrypted_content = DocumentEncryption.decrypt_content(encrypted_content, iv, document_id)
    decryption_time = time.time() - start_time
    
    # Verify integrity
    integrity_check = test_content == decrypted_content
    
    return {
        "content_size_mb": content_size_mb,
        "encryption_time_ms": round(encryption_time * 1000, 2),
        "decryption_time_ms": round(decryption_time * 1000, 2),
        "total_time_ms": round((encryption_time + decryption_time) * 1000, 2),
        "throughput_mbps": round(content_size_mb / (encryption_time + decryption_time), 2),
        "integrity_check": integrity_check
    }