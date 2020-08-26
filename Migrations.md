# Migrations

- Date: 26 Aug 2020
- Author: Dylan Lott <lott.dylan@gmail.com>

## alembic

We use Alembic to run migrations against our SQLite database.

The alembic.ini file contains the connection URL to the sqlite database.

To create a new migration, run `alembic revision -m "describe your migration here"`

After that's run, go edit it in the `/api/alembic/revisions/` folder.

Add an up and a downgrade so that we can revert in prod if necessary.

To run the actual migration against the database, simply run `alembic upgrade head`
To downgrade if there are issues, run `alembic downgrade 1`. This will revert the last revision (the one you just ran) and put the database back into the correct state, assuming you wrote your downgrade revision correctly.
If you want to read more about alembic, we encourage you to read the documentation which can be found [here](https://alembic.sqlalchemy.org).

### Migrations in prod

_*Before migrating production databases:*_

1. Always run a backup before migrating in production.
2. Make sure that there is a proper downgrade for any upgrade that you're running.
3. Give the team a heads up that you're migrating prod.
4. Make sure the migration has been tested locally for soundness before trying it in prod.

### Running the migration

To run a migration in prod, get the latest code pulled down to master, and then run `alembic upgrade head` from the project root. This will run any unapplied migrations to the production SQLite database.

If there are issues, downgrade the database immediately and attempt to get the server back online.
