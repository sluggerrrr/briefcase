"""
Tests for encryption functionality in Briefcase application.
"""
import pytest
import base64
import os
from app.core.encryption import (
    DocumentEncryption, 
    EncryptionKeyManager, 
    EncryptionError,
    benchmark_encryption
)


class TestDocumentEncryption:
    """Test AES-256 encryption functionality."""
    
    def test_key_generation(self):
        """Test encryption key generation."""
        key1 = DocumentEncryption.generate_key()
        key2 = DocumentEncryption.generate_key()
        
        assert len(key1) == 32  # 256 bits
        assert len(key2) == 32
        assert key1 != key2  # Should be unique
    
    def test_iv_generation(self):
        """Test initialization vector generation."""
        iv1 = DocumentEncryption.generate_iv()
        iv2 = DocumentEncryption.generate_iv()
        
        assert len(iv1) == 16  # 128 bits
        assert len(iv2) == 16
        assert iv1 != iv2  # Should be unique
    
    def test_key_derivation(self):
        """Test document-specific key derivation."""
        doc_id1 = "doc-123"
        doc_id2 = "doc-456"
        master_key = "test-master-key"
        
        key1a = DocumentEncryption.derive_key_from_master(doc_id1, master_key)
        key1b = DocumentEncryption.derive_key_from_master(doc_id1, master_key)
        key2 = DocumentEncryption.derive_key_from_master(doc_id2, master_key)
        
        # Same document ID should produce same key
        assert key1a == key1b
        
        # Different document IDs should produce different keys
        assert key1a != key2
        
        # Keys should be proper length
        assert len(key1a) == 32
        assert len(key2) == 32
    
    def test_content_encryption_decryption(self):
        """Test basic content encryption and decryption."""
        # Test data
        original_content = b"This is a test document with sensitive content!"
        document_id = "test-doc-123"
        
        # Encrypt
        encrypted_content, iv = DocumentEncryption.encrypt_content(original_content, document_id)
        
        # Verify encrypted content is different and base64 encoded
        assert encrypted_content != base64.b64encode(original_content).decode('utf-8')
        assert len(encrypted_content) > 0
        assert len(iv) > 0
        
        # Verify base64 encoding
        base64.b64decode(encrypted_content.encode('utf-8'))  # Should not raise
        base64.b64decode(iv.encode('utf-8'))  # Should not raise
        
        # Decrypt
        decrypted_content = DocumentEncryption.decrypt_content(encrypted_content, iv, document_id)
        
        # Verify decryption
        assert decrypted_content == original_content
    
    def test_base64_content_encryption(self):
        """Test encryption of base64-encoded content."""
        # Original binary content
        original_bytes = b"Test file content with binary data: \x00\x01\x02\x03"
        base64_content = base64.b64encode(original_bytes).decode('utf-8')
        document_id = "test-doc-base64"
        
        # Encrypt base64 content
        encrypted_content, iv = DocumentEncryption.encrypt_base64_content(base64_content, document_id)
        
        # Decrypt back to base64
        decrypted_base64 = DocumentEncryption.decrypt_to_base64_content(encrypted_content, iv, document_id)
        
        # Verify round-trip
        assert decrypted_base64 == base64_content
        
        # Verify original content is preserved
        recovered_bytes = base64.b64decode(decrypted_base64.encode('utf-8'))
        assert recovered_bytes == original_bytes
    
    def test_large_content_encryption(self):
        """Test encryption of large content (1MB)."""
        # Generate 1MB of test data
        large_content = os.urandom(1024 * 1024)
        document_id = "large-doc-test"
        
        # Encrypt
        encrypted_content, iv = DocumentEncryption.encrypt_content(large_content, document_id)
        
        # Decrypt
        decrypted_content = DocumentEncryption.decrypt_content(encrypted_content, iv, document_id)
        
        # Verify
        assert decrypted_content == large_content
    
    def test_encryption_with_different_document_ids(self):
        """Test that different document IDs produce different encrypted output."""
        content = b"Same content, different documents"
        doc_id1 = "document-1"
        doc_id2 = "document-2"
        
        encrypted1, iv1 = DocumentEncryption.encrypt_content(content, doc_id1)
        encrypted2, iv2 = DocumentEncryption.encrypt_content(content, doc_id2)
        
        # Should produce different encrypted content due to different keys
        assert encrypted1 != encrypted2
        
        # Should be able to decrypt each with correct document ID
        decrypted1 = DocumentEncryption.decrypt_content(encrypted1, iv1, doc_id1)
        decrypted2 = DocumentEncryption.decrypt_content(encrypted2, iv2, doc_id2)
        
        assert decrypted1 == content
        assert decrypted2 == content
    
    def test_decryption_with_wrong_document_id(self):
        """Test that decryption fails with wrong document ID."""
        content = b"Secret content"
        correct_id = "correct-doc-id"
        wrong_id = "wrong-doc-id"
        
        encrypted_content, iv = DocumentEncryption.encrypt_content(content, correct_id)
        
        # Should raise EncryptionError with wrong document ID
        with pytest.raises(EncryptionError):
            DocumentEncryption.decrypt_content(encrypted_content, iv, wrong_id)
    
    def test_decryption_with_corrupted_data(self):
        """Test that decryption fails with corrupted data."""
        content = b"Test content"
        document_id = "test-doc"
        
        encrypted_content, iv = DocumentEncryption.encrypt_content(content, document_id)
        
        # Corrupt the encrypted content
        corrupted_content = encrypted_content[:-4] + "XXXX"
        
        # Should raise EncryptionError
        with pytest.raises(EncryptionError):
            DocumentEncryption.decrypt_content(corrupted_content, iv, document_id)
    
    def test_encryption_error_handling(self):
        """Test encryption error handling."""
        # Test with empty master key
        with pytest.raises(EncryptionError):
            DocumentEncryption.derive_key_from_master("doc-id", "")


