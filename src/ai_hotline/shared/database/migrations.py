"""Database migration utilities for application startup."""

import logging
from pathlib import Path
from alembic.config import Config
from alembic import command
from alembic.script import ScriptDirectory
from alembic.runtime.environment import EnvironmentContext

from src.ai_hotline.shared.config.settings import get_settings

logger = logging.getLogger(__name__)


class MigrationManager:
    """Manages database migrations for the application."""
    
    def __init__(self):
        self.settings = get_settings()
        self.project_root = Path(__file__).parent.parent.parent.parent.parent
        self.alembic_cfg_path = self.project_root / "alembic.ini"
        
    def get_alembic_config(self) -> Config:
        """Get Alembic configuration."""
        if not self.alembic_cfg_path.exists():
            raise FileNotFoundError(f"Alembic config not found: {self.alembic_cfg_path}")
        
        alembic_cfg = Config(str(self.alembic_cfg_path))
        # Override database URL with current settings
        alembic_cfg.set_main_option("sqlalchemy.url", self.settings.database_url)
        return alembic_cfg
    
    def check_migration_status(self) -> dict:
        """Check current migration status."""
        try:
            alembic_cfg = self.get_alembic_config()
            script_dir = ScriptDirectory.from_config(alembic_cfg)
            
            # Get current revision
            def get_current_revision(rev, context):
                return rev
            
            with EnvironmentContext(
                alembic_cfg,
                script_dir,
                fn=get_current_revision
            ) as context:
                current_rev = context.get_current_revision()
            
            # Get head revision
            head_rev = script_dir.get_current_head()
            
            return {
                "current_revision": current_rev,
                "head_revision": head_rev,
                "is_up_to_date": current_rev == head_rev,
                "needs_migration": current_rev != head_rev
            }
        except Exception as e:
            logger.error(f"Failed to check migration status: {e}")
            return {
                "current_revision": None,
                "head_revision": None,
                "is_up_to_date": False,
                "needs_migration": True,
                "error": str(e)
            }
    
    def apply_migrations(self, target_revision: str = "head") -> bool:
        """Apply database migrations."""
        try:
            alembic_cfg = self.get_alembic_config()
            logger.info(f"Applying migrations to {target_revision}")
            command.upgrade(alembic_cfg, target_revision)
            logger.info("Migrations applied successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to apply migrations: {e}")
            return False
    
    def create_migration(self, message: str, autogenerate: bool = True) -> bool:
        """Create a new migration."""
        try:
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
        try:
            status = self.check_migration_status()
            
            if status.get("error"):
                logger.warning(f"Could not check migration status: {status['error']}")
                return False
            
            if status["is_up_to_date"]:
                logger.info("Database is up to date")
                return True
            
            if status["needs_migration"] and auto_upgrade:
                logger.info("Database needs migration, applying automatically")
                return self.apply_migrations()
            elif status["needs_migration"]:
                logger.warning("Database needs migration but auto_upgrade is disabled")
                return False
            
            return True
        except Exception as e:
            logger.error(f"Failed to ensure database is current: {e}")
            return False


# Global instance
migration_manager = MigrationManager()


def check_and_apply_migrations(auto_upgrade: bool = True) -> bool:
    """Check and optionally apply database migrations."""
    return migration_manager.ensure_database_is_current(auto_upgrade)


def get_migration_status() -> dict:
    """Get current migration status."""
    return migration_manager.check_migration_status()
