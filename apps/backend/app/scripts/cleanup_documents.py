#!/usr/bin/env python3
"""
CLI script to cleanup deleted documents.
Run as Railway cron job: python -m app.scripts.cleanup_documents
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
    """Main entry point for document cleanup cron job."""
    try:
        logger.info("Starting document cleanup job...")
        
        deleted_count = await DocumentLifecycleService.cleanup_deleted_documents()
        
        logger.info(f"Document cleanup job completed successfully. Permanently deleted {deleted_count} documents.")
        return 0
        
    except Exception as e:
        logger.error(f"Document cleanup job failed: {e}")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)