"""
Module: models
SQLAlchemy ORM model for Customer Accounts
"""
import logging
from flask_sqlalchemy import SQLAlchemy

logger = logging.getLogger("flask.app")

# Create the SQLAlchemy instance (bound to the app in __init__.py)
db = SQLAlchemy()


def init_db(app):
    """
    Bind SQLAlchemy to the app and create all tables.

    This is the ONLY place db.init_app(app) is called, so that tests can
    set app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:" before
    invoking this function — without triggering a real Postgres connection.
    """
    logger.debug("Initialising database...")
    db.init_app(app)
    with app.app_context():
        db.create_all()
    logger.info("Database tables created (if not already present).")


######################################################################
# Account Model
######################################################################


class DataValidationError(Exception):
    """Raised when invalid data is passed to deserialize()"""


class Account(db.Model):
    """
    Class that represents a Customer Account

    Schema
    ------
    id           INTEGER   primary key, auto-increment
    name         VARCHAR   customer full name
    email        VARCHAR   customer email address
    address      VARCHAR   customer postal address
    phone_number VARCHAR   customer phone number
    """

    __tablename__ = "account"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    email = db.Column(db.String(64), nullable=False)
    address = db.Column(db.String(256), nullable=False)
    phone_number = db.Column(db.String(32), nullable=False)

    # ------------------------------------------------------------------
    # Representation
    # ------------------------------------------------------------------

    def __repr__(self):
        return f"<Account {self.name} id=[{self.id}]>"

    # ------------------------------------------------------------------
    # Serialisation
    # ------------------------------------------------------------------

    def serialize(self) -> dict:
        """Convert the Account object to a plain Python dict."""
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "address": self.address,
            "phone_number": self.phone_number,
        }

    def deserialize(self, data: dict) -> "Account":
        """
        Populate the Account from a dict.

        Parameters
        ----------
        data : dict
            Dictionary containing account field values.

        Raises
        ------
        DataValidationError
            If any required field is missing or the data argument is not a dict.
        """
        try:
            self.name = data["name"]
            self.email = data["email"]
            self.address = data["address"]
            self.phone_number = data["phone_number"]
        except AttributeError as error:
            raise DataValidationError(
                "Invalid Account: body of request contained bad or no data — "
                "Error message: " + str(error)
            ) from error
        except KeyError as error:
            raise DataValidationError(
                "Invalid Account: missing field — " + str(error)
            ) from error
        return self

    # ------------------------------------------------------------------
    # CRUD operations
    # ------------------------------------------------------------------

    def create(self):
        """Persist a new Account to the database."""
        logger.debug("Creating account: %s", self.name)
        self.id = None  # let the database assign the PK
        db.session.add(self)
        db.session.commit()

    def update(self):
        """Persist changes to an existing Account."""
        logger.debug("Updating account: %s", self.name)
        if not self.id:
            raise DataValidationError("Cannot update an Account without an id")
        db.session.commit()

    def delete(self):
        """Remove this Account from the database."""
        logger.debug("Deleting account: %s", self.name)
        db.session.delete(self)
        db.session.commit()

    # ------------------------------------------------------------------
    # Class-level finders
    # ------------------------------------------------------------------

    @classmethod
    def all(cls) -> list:
        """Return all Accounts."""
        logger.debug("Fetching all accounts")
        return cls.query.all()

    @classmethod
    def find(cls, account_id: int) -> "Account | None":
        """Find a single Account by primary key."""
        logger.debug("Fetching account with id=%s", account_id)
        return cls.query.get(account_id)
