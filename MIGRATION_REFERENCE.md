# Migration Quick Reference

## Essential Commands

| Command | Description |
|---------|-------------|
| `python migrate.py create "message"` | Create new migration |
| `python migrate.py upgrade` | Apply all pending migrations |
| `python migrate.py current` | Show current revision |
| `python migrate.py history` | Show migration history |
| `python migrate.py downgrade <revision>` | Rollback to revision |

## Example Workflow

```bash
# 1. After modifying models, create migration
python migrate.py create "Add user preferences table"

# 2. Review the generated migration file
cat alembic/versions/latest_*.py

# 3. Apply the migration
python migrate.py upgrade

# 4. Verify it worked
python migrate.py current
```

## Troubleshooting

- **Models not detected**: Check imports in `alembic/env.py`
- **Migration fails**: Check database permissions and syntax
- **Conflicts**: Manually resolve or use `alembic merge`
- **Need to rollback**: Use `python migrate.py downgrade <revision>`

## Files

- `alembic.ini` - Configuration
- `alembic/env.py` - Environment setup
- `alembic/versions/` - Migration files
- `migrate.py` - Helper script
