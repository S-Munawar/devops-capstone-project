"""
Module: error_handlers
Flask error handlers for the Customer Accounts service
"""
import logging
from flask import jsonify
from service import app
from service.common.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_405_METHOD_NOT_ALLOWED,
    HTTP_500_INTERNAL_SERVER_ERROR,
)

logger = logging.getLogger("flask.app")


######################################################################
# Error Handlers
######################################################################


@app.errorhandler(HTTP_405_METHOD_NOT_ALLOWED)
def method_not_allowed(error):
    """Handle 405 Method Not Allowed"""
    app.logger.warning("Method Not Allowed: %s", error)
    return (
        jsonify(
            status=405,
            error="Method Not Allowed",
            message=str(error),
        ),
        HTTP_405_METHOD_NOT_ALLOWED,
    )


@app.errorhandler(HTTP_400_BAD_REQUEST)
def bad_request(error):
    """Handle 400 Bad Request"""
    app.logger.warning("Bad Request: %s", error)
    return (
        jsonify(
            status=400,
            error="Bad Request",
            message=str(error),
        ),
        HTTP_400_BAD_REQUEST,
    )


@app.errorhandler(HTTP_500_INTERNAL_SERVER_ERROR)
def internal_server_error(error):
    """Handle 500 Internal Server Error"""
    app.logger.error("Server Error: %s", error)
    return (
        jsonify(
            status=500,
            error="Internal Server Error",
            message=str(error),
        ),
        HTTP_500_INTERNAL_SERVER_ERROR,
    )
