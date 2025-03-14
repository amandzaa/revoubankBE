from datetime import datetime
import sqlite3
import os
import click
from flask import current_app, g
from flask.cli import with_appcontext

def get_db():
    """Connect to the application's configured database."""
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db(e=None):
    """Close the database connection."""
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db():
    """Initialize the database with the schema."""
    db = get_db()
    # Get the schema path relative to this file
    schema_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'schema.sql')
    with open(schema_path, 'r') as f:
        db.executescript(f.read())
    db.commit()

def query_db(query, args=(), one=False):
    """Execute a database query."""
    cur = get_db().cursor()
    cur.execute(query, args)
    if one:
        return cur.fetchone()
    else:
        return cur.fetchall()
    
def execute_db(query, args, commit=True):
    """Execute a database query with commit."""
    cur = get_db().cursor()
    cur.execute(query, args)
    if commit:
        get_db().commit()
    return cur.lastrowid

def update_timestamp(table, id_field, id_value):
    """Update the timestamp for a specific record in the database."""
    now = datetime.datetime.now()
    query = f"UPDATE {table} SET updated_at = CURRENT_TIMESTAMP WHERE {id_field} =?"
    execute_db(query, (now, id_value))
    return get_db().total_changes > 0

@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')

def init_app(app):
    """Register database functions with the Flask app."""
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
    # Ensure the instance folder exists
    os.makedirs(app.instance_path, exist_ok=True)
    # Initialize the database if it doesn't exist
    if not os.path.exists(os.path.join(app.instance_path, 'revobank.db')):
        with app.app_context():
            init_db()
            