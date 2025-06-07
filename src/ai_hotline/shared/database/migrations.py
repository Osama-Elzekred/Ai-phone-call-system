"""Database migration utilities for application startup."""

import logging
import subprocess
import sys
from pathlib import Path
from typing import Dict, Optional

from src.ai_hotline.shared.config.settings import get_settings

logger = logging.getLogger(__name__)


class MigrationManager:
    """Manages database migrations for the application."""
    
    def __init__(self):
        self.settings = get_settings()
        self.project_root = Path(__file__).parent.parent.parent.parent.parent
        self.alembic_cfg_path = self.project_root / "alembic.ini"
        self._alembic_available = self._check_alembic_availability()
        
    def _check_alembic_availability(self) -> bool:
        """Check if Alembic is available and properly configured."""
        try:
            # Check Python version compatibility first
            if sys.version_info < (3,8):
                logger.error("Alembic requires Python 3.8 or higher")
                return False
            
            # Try importing critical Alembic components
            import alembic
            logger.debug(f"Alembic version: {alembic.__version__}")
            
            # Test imports individually to isolate issues
            from alembic.config import Config
            from alembic.script import ScriptDirectory
            
            # Verify configuration file exists
            if not self.alembic_cfg_path.exists():
                logger.error(f"Alembic config file not found: {self.alembic_cfg_path}")
                return False
            
            # Test basic configuration loading
            config = Config(str(self.alembic_cfg_path))
            ScriptDirectory.from_config(config)
            
            logger.info("Alembic is available and properly configured")
            return True
            
        except ImportError as e:
            logger.error(f"Alembic not available - ImportError: {e}")
            logger.warning("Run: pip install --upgrade alembic")
            return False
        except SyntaxError as e:
            logger.error(f"Alembic syntax error (version incompatibility): {e}")
            logger.warning("Try: pip install --upgrade --force-reinstall alembic sqlalchemy")
            return False
        except Exception as e:
            logger.error(f"Unexpected error with Alembic: {e}")
            return False
    
    def _run_alembic_command(self, command_args: list) -> tuple[bool, str]:
        """Run Alembic command via subprocess as fallback."""
        try:
            # Construct the full command
            cmd = [sys.executable, "-m", "alembic"] + command_args
            
            # Set environment variables
            env = {
                **dict(os.environ),
                "PYTHONPATH": str(self.project_root / "src")
            }
            
            result = subprocess.run(
                cmd,
                cwd=str(self.project_root),
                env=env,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                return True, result.stdout
            else:
                logger.error(f"Alembic command failed: {result.stderr}")
                return False, result.stderr
                
        except subprocess.TimeoutExpired:
            logger.error("Alembic command timed out")
            return False, "Command timed out"
        except Exception as e:
            logger.error(f"Failed to run Alembic command: {e}")
            return False, str(e)
    
    def get_alembic_config(self):
        """Get Alembic configuration."""
        if not self._alembic_available:
            raise RuntimeError("Alembic is not available or has configuration issues")
            
        if not self.alembic_cfg_path.exists():
            raise FileNotFoundError(f"Alembic config not found: {self.alembic_cfg_path}")
        
        try:
            from alembic.config import Config
            alembic_cfg = Config(str(self.alembic_cfg_path))
            # Override database URL with current settings
            alembic_cfg.set_main_option("sqlalchemy.url", self.settings.database_url)
            return alembic_cfg
        except Exception as e:
            logger.error(f"Failed to create Alembic config: {e}")
            raise
    
    def check_migration_status(self) -> Dict[str, Optional[str]]:
        """Check current migration status."""
        if not self._alembic_available:
            logger.warning("Alembic is not available - cannot check migration status")
            return {
                "current_revision": None,
                "head_revision": None,
                "is_up_to_date": False,
                "needs_migration": False,
                "error": "Alembic not available"
            }
            
        try:
            # Try using Alembic API first
            from alembic.script import ScriptDirectory
            from sqlalchemy import create_engine, text
            
            alembic_cfg = self.get_alembic_config()
            script_dir = ScriptDirectory.from_config(alembic_cfg)
            
            # Get current revision from database
            engine = create_engine(self.settings.database_url, pool_pre_ping=True)
            
            current_rev = None
            try:
                with engine.connect() as conn:
                    # Check if alembic_version table exists
                    result = conn.execute(text(
                        "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'alembic_version')"
                    ))
                    table_exists = result.scalar()
                    
                    if table_exists:
                        # Get current revision from alembic_version table
                        result = conn.execute(text("SELECT version_num FROM alembic_version"))
                        current_rev = result.scalar()
            except Exception as db_error:
                logger.warning(f"Could not query database for current revision: {db_error}")
                current_rev = None
            finally:
                engine.dispose()
            
            # Get head revision from migration scripts
            head_rev = script_dir.get_current_head()
            
            return {
                "current_revision": current_rev,
                "head_revision": head_rev,
                "is_up_to_date": current_rev == head_rev if current_rev is not None else False,
                "needs_migration": current_rev != head_rev if current_rev is not None else True
            }
            
        except Exception as api_error:
            logger.warning(f"Alembic API failed, trying subprocess: {api_error}")
            
            # Fallback to subprocess approach
            success, output = self._run_alembic_command(["current"])
            if not success:
                return {
                    "current_revision": None,
                    "head_revision": None,
                    "is_up_to_date": False,
                    "needs_migration": True,
                    "error": f"Failed to check migration status: {output}"
                }
            
            # Parse subprocess output (basic implementation)
            current_rev = None
            if "Current revision(s)" in output:
                # Extract revision ID from output
                lines = output.split('\n')
                for line in lines:
                    if "Current revision(s)" in line and ":" in line:
                        current_rev = line.split(":")[-1].strip()
                        break
            
            return {
                "current_revision": current_rev,
                "head_revision": "unknown",
                "is_up_to_date": False,
                "needs_migration": current_rev is None
            }
    
    def apply_migrations(self, target_revision: str = "head") -> bool:
        """Apply database migrations."""
        if not self._alembic_available:
            logger.error("Cannot apply migrations - Alembic is not available")
            return False
            
        try:
            # Try using Alembic API first
            from alembic import command
            
            alembic_cfg = self.get_alembic_config()
            logger.info(f"Applying migrations to {target_revision}")
            command.upgrade(alembic_cfg, target_revision)
            logger.info("Migrations applied successfully")
            return True
            
        except Exception as api_error:
            logger.warning(f"Alembic API failed, trying subprocess: {api_error}")
            
            # Fallback to subprocess approach
            success, output = self._run_alembic_command(["upgrade", target_revision])
            if success:
                logger.info("Migrations applied successfully via subprocess")
                return True
            else:
                logger.error(f"Failed to apply migrations: {output}")
                return False
    
    def create_migration(self, message: str, autogenerate: bool = True) -> bool:
        """Create a new migration."""
        if not self._alembic_available:
            logger.error("Cannot create migration - Alembic is not available")
            return False
            
        try:
            from alembic import command
            
            alembic_cfg = self.get_alembic_config()
            logger.info(f"Creating migration: {message}")
            command.revision(alembic_cfg, message=message, autogenerate=autogenerate)
            logger.info("Migration created successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to create migration: {e}")
            return False
    
    def ensure_database_is_current(self, auto_upgrade: bool = True) -> bool:
        """Ensure database is up to date with migrations."""
        if not self._alembic_available:
            logger.warning("Alembic is not available - skipping migration check")
            logger.info("Application will continue with basic database initialization only")
            return True  # Allow application to continue
            
        try:
            status = self.check_migration_status()
            
            if status.get("error"):
                logger.warning(f"Could not check migration status: {status['error']}")
                logger.info("Continuing with application startup - manual migration may be needed")
                return True  # Allow application to continue in development
            
            if status["is_up_to_date"]:
                logger.info("Database is up to date with migrations")
                return True
            
            if status["needs_migration"]:
                if auto_upgrade:
                    logger.info("Database needs migration - applying automatically")
                    success = self.apply_migrations()
                    if success:
                        logger.info("Database migrations completed successfully")
                        return True
                    else:
                        logger.error("Failed to apply migrations automatically")
                        return False
                else:
                    logger.warning("Database needs migration but auto_upgrade is disabled")
                    logger.info("Run 'alembic upgrade head' manually to apply migrations")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to ensure database is current: {e}")
            logger.info("Continuing with application startup - check migrations manually")
            return True  # Allow application to continue in development


# Global instance
migration_manager = MigrationManager()


def check_and_apply_migrations(auto_upgrade: bool = True) -> bool:
    """Check and optionally apply database migrations."""
    try:
        return migration_manager.ensure_database_is_current(auto_upgrade)
    except Exception as e:
        logger.error(f"Migration check failed: {e}")
        logger.info("Application will continue startup - verify database manually")
        return True  # Allow application to continue


def get_migration_status() -> Dict[str, Optional[str]]:
    """Get current migration status."""
    try:
        return migration_manager.check_migration_status()
    except Exception as e:
        logger.error(f"Failed to get migration status: {e}")
        return {
            "current_revision": None,
            "head_revision": None,
            "is_up_to_date": False,
            "needs_migration": False,
            "error": str(e)
        }
