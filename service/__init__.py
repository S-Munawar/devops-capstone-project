"""
Package: service
Package for the Customer Accounts application
"""
import logging
import click
from flask import Flask
from service import config

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] [%(module)s] %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S%z",
)

# ---------------------------------------------------------------------------
# Create & configure the Flask application
# ---------------------------------------------------------------------------
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = config.DATABASE_URI
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = config.SQLALCHEMY_TRACK_MODIFICATIONS

app.logger.setLevel(logging.INFO)
app.logger.info("Customer Accounts Service starting...")

# ---------------------------------------------------------------------------
# Initialise SQLAlchemy and create tables
# db.init_app(app) is called here so that production requests work correctly.
# Tests override DATABASE_URI via the environment BEFORE importing service,
# so config.DATABASE_URI already contains the SQLite URI when this runs.
# ---------------------------------------------------------------------------
from service.models import db, init_db  # noqa: E402

init_db(app)

# ---------------------------------------------------------------------------
# Register routes and error handlers
# ---------------------------------------------------------------------------
from service import routes  # noqa: F401, E402
from service.common import error_handlers  # noqa: F401, E402


# ---------------------------------------------------------------------------
# Flask CLI command: flask db-create
# ---------------------------------------------------------------------------
@app.cli.command("db-create")
def db_create():
    """Drop all tables and re-create them (WARNING: destroys data)."""
    with app.app_context():
        db.drop_all()
        db.create_all()
    click.echo("Database tables created.")
