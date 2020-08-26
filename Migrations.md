Migrations
==========

* Date: 26 Aug 2020
* Author: Dylan Lott <lott.dylan@gmail.com>

# alembic 

We use Alembic to run migrations against our SQLite database. 

The alembic.ini file contains the connection URL to the sqlite database. 

To create a new migration, run `alembic revision -m "describe your migration here"`

After that's run, go edit it in the `/api/alembic/revisions/` folder. 

Add an up and a downgrade so that we can revert in prod if necessary. 

To run the actual migration against the database, simply run `alembic upgrade head`
To downgrade if there are issues, run `alembic downgrade 1`. This will revert the last revision (the one you just ran) and put the database back into the correct state, assuming you wrote your downgrade revision correctly.
If you want to read more about alembic, we encourage you to read the documentation which can be found [here](https://alembic.sqlalchemy.org).


