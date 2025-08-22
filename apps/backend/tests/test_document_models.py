"""
Tests for document models in Briefcase application.
"""
import pytest
from datetime import datetime, timedelta, timezone
from app.models.document import Document, DocumentStatus
from app.models.document_access_log import DocumentAccessLog, AccessAction
from app.models.user import User
from app.core.security import get_password_hash


class TestDocumentModel:
    """Test Document model functionality."""
    
    def test_create_document(self, db_session):
        """Test creating a document."""
        # Create test users
        sender = User(email="sender@test.com", password_hash=get_password_hash("pass"), is_active=True)
        recipient = User(email="recipient@test.com", password_hash=get_password_hash("pass"), is_active=True)
        db_session.add(sender)
        db_session.add(recipient)
        db_session.commit()
        
        # Create document
        document = Document(
            title="Test Document",
            description="Test description",
            file_name="test.pdf",
            file_size=1024,
            mime_type="application/pdf",
            sender_id=sender.id,
            recipient_id=recipient.id,
            encrypted_content="encrypted_base64_content",
            view_limit=5,
            expires_at=datetime.now(timezone.utc) + timedelta(days=7)
        )
        db_session.add(document)
        db_session.commit()
        
        assert document.id is not None
        assert document.title == "Test Document"
        assert document.sender_id == sender.id
        assert document.recipient_id == recipient.id
        assert document.status == DocumentStatus.ACTIVE
        assert document.access_count == 0
    
    def test_document_status_calculation_active(self, db_session):
        """Test document status calculation for active document."""
        # Create test users
        sender = User(email="sender2@test.com", password_hash=get_password_hash("pass"), is_active=True)
        recipient = User(email="recipient2@test.com", password_hash=get_password_hash("pass"), is_active=True)
        db_session.add_all([sender, recipient])
        db_session.commit()
        
        document = Document(
            title="Active Document",
            file_name="active.pdf",
            file_size=1024,
            sender_id=sender.id,
            recipient_id=recipient.id,
            encrypted_content="encrypted",
            view_limit=5,
            expires_at=datetime.now(timezone.utc) + timedelta(days=7)
        )
        db_session.add(document)
        db_session.commit()
        
        assert document.calculate_status() == DocumentStatus.ACTIVE
    
    def test_document_status_calculation_expired(self, db_session):
        """Test document status calculation for expired document."""
        sender = User(email="sender3@test.com", password_hash=get_password_hash("pass"), is_active=True)
        recipient = User(email="recipient3@test.com", password_hash=get_password_hash("pass"), is_active=True)
        db_session.add_all([sender, recipient])
        db_session.commit()
        
        document = Document(
            title="Expired Document",
            file_name="expired.pdf",
            file_size=1024,
            sender_id=sender.id,
            recipient_id=recipient.id,
            encrypted_content="encrypted",
            expires_at=datetime.now(timezone.utc) - timedelta(days=1)  # Expired yesterday
        )
        db_session.add(document)
        db_session.commit()
        
        assert document.calculate_status() == DocumentStatus.EXPIRED
    
    def test_document_status_calculation_view_exhausted(self, db_session):
        """Test document status calculation for view-exhausted document."""
        sender = User(email="sender4@test.com", password_hash=get_password_hash("pass"), is_active=True)
        recipient = User(email="recipient4@test.com", password_hash=get_password_hash("pass"), is_active=True)
        db_session.add_all([sender, recipient])
        db_session.commit()
        
        document = Document(
            title="Limited Views Document",
            file_name="limited.pdf",
            file_size=1024,
            sender_id=sender.id,
            recipient_id=recipient.id,
            encrypted_content="encrypted",
            view_limit=2,
            access_count=2  # Already viewed twice
        )
        db_session.add(document)
        db_session.commit()
        
        assert document.calculate_status() == DocumentStatus.VIEW_EXHAUSTED
    
    def test_document_accessibility(self, db_session):
        """Test document accessibility checks."""
        sender = User(email="sender5@test.com", password_hash=get_password_hash("pass"), is_active=True)
        recipient = User(email="recipient5@test.com", password_hash=get_password_hash("pass"), is_active=True)
        other_user = User(email="other@test.com", password_hash=get_password_hash("pass"), is_active=True)
        db_session.add_all([sender, recipient, other_user])
        db_session.commit()
        
        document = Document(
            title="Access Test Document",
            file_name="access.pdf",
            file_size=1024,
            sender_id=sender.id,
            recipient_id=recipient.id,
            encrypted_content="encrypted",
            expires_at=datetime.now(timezone.utc) + timedelta(days=7)
        )
        db_session.add(document)
        db_session.commit()
        
        # Sender can access
        assert document.is_accessible_by(sender.id) is True
        
        # Recipient can access
        assert document.is_accessible_by(recipient.id) is True
        
        # Other user cannot access
        assert document.is_accessible_by(other_user.id) is False
    
    def test_document_increment_access_count(self, db_session):
        """Test incrementing document access count."""
        sender = User(email="sender6@test.com", password_hash=get_password_hash("pass"), is_active=True)
        recipient = User(email="recipient6@test.com", password_hash=get_password_hash("pass"), is_active=True)
        db_session.add_all([sender, recipient])
        db_session.commit()
        
        document = Document(
            title="Count Test Document",
            file_name="count.pdf",
            file_size=1024,
            sender_id=sender.id,
            recipient_id=recipient.id,
            encrypted_content="encrypted",
            view_limit=3
        )
        db_session.add(document)
        db_session.commit()
        
        assert document.access_count == 0
        
        document.increment_access_count()
        assert document.access_count == 1
        assert document.status == DocumentStatus.ACTIVE
        
        document.increment_access_count()
        assert document.access_count == 2
        assert document.status == DocumentStatus.ACTIVE
        
        document.increment_access_count()
        assert document.access_count == 3
        assert document.status == DocumentStatus.VIEW_EXHAUSTED
    
    def test_document_soft_delete(self, db_session):
        """Test soft deleting a document."""
        sender = User(email="sender7@test.com", password_hash=get_password_hash("pass"), is_active=True)
        recipient = User(email="recipient7@test.com", password_hash=get_password_hash("pass"), is_active=True)
        db_session.add_all([sender, recipient])
        db_session.commit()
        
        document = Document(
            title="Delete Test Document",
            file_name="delete.pdf",
            file_size=1024,
            sender_id=sender.id,
            recipient_id=recipient.id,
            encrypted_content="encrypted"
        )
        db_session.add(document)
        db_session.commit()
        
        assert document.deleted_at is None
        assert document.status == DocumentStatus.ACTIVE
        
        document.soft_delete()
        
        assert document.deleted_at is not None
        assert document.status == DocumentStatus.DELETED
        assert document.calculate_status() == DocumentStatus.DELETED


