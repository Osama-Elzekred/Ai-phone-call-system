# Database Migrations Guide

This guide explains how to manage database schema changes using Alembic migrations in the AI Hotline Backend project.

## Overview

We use [Alembic](https://alembic.sqlalchemy.org/) for database migrations, which provides:
- Version control for database schema
- Automatic migration generation from SQLAlchemy models
- Rollback capabilities
- Multi-environment support

## Quick Start

### 1. Create a New Migration

When you add new models or modify existing ones, create a migration:

```bash
# Create migration with automatic detection of changes
python migrate.py create "Add new feature table"

# Or use alembic directly
python -m alembic revision --autogenerate -m "Add new feature table"
```

### 2. Apply Migrations

```bash
# Apply all pending migrations
python migrate.py upgrade

# Apply to a specific revision
python migrate.py upgrade abc123

# Initialize database (same as upgrade to head)
python migrate.py init
```

### 3. Check Migration Status

```bash
# Show current database revision
python migrate.py current

# Show migration history
python migrate.py history

# Show pending migrations
python migrate.py pending
```

### 4. Rollback Changes

```bash
# Rollback to a specific revision
python migrate.py downgrade abc123

# Rollback one migration
python migrate.py downgrade -1
```

## File Structure

```
alembic/
├── env.py              # Alembic environment configuration
├── script.py.mako      # Template for new migrations
└── versions/           # Migration files
    └── 6c6fcf9133ce_initial_schema.py
alembic.ini             # Alembic configuration
migrate.py              # Migration management script
```

## Migration Workflow

### 1. Development Workflow

1. **Modify Models**: Update your SQLAlchemy models in `src/ai_hotline/modules/*/infrastructure/persistence/models.py`

2. **Create Migration**: 
   ```bash
   python migrate.py create "Descriptive message about changes"
   ```

3. **Review Migration**: Check the generated file in `alembic/versions/` to ensure it's correct

4. **Apply Migration**:
   ```bash
   python migrate.py upgrade
   ```

5. **Test**: Verify your application works with the new schema

### 2. Production Workflow

1. **Backup Database**: Always backup before applying migrations in production

2. **Test Migrations**: Test on a copy of production data first

3. **Apply Migrations**:
   ```bash
   python migrate.py upgrade
   ```

4. **Verify**: Check that the application works correctly

## Common Operations

### Adding a New Table

1. Create the SQLAlchemy model in the appropriate module
2. Import it in `alembic/env.py` (already configured for existing modules)
3. Create migration: `python migrate.py create "Add user_preferences table"`
4. Apply: `python migrate.py upgrade`

### Modifying an Existing Table

1. Update the SQLAlchemy model
2. Create migration: `python migrate.py create "Add email_verified column to users"`
3. Review the generated migration file
4. Apply: `python migrate.py upgrade`

### Adding Indexes

1. Add indexes to your SQLAlchemy model:
   ```python
   class UserModel(TenantBaseModel):
       email = Column(String(255), nullable=False, index=True)
   ```
2. Create migration: `python migrate.py create "Add index on user email"`
3. Apply: `python migrate.py upgrade`

## Best Practices

### 1. Migration Messages

Use clear, descriptive messages:
- ✅ "Add user_preferences table with theme and language settings"
- ✅ "Add email_verified column to users table"
- ✅ "Create index on calls.phone_number for faster lookups"
- ❌ "Update schema"
- ❌ "Fix stuff"

### 2. Review Generated Migrations

Always review auto-generated migrations before applying:
- Check that all intended changes are included
- Verify data type mappings are correct
- Ensure foreign key constraints are properly handled
- Check for any unintended changes

### 3. Data Migrations

For complex data transformations, you may need custom migration code:

```python
def upgrade() -> None:
    # Schema changes
    op.add_column('users', sa.Column('full_name', sa.String(200)))
    
    # Data migration
    connection = op.get_bind()
    connection.execute(
        text("UPDATE users SET full_name = first_name || ' ' || last_name")
    )
    
    # Remove old columns
    op.drop_column('users', 'first_name')
    op.drop_column('users', 'last_name')
```

### 4. Environment-Specific Migrations

The system automatically uses the correct database URL from your environment settings.

### 5. Backup Strategy

- Always backup production data before migrations
- Test migrations on a copy of production data
- Have a rollback plan ready

## Troubleshooting

### Migration Conflicts

If multiple developers create migrations simultaneously:

1. **Merge Conflicts**: Resolve conflicts in migration files manually
2. **Revision Conflicts**: Use `alembic merge` to create a merge revision
3. **Schema Drift**: Drop and recreate development databases if needed

### Failed Migrations

If a migration fails:

1. **Check Error Message**: Read the error carefully
2. **Manual Intervention**: Sometimes you need to fix the database state manually
3. **Mark as Applied**: Use `alembic stamp` if you've manually applied changes
4. **Rollback**: Use `python migrate.py downgrade` to rollback

### Schema Detection Issues

If Alembic doesn't detect your changes:

1. **Check Imports**: Ensure your models are imported in `alembic/env.py`
2. **Restart**: Restart your development environment
3. **Manual Migration**: Create an empty migration and add operations manually

## Configuration

### Database URL

The database URL is automatically loaded from your environment settings. Make sure your `.env` file has:

```env
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
```

### Alembic Configuration

Main configuration is in `alembic.ini`. Key settings:

- `script_location`: Where migration scripts are stored
- `sqlalchemy.url`: Database URL (overridden by env.py)
- `file_template`: Naming pattern for migration files

## Multi-Tenant Considerations

Our models include tenant isolation through `TenantBaseModel`. When creating migrations:

- Ensure tenant_id columns are properly indexed
- Consider data migration impacts across tenants
- Test with multi-tenant data scenarios

## Integration with CI/CD

In your deployment pipeline:

```bash
# Check for pending migrations
python migrate.py pending

# Apply migrations
python migrate.py upgrade

# Verify database state
python migrate.py current
```

## Examples

### Example 1: Adding a New Feature

```bash
# 1. Add new model in code
# 2. Create migration
python migrate.py create "Add notification_preferences table"

# 3. Review generated migration
cat alembic/versions/latest_migration.py

# 4. Apply migration
python migrate.py upgrade

# 5. Verify
python migrate.py current
```

### Example 2: Modifying Existing Table

```bash
# 1. Update model in code (e.g., add column)
# 2. Create migration
python migrate.py create "Add avatar_url to users table"

# 3. Apply migration
python migrate.py upgrade
```

### Example 3: Rolling Back

```bash
# Check current state
python migrate.py current

# See history
python migrate.py history

# Rollback to specific revision
python migrate.py downgrade abc123

# Verify
python migrate.py current
```

## Support

For more information:
- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- Check the project's README.md for specific setup instructions
