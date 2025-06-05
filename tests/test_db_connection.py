#!/usr/bin/env python3
"""Test database connection without full initialization."""

import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_database_connection():
    """Test basic database connection."""
    print("Testing database connection...")
    
    try:
        from src.ai_hotline.shared.config import get_settings
        from sqlalchemy import create_engine, text
        
        settings = get_settings()
        print(f"Database URL: {settings.database_url}")
        
        # Convert to synchronous URL for testing
        sync_url = settings.database_url.replace("postgresql+asyncpg://", "postgresql+psycopg2://")
        print(f"Sync URL: {sync_url}")
        
        # Try to create engine and connect
        engine = create_engine(sync_url)
        print("✅ Engine created successfully!")
        
        # Test basic connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1 as test"))
            print(f"✅ Database connection successful! Test query result: {result.fetchone()}")
            
        return True
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_database_connection()
    sys.exit(0 if success else 1)
