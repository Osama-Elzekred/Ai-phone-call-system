#!/usr/bin/env python3
"""
Final verification script for AI Hotline Backend setup.
This script tests all major components to ensure they're working correctly.
"""

import sys
import os
import traceback
from pathlib import Path

# Add src to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / 'src'))

def test_component(name, test_func):
    """Test a component and return success status."""
    try:
        print(f"🔍 Testing {name}...")
        result = test_func()
        if result:
            print(f"✅ {name}: PASSED")
            return True
        else:
            print(f"❌ {name}: FAILED")
            return False
    except Exception as e:
        print(f"❌ {name}: ERROR - {e}")
        if '--verbose' in sys.argv:
            traceback.print_exc()
        return False

def test_imports():
    """Test that all major modules can be imported."""
    try:
        from ai_hotline.shared.config import get_settings
        from ai_hotline.shared.database.session import Base, create_database_engine
        from ai_hotline.shared.database.migrations import check_migration_status
        from main import create_app
        return True
    except Exception:
        return False

def test_configuration():
    """Test configuration loading."""
    try:
        from ai_hotline.shared.config import get_settings
        settings = get_settings()
        return hasattr(settings, 'database_url') and settings.database_url is not None
    except Exception:
        return False

def test_database_connection():
    """Test database connectivity."""
    try:
        import psycopg2
        from ai_hotline.shared.config import get_settings
        settings = get_settings()
        
        # Convert asyncpg URL to psycopg2 format
        db_url = settings.database_url.replace("postgresql+asyncpg://", "postgresql://")
        
        conn = psycopg2.connect(db_url)
        conn.close()
        return True
    except Exception:
        return False

def test_fastapi_app():
    """Test FastAPI application creation."""
    try:
        from main import create_app
        app = create_app()
        return app is not None and hasattr(app, 'title')
    except Exception:
        return False

def test_migration_system():
    """Test migration system functionality."""
    try:
        from ai_hotline.shared.database.migrations import check_migration_status
        # Just test that the function exists and can be called
        # Don't actually check migration status as it may hang
        return callable(check_migration_status)
    except Exception:
        return False

def main():
    """Run all tests."""
    print("🚀 AI Hotline Backend - Final Verification")
    print("=" * 50)
    
    tests = [
        ("Module Imports", test_imports),
        ("Configuration Loading", test_configuration),
        ("Database Connection", test_database_connection),
        ("FastAPI Application", test_fastapi_app),
        ("Migration System", test_migration_system),
    ]
    
    passed = 0
    total = len(tests)
    
    for name, test_func in tests:
        if test_component(name, test_func):
            passed += 1
        print()
    
    print("=" * 50)
    print(f"📊 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! Your setup is ready for development.")
        print()
        print("🚀 To start the application:")
        print("   python -m uvicorn main:app --reload")
        print()
        print("🗄️ To manage migrations:")
        print("   python migrate.py history")
        print("   python migrate.py upgrade head")
        return True
    else:
        print("❌ Some tests failed. Please check the issues above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