class TestDocumentAccessLog:
    """Test DocumentAccessLog model functionality."""
    
    def test_create_access_log(self, db_session):
        """Test creating a document access log."""
        # Create test user and document
        user = User(email="logger@test.com", password_hash=get_password_hash("pass"), is_active=True)
        db_session.add(user)
        db_session.commit()
        
        document = Document(
            title="Log Test Document",
            file_name="log.pdf",
            file_size=1024,
            sender_id=user.id,
            recipient_id=user.id,
            encrypted_content="encrypted"
        )
        db_session.add(document)
        db_session.commit()
        
        # Create access log
        log = DocumentAccessLog(
            document_id=document.id,
            user_id=user.id,
            action=AccessAction.VIEW,
            success="true",
            ip_address="192.168.1.1",
            user_agent="TestBrowser/1.0"
        )
        db_session.add(log)
        db_session.commit()
        
        assert log.id is not None
        assert log.document_id == document.id
        assert log.user_id == user.id
        assert log.action == AccessAction.VIEW
        assert log.success == "true"
    
    def test_access_denied_log(self, db_session):
        """Test creating an access denied log."""
        user = User(email="denied@test.com", password_hash=get_password_hash("pass"), is_active=True)
        db_session.add(user)
        db_session.commit()
        
        document = Document(
            title="Denied Test Document",
            file_name="denied.pdf",
            file_size=1024,
            sender_id=user.id,
            recipient_id=user.id,
            encrypted_content="encrypted"
        )
        db_session.add(document)
        db_session.commit()
        
        log = DocumentAccessLog(
            document_id=document.id,
            user_id=user.id,
            action=AccessAction.ACCESS_DENIED,
            success="false",
            error_message="User not authorized to access this document"
        )
        db_session.add(log)
        db_session.commit()
        
        assert log.success == "false"
        assert log.error_message == "User not authorized to access this document"
        assert log.action == AccessAction.ACCESS_DENIED