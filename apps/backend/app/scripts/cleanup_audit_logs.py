#!/usr/bin/env python3
"""
CLI script to cleanup old audit logs.
Run as Railway cron job: python -m app.scripts.cleanup_audit_logs
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
    """Main entry point for audit log cleanup cron job."""
    try:
        logger.info("Starting audit log cleanup job...")
        
        deleted_count = await DocumentLifecycleService.cleanup_old_audit_logs()
        
        logger.info(f"Audit log cleanup job completed successfully. Deleted {deleted_count} old audit logs.")
        return 0
        
    except Exception as e:
        logger.error(f"Audit log cleanup job failed: {e}")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)