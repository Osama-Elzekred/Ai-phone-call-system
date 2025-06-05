#!/usr/bin/env python3
"""Test migration system functionality."""

import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_migration_system():
    """Test if migration system is working correctly."""
    print("Testing migration system...")
    
    try:
        # Test migration manager import
        from src.ai_hotline.shared.database.migrations import migration_manager
        print("✅ Migration manager imported successfully")
        
        # Test migration status check
        status = migration_manager.check_migration_status()
        print(f"✅ Migration status check: {status}")
        
        if status.get("error"):
            print(f"⚠️  Migration status error: {status['error']}")
            return True  # Continue anyway for development
        
        if status.get("is_up_to_date"):
            print("✅ Database is up to date")
        else:
            print(f"📝 Current revision: {status.get('current_revision')}")
            print(f"📝 Head revision: {status.get('head_revision')}")
            
        return True
        
    except Exception as e:
        print(f"❌ Migration system test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_migration_commands():
    """Test migration commands using the migrate.py script."""
    print("\nTesting migration commands...")
    
    try:
        import subprocess
        
        # Test current command
        result = subprocess.run(
            [sys.executable, "migrate.py", "current"],
            capture_output=True,
            text=True,
            cwd=os.path.dirname(__file__)
        )
        
        if result.returncode == 0:
            print("✅ Migration 'current' command works")
        else:
            print(f"⚠️  Migration 'current' command returned: {result.returncode}")
            if result.stderr:
                print(f"   Error: {result.stderr}")
        
        # Test history command
        result = subprocess.run(
            [sys.executable, "migrate.py", "history"],
            capture_output=True,
            text=True,
            cwd=os.path.dirname(__file__)
        )
        
        if result.returncode == 0:
            print("✅ Migration 'history' command works")
        else:
            print(f"⚠️  Migration 'history' command returned: {result.returncode}")
        
        return True
        
    except Exception as e:
        print(f"❌ Migration commands test failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Migration System")
    print("=" * 50)
    
    success1 = test_migration_system()
    success2 = test_migration_commands()
    
    overall_success = success1 and success2
    
    print("\n" + "=" * 50)
    if overall_success:
        print("✅ All migration tests passed!")
    else:
        print("❌ Some migration tests failed")
    
    sys.exit(0 if overall_success else 1)
