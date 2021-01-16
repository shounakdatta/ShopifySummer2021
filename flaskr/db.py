import sqlite3
import os
import psycopg2
import click
from flask import current_app, g
from flask.cli import with_appcontext


# Retrieves existing db instance or creates a new one
def get_db():
    if 'db' not in g:
        # g.db = sqlite3.connect(
        #     current_app.config['DATABASE'],
        #     detect_types=sqlite3.PARSE_DECLTYPES
        # )
        # g.db.row_factory = sqlite3.Row

        if os.environ.get('DATABASE_URL') is None:
            g.db = sqlite3.connect(
                current_app.config['DATABASE'],
                detect_types=sqlite3.PARSE_DECLTYPES
            )
            g.db.row_factory = sqlite3.Row
        else:
            DATABASE_URL = os.environ['DATABASE_URL']
            g.db = psycopg2.connect(DATABASE_URL, sslmode='require')

    return g.db


# Closes existing db instance
def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()


# Executes schema.sql upon intialization
def init_db():
    db = get_db()

    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))


# Defines a CLI command called init-db which calls the init-db function above
@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')


# Registers close_db and init_db_command functions with the Flask instance
def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
