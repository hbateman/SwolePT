# Database Migrations

This directory contains database migration scripts for the SwolePT application.

## Migration Files

- `001_initial_schema.sql`: Creates the initial database schema with tables for users, workouts, and exercises.
- `001_initial_schema_down.sql`: Rolls back the initial schema.

## Applying Migrations

To apply a migration, use the `apply_migration.py` script:

```bash
# Set the required environment variables
export DATABASE_HOST=your-database-host
export DATABASE_PORT=5432
export DATABASE_NAME=your-database-name
export DATABASE_USER=your-database-user
export DATABASE_PASSWORD=your-database-password

# Apply an "up" migration (creates/updates schema)
python apply_migration.py 001_initial_schema.sql up

# Apply a "down" migration (rolls back changes)
python apply_migration.py 001_initial_schema_down.sql down
```

If the direction is not specified, "up" is assumed by default.

## Migration Naming Convention

Migration files should follow this naming convention:
- `NNN_description.sql`: For "up" migrations
- `NNN_description_down.sql`: For corresponding "down" migrations

Where NNN is a sequential number (001, 002, etc.) and description is a brief description of what the migration does.

## Best Practices

1. Always make migrations idempotent by using `IF NOT EXISTS` and `IF EXISTS` clauses.
2. Include both "up" and "down" migrations when possible.
3. Test migrations in a development environment before applying to production.
4. Back up your database before applying migrations in production.
5. Document any manual steps required alongside migrations.
6. Drop objects in the reverse order of their creation in down migrations. 