"""Test application startup and basic functionality."""

import pytest
import sys
import os

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def test_can_import_main_module():
    """Test that we can import the main module without errors."""
    try:
        import main
        assert main is not None
        print("✅ Main module imported successfully")
    except Exception as e:
        pytest.fail(f"Failed to import main module: {e}")

def test_can_create_app():
    """Test that we can create the FastAPI app without errors."""
    try:
        import main
        app = main.create_app()
        assert app is not None
        assert hasattr(app, 'title')
        print("✅ FastAPI app created successfully")
    except Exception as e:
        pytest.fail(f"Failed to create FastAPI app: {e}")

def test_database_session_import():
    """Test that we can import database session without errors."""
    try:
        from ai_hotline.shared.database.session import get_db
        assert get_db is not None
        print("✅ Database session imported successfully")
    except Exception as e:
        pytest.fail(f"Failed to import database session: {e}")

def test_migration_utilities_import():
    """Test that we can import migration utilities without errors."""
    try:
        from ai_hotline.shared.database.migrations import check_migration_status
        assert check_migration_status is not None
        print("✅ Migration utilities imported successfully")
    except Exception as e:
        pytest.fail(f"Failed to import migration utilities: {e}")

def test_basic_configuration():
    """Test that basic configuration can be loaded."""
    try:
        from ai_hotline.shared.config import get_settings
        settings = get_settings()
        assert settings is not None
        assert hasattr(settings, 'database_url')
        print("✅ Configuration loaded successfully")
    except Exception as e:
        pytest.fail(f"Failed to load configuration: {e}")
