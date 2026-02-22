import logging
import click
from flask import Flask
from flask_talisman import Talisman
from flask_cors import CORS
from service import config
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] [%(module)s] %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S%z",
)
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = config.DATABASE_URI
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = config.SQLALCHEMY_TRACK_MODIFICATIONS
app.logger.setLevel(logging.INFO)
app.logger.info("Customer Accounts Service starting...")
talisman = Talisman(app, force_https=False)
CORS(app)
from service.models import db, init_db  # noqa: E402
init_db(app)
from service import routes  # noqa: F401, E402
from service.common import error_handlers  # noqa: F401, E402
@app.cli.command("db-create")
def db_create():
    """Drop all tables and re-create them (WARNING: destroys data)."""
    with app.app_context():
        db.drop_all()
        db.create_all()
    click.echo("Database tables created.")