class TestEncryptionKeyManager:
    """Test encryption key management."""
    
    def test_master_key_generation(self):
        """Test master key generation."""
        key1 = EncryptionKeyManager.generate_master_key()
        key2 = EncryptionKeyManager.generate_master_key()
        
        assert key1 != key2
        assert len(key1) > 0
        assert len(key2) > 0
        
        # Should be valid base64
        base64.b64decode(key1.encode('utf-8'))
        base64.b64decode(key2.encode('utf-8'))
    
    def test_master_key_validation(self):
        """Test master key validation."""
        # Valid key
        valid_key = EncryptionKeyManager.generate_master_key()
        assert EncryptionKeyManager.validate_master_key(valid_key) is True
        
        # Invalid keys
        assert EncryptionKeyManager.validate_master_key("") is False
        assert EncryptionKeyManager.validate_master_key("not-base64!@#") is False
        assert EncryptionKeyManager.validate_master_key("dGVzdA==") is False  # Too short
    
    def test_key_rotation(self):
        """Test key rotation functionality."""
        old_key = EncryptionKeyManager.generate_master_key()
        new_key = EncryptionKeyManager.rotate_master_key()
        
        assert old_key != new_key
        assert EncryptionKeyManager.validate_master_key(new_key) is True


class TestEncryptionPerformance:
    """Test encryption performance and benchmarking."""
    
    def test_encryption_benchmark(self):
        """Test encryption performance benchmarking."""
        # Test with small content (100KB)
        result = benchmark_encryption(content_size_mb=0.1)
        
        assert result["content_size_mb"] == 0.1
        assert result["encryption_time_ms"] > 0
        assert result["decryption_time_ms"] > 0
        assert result["total_time_ms"] > 0
        assert result["throughput_mbps"] > 0
        assert result["integrity_check"] is True
        
        # Performance should be reasonable (less than 1 second for 100KB)
        assert result["total_time_ms"] < 1000
    
    def test_encryption_performance_scalability(self):
        """Test encryption performance with different content sizes."""
        sizes = [0.01, 0.1, 0.5]  # MB
        
        for size in sizes:
            result = benchmark_encryption(content_size_mb=size)
            
            assert result["integrity_check"] is True
            assert result["throughput_mbps"] > 0
            
            # Larger files should generally take more time
            # but this is a basic sanity check
            assert result["total_time_ms"] > 0


class TestEncryptionIntegration:
    """Test encryption integration with document models."""
    
    def test_document_encryption_workflow(self):
        """Test complete document encryption workflow."""
        # Simulate document upload
        file_content = b"PDF content here with binary data \x89PNG\r\n"
        base64_content = base64.b64encode(file_content).decode('utf-8')
        document_id = "workflow-test-doc"
        
        # Step 1: Encrypt during upload
        encrypted_content, iv = DocumentEncryption.encrypt_base64_content(base64_content, document_id)
        
        # Step 2: Store in database (simulated)
        stored_data = {
            'document_id': document_id,
            'encrypted_content': encrypted_content,
            'encryption_iv': iv
        }
        
        # Step 3: Retrieve and decrypt during download
        decrypted_base64 = DocumentEncryption.decrypt_to_base64_content(
            stored_data['encrypted_content'],
            stored_data['encryption_iv'],
            stored_data['document_id']
        )
        
        # Step 4: Verify integrity
        recovered_content = base64.b64decode(decrypted_base64.encode('utf-8'))
        assert recovered_content == file_content
    
    def test_multiple_document_encryption(self):
        """Test encryption of multiple documents with different keys."""
        documents = [
            {"id": "doc-1", "content": b"Content for document 1"},
            {"id": "doc-2", "content": b"Different content for document 2"},
            {"id": "doc-3", "content": b"Yet another document with unique content"}
        ]
        
        encrypted_docs = []
        
        # Encrypt all documents
        for doc in documents:
            encrypted_content, iv = DocumentEncryption.encrypt_content(doc["content"], doc["id"])
            encrypted_docs.append({
                "id": doc["id"],
                "original": doc["content"],
                "encrypted": encrypted_content,
                "iv": iv
            })
        
        # Decrypt and verify all documents
        for doc in encrypted_docs:
            decrypted = DocumentEncryption.decrypt_content(doc["encrypted"], doc["iv"], doc["id"])
            assert decrypted == doc["original"]
        
        # Verify all encrypted content is different
        encrypted_contents = [doc["encrypted"] for doc in encrypted_docs]
        assert len(set(encrypted_contents)) == len(encrypted_contents)  # All unique