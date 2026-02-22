"""
Module: routes
RESTful API routes for the Customer Accounts service
"""
import logging
from flask import jsonify, request, abort
from service import app
from service.models import Account, DataValidationError
from service.common.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_204_NO_CONTENT,
    HTTP_404_NOT_FOUND,
    HTTP_400_BAD_REQUEST,
)

logger = logging.getLogger("flask.app")


######################################################################
# I N D E X
######################################################################


@app.route("/")
def index():
    """Root URL — returns service info."""
    return jsonify(
        name="Customer Accounts REST API Service",
        version="1.0",
    ), HTTP_200_OK


######################################################################
# H E A L T H   C H E C K
######################################################################


@app.route("/health")
def health():
    """Health endpoint — used by load-balancers / orchestration."""
    return jsonify(status="OK"), HTTP_200_OK



######################################################################
# C R E A T E   A C C O U N T
######################################################################


@app.route("/accounts", methods=["POST"])
def create_accounts():
    """
    Create a new Account.

    This endpoint will create an Account based on the data in the body
    that is posted.
    """
    app.logger.info("Request to create an Account")

    check_content_type("application/json")
    account = Account()

    try:
        account.deserialize(request.get_json())
    except DataValidationError as error:
        abort(HTTP_400_BAD_REQUEST, str(error))

    account.create()

    app.logger.info("Account with ID [%s] created.", account.id)
    return jsonify(account.serialize()), HTTP_201_CREATED


######################################################################
# R E A D   A C C O U N T
######################################################################


@app.route("/accounts/<int:account_id>", methods=["GET"])
def get_accounts(account_id):
    """
    Read a single Account.

    This endpoint will return an Account based on its id.
    """
    app.logger.info("Request to read Account with id: %s", account_id)

    account = Account.find(account_id)
    if not account:
        abort(HTTP_404_NOT_FOUND, f"Account with id [{account_id}] could not be found.")

    app.logger.info("Returning account: %s", account.name)
    return jsonify(account.serialize()), HTTP_200_OK


######################################################################
# L I S T   A C C O U N T S
######################################################################


@app.route("/accounts", methods=["GET"])
def list_accounts():
    """
    List all Accounts.

    This endpoint will return a list of all Accounts.
    """
    app.logger.info("Request to list Accounts")

    accounts = Account.all()
    account_list = [account.serialize() for account in accounts]

    app.logger.info("Returning [%d] accounts", len(account_list))
    return jsonify(account_list), HTTP_200_OK


######################################################################
# U P D A T E   A C C O U N T
######################################################################


@app.route("/accounts/<int:account_id>", methods=["PUT"])
def update_accounts(account_id):
    """
    Update an existing Account.

    This endpoint will update an Account based on the posted data.
    """
    app.logger.info("Request to update Account with id: %s", account_id)

    account = Account.find(account_id)
    if not account:
        abort(HTTP_404_NOT_FOUND, f"Account with id [{account_id}] could not be found.")

    check_content_type("application/json")
    try:
        account.deserialize(request.get_json())
    except DataValidationError as error:
        abort(HTTP_400_BAD_REQUEST, str(error))

    account.update()

    app.logger.info("Account with ID [%s] updated.", account.id)
    return jsonify(account.serialize()), HTTP_200_OK


######################################################################
# D E L E T E   A C C O U N T
######################################################################


@app.route("/accounts/<int:account_id>", methods=["DELETE"])
def delete_accounts(account_id):
    """
    Delete an Account.

    This endpoint will delete an Account based on its id.
    A DELETE on a non-existing account still returns 204.
    """
    app.logger.info("Request to delete Account with id: %s", account_id)

    account = Account.find(account_id)
    if account:
        account.delete()
        app.logger.info("Account with ID [%s] deleted.", account_id)

    return "", HTTP_204_NO_CONTENT


######################################################################
# U T I L I T Y
######################################################################


def check_content_type(media_type):
    """Raise a 415 if the request Content-Type is wrong."""
    content_type = request.headers.get("Content-Type")
    if content_type and content_type == media_type:
        return
    app.logger.error("Invalid Content-Type: %s", content_type)
    abort(
        415,
        f"Content-Type must be {media_type}",
    )
