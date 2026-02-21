"""
Module: config
Configuration for the Flask application / SQLAlchemy
"""
import os

# Default to a local Postgres database; can be overridden via env var
DATABASE_URI = os.getenv(
    "DATABASE_URI",
    "postgresql://postgres:postgres@localhost/postgres",
)

# Use SQLite in-memory database during testing
TESTING_DATABASE_URI = "sqlite:///:memory:"

SQLALCHEMY_TRACK_MODIFICATIONS = False
