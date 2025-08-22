#!/usr/bin/env python3
"""
Railway entry point for Briefcase FastAPI application.
This file imports and runs the actual FastAPI app from app/main.py
"""

from app.main import app

def main():
    import uvicorn
    import os
    
    # Get port from environment (Railway sets this)
    port = int(os.getenv("PORT", 8000))
    
    # Run the FastAPI application
    uvicorn.run(app, host="0.0.0.0", port=port)

if __name__ == "__main__":
    main()
