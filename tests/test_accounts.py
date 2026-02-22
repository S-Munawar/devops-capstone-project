"""
Test Cases for Customer Accounts Service

Test cases can be run with:
    nosetests
    coverage report -m

While debugging just one test case use:
    nose2 -v tests.test_accounts.TestAccountService.test_create_account
"""
import os
import logging
import unittest
from unittest import TestCase

# -----------------------------------------------------------------------
# Force SQLite in-memory BEFORE importing the service package.
# This ensures that service/__init__.py sees the test URI when it runs
# db.init_app(app) so no Postgres connection is ever attempted.
# -----------------------------------------------------------------------
os.environ["DATABASE_URI"] = "sqlite:///:memory:"

from service import app, talisman  # noqa: E402
from service.models import db, Account  # noqa: E402
from service.common import status  # noqa: E402
from tests.factories import AccountFactory  # noqa: E402

BASE_URL = "/accounts"
CONTENT_TYPE_JSON = "application/json"
HTTPS_ENVIRON = {'wsgi.url_scheme': 'https'}

logging.disable(logging.CRITICAL)


######################################################################
# A C C O U N T   T E S T   C A S E S
######################################################################


class TestAccountService(TestCase):
    """Account Service Tests"""

    # ------------------------------------------------------------------
    # Class-level setup / teardown (run once per test class)
    # ------------------------------------------------------------------

    @classmethod
    def setUpClass(cls):
        """The app is already initialised with SQLite by the module-level env var."""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.logger.setLevel(logging.CRITICAL)
        talisman.force_https = False

    @classmethod
    def tearDownClass(cls):
        """Nothing to tear down at class level."""

    # ------------------------------------------------------------------
    # Method-level setup / teardown (run before/after every test)
    # ------------------------------------------------------------------

    def setUp(self):
        """Create a fresh test client and empty the database tables."""
        self.app_context = app.app_context()
        self.app_context.push()
        self.client = app.test_client()
        db.session.query(Account).delete()
        db.session.commit()

    def tearDown(self):
        """Roll back any open transactions and pop the app context."""
        db.session.remove()
        self.app_context.pop()

    # ------------------------------------------------------------------
    # H E L P E R
    # ------------------------------------------------------------------

    def _create_accounts(self, count):
        """Factory method to create accounts in bulk for testing."""
        accounts = []
        for _ in range(count):
            account = AccountFactory()
            response = self.client.post(
                BASE_URL,
                json=account.serialize(),
                content_type=CONTENT_TYPE_JSON,
            )
            self.assertEqual(response.status_code, 201)
            new_account = response.get_json()
            account.id = new_account["id"]
            accounts.append(account)
        return accounts

    # ------------------------------------------------------------------
    # T E S T   C A S E S
    # ------------------------------------------------------------------

    def test_create_account(self):
        """It should Create a new Account"""
        account = AccountFactory()
        response = self.client.post(
            BASE_URL,
            json=account.serialize(),
            content_type=CONTENT_TYPE_JSON,
        )
        self.assertEqual(response.status_code, 201)
        created_account = response.get_json()
        self.assertEqual(created_account["name"], account.name)
        self.assertEqual(created_account["email"], account.email)
        self.assertEqual(created_account["address"], account.address)
        self.assertEqual(created_account["phone_number"], account.phone_number)
        self.assertIsNotNone(created_account["id"])

    def test_get_account(self):
        """It should Read a single Account"""
        account = self._create_accounts(1)[0]
        response = self.client.get(
            f"{BASE_URL}/{account.id}",
            content_type=CONTENT_TYPE_JSON,
        )
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data["name"], account.name)

    def test_get_account_not_found(self):
        """It should not Read an Account that is not found"""
        response = self.client.get(f"{BASE_URL}/0")
        self.assertEqual(response.status_code, 404)

    def test_list_accounts(self):
        """It should Get a list of Accounts"""
        self._create_accounts(5)
        response = self.client.get(BASE_URL)
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(len(data), 5)

    def test_update_account(self):
        """It should Update an existing Account"""
        # Create an account first
        test_account = AccountFactory()
        response = self.client.post(
            BASE_URL,
            json=test_account.serialize(),
            content_type=CONTENT_TYPE_JSON,
        )
        self.assertEqual(response.status_code, 201)
        new_account = response.get_json()

        # Update the phone_number field
        new_account["phone_number"] = "555-1111"
        response = self.client.put(
            f"{BASE_URL}/{new_account['id']}",
            json=new_account,
            content_type=CONTENT_TYPE_JSON,
        )
        self.assertEqual(response.status_code, 200)
        updated_account = response.get_json()
        self.assertEqual(updated_account["phone_number"], "555-1111")

    def test_delete_account(self):
        """It should Delete an Account"""
        account = self._create_accounts(1)[0]
        response = self.client.delete(f"{BASE_URL}/{account.id}")
        self.assertEqual(response.status_code, 204)

    def test_method_not_allowed(self):
        """It should not allow an illegal method call"""
        # DELETE on the collection URL is not routed → 405
        response = self.client.delete(BASE_URL)
        self.assertEqual(response.status_code, 405)

    def test_security_headers(self):
        """It should return security headers"""
        response = self.client.get('/', environ_overrides=HTTPS_ENVIRON)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        headers = {
            'X-Frame-Options': 'SAMEORIGIN',
            'X-Content-Type-Options': 'nosniff',
            'Content-Security-Policy': "default-src 'self'; object-src 'none'",
            'Referrer-Policy': 'strict-origin-when-cross-origin',
        }
        for key, value in headers.items():
            self.assertEqual(response.headers.get(key), value)

    def test_cors_security(self):
        """It should return a CORS header"""
        response = self.client.get('/', environ_overrides=HTTPS_ENVIRON)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Check for the CORS header
        self.assertEqual(response.headers.get('Access-Control-Allow-Origin'), '*')


######################################################################
# Entry point
######################################################################

if __name__ == "__main__":
    unittest.main()
