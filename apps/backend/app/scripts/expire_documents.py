#!/usr/bin/env python3
"""
CLI script to expire documents.
Run as Railway cron job: python -m app.scripts.expire_documents
"""
import asyncio
import logging
import sys
from app.services.lifecycle_service import DocumentLifecycleService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def main():
    """Main entry point for document expiration cron job."""
    try:
        logger.info("Starting document expiration job...")
        
        expired_count = await DocumentLifecycleService.expire_documents()
        
        logger.info(f"Document expiration job completed successfully. Expired {expired_count} documents.")
        return 0
        
    except Exception as e:
        logger.error(f"Document expiration job failed: {e}")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)