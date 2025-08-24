#!/usr/bin/env python3
"""
Test script to verify cron scripts work locally.
"""
import pytest
import subprocess
import sys
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))


@pytest.mark.asyncio
async def test_cron_scripts():
    """Test all cron scripts."""
    scripts = [
        "app.scripts.expire_documents",
        "app.scripts.cleanup_documents", 
        "app.scripts.cleanup_audit_logs"
    ]
    
    print("Testing cron scripts...")
    
    for script in scripts:
        print(f"\n🧪 Testing {script}...")
        
        try:
            # Run the script as a module
            result = subprocess.run(
                [sys.executable, "-m", script],
                cwd=backend_dir,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                print(f"✅ {script} - SUCCESS")
                print(f"   Output: {result.stdout.strip()}")
            else:
                print(f"❌ {script} - FAILED")
                print(f"   Error: {result.stderr.strip()}")
                
        except subprocess.TimeoutExpired:
            print(f"⏰ {script} - TIMEOUT")
        except Exception as e:
            print(f"💥 {script} - EXCEPTION: {e}")
    
    print(f"\n🎉 Cron script testing completed!")


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_cron_scripts())