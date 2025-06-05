#!/usr/bin/env python3
"""
Database migration management script.

This script provides easy commands for managing database migrations using Alembic.
"""

import os
import sys
import subprocess
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / 'src'))

def run_alembic_command(command_args):
    """Run an alembic command."""
    try:
        result = subprocess.run(
            ['python', '-m', 'alembic'] + command_args,
            cwd=project_root,
            capture_output=True,
            text=True
        )
        
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
        
        return result.returncode == 0
    except Exception as e:
        print(f"Error running alembic command: {e}", file=sys.stderr)
        return False

def create_migration(message):
    """Create a new migration."""
    print(f"Creating migration: {message}")
    return run_alembic_command(['revision', '--autogenerate', '-m', message])

def upgrade_database(revision='head'):
    """Upgrade database to a specific revision."""
    print(f"Upgrading database to {revision}")
    return run_alembic_command(['upgrade', revision])

def downgrade_database(revision):
    """Downgrade database to a specific revision."""
    print(f"Downgrading database to {revision}")
    return run_alembic_command(['downgrade', revision])

def show_current_revision():
    """Show current database revision."""
    print("Current database revision:")
    return run_alembic_command(['current'])

def show_history():
    """Show migration history."""
    print("Migration history:")
    return run_alembic_command(['history'])

def show_pending():
    """Show pending migrations."""
    print("Pending migrations:")
    return run_alembic_command(['current', '--verbose'])

def init_database():
    """Initialize database with all migrations."""
    print("Initializing database...")
    return upgrade_database('head')

def main():
    """Main CLI interface."""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python migrate.py create 'migration message'  # Create new migration")
        print("  python migrate.py upgrade [revision]          # Upgrade to revision (default: head)")
        print("  python migrate.py downgrade <revision>        # Downgrade to revision")
        print("  python migrate.py current                     # Show current revision")
        print("  python migrate.py history                     # Show migration history")
        print("  python migrate.py pending                     # Show pending migrations")
        print("  python migrate.py init                        # Initialize database")
        sys.exit(1)
    
    command = sys.argv[1]
    
    try:
        if command == 'create':
            if len(sys.argv) < 3:
                print("Error: Migration message is required")
                sys.exit(1)
            message = sys.argv[2]
            success = create_migration(message)
        
        elif command == 'upgrade':
            revision = sys.argv[2] if len(sys.argv) > 2 else 'head'
            success = upgrade_database(revision)
        
        elif command == 'downgrade':
            if len(sys.argv) < 3:
                print("Error: Target revision is required")
                sys.exit(1)
            revision = sys.argv[2]
            success = downgrade_database(revision)
        
        elif command == 'current':
            success = show_current_revision()
        
        elif command == 'history':
            success = show_history()
        
        elif command == 'pending':
            success = show_pending()
        
        elif command == 'init':
            success = init_database()
        
        else:
            print(f"Unknown command: {command}")
            success = False
        
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()
