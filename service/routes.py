"""
Account Service

This microservice handles the lifecycle of Accounts
"""
# pylint: disable=unused-import
from flask import jsonify, request, make_response, abort, url_for   # noqa; F401
from service.models import Account
from service.common import status  # HTTP Status Codes
from . import app  # Import Flask application


############################################################
# Health Endpoint
############################################################
@app.route("/health")
def health():
    """Health Status"""
    return jsonify(status="OK"), status.HTTP_200_OK


######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """Root URL response"""
    return (
        jsonify(
            name="Account REST API Service",
            version="1.0",
            # paths=url_for("list_accounts", _external=True),
        ),
        status.HTTP_200_OK,
    )


######################################################################
# CREATE A NEW ACCOUNT
######################################################################
@app.route("/accounts", methods=["POST"])
def create_accounts():
    """
    Creates an Account
    This endpoint will create an Account based the data in the body that is posted
    """
    app.logger.info("Request to create an Account")
    check_content_type("application/json")
    account = Account()
    account.deserialize(request.get_json())
    account.create()
    message = account.serialize()
    # Uncomment once get_accounts has been implemented
    # location_url = url_for("get_accounts", account_id=account.id, _external=True)
    location_url = "/"  # Remove once get_accounts has been implemented
    return make_response(
        jsonify(message), status.HTTP_201_CREATED, {"Location": location_url}
    )

######################################################################
# LIST ALL ACCOUNTS
######################################################################

@app.route("/accounts", methods=["GET"])
def list_accounts():
    """This endpoint will return all Accounts"""

    app.logger.info("Request to list all accounts")
    
    # Query all accounts
    accounts = Account.query.all()
    
    # Serialize the list of accounts
    results = [account.serialize() for account in accounts]
    
    app.logger.info(f"Returning {len(results)} accounts")
    
    return jsonify(results), status.HTTP_200_OK


######################################################################
# READ AN ACCOUNT
######################################################################

@app.route("/accounts/<int:account_id>", methods=["GET"])
def get_account(account_id):
    """
    Retrieve a single account
    This endpoint will return an account based on its id
    """
    app.logger.info(f"Request to read an account with id: {account_id}")
    
    # Find the account by ID
    account = Account.query.get(account_id)
    
    # Return 404 if not found
    if not account:
        abort(status.HTTP_404_NOT_FOUND, f"Account with id [{account_id}] not found")
    
    # Return the account as JSON
    return jsonify(account.serialize()), status.HTTP_200_OK


######################################################################
# UPDATE AN EXISTING ACCOUNT
######################################################################

@app.route("/accounts/<int:account_id>", methods=["PUT"])
def update_account(account_id):
    """This will update an account based on data input"""

    app.logger.info(f"Request to update account with id: {account_id}")
    
    # Check for valid JSON
    check_content_type("application/json")
    
    # Find the account
    account = Account.query.get(account_id)
    
    # Return 404 if not found
    if not account:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Account with id [{account_id}] could not be found."
        )
    
    # Update the account
    account.deserialize(request.get_json())
    account.update()
    
    app.logger.info(f"Account with ID [{account_id}] updated")
    
    return jsonify(account.serialize()), status.HTTP_200_OK


######################################################################
# DELETE AN ACCOUNT
######################################################################

@app.route("/accounts/<int:account_id>", methods=["DELETE"])
def delete_account(account_id):
    """This  will delete an Account based on the id specified in the path"""

    app.logger.info(f"Request to delete account with id: {account_id}")
    
    # Find the account
    account = Account.query.get(account_id)
    
    # Delete if it exists
    if account:
        account.delete()
        app.logger.info(f"Account with ID [{account_id}] deleted")
    
    # Return 204 No Content (whether account existed or not)
    return "", status.HTTP_204_NO_CONTENT


######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################


def check_content_type(media_type):
    """Checks that the media type is correct"""
    content_type = request.headers.get("Content-Type")
    if content_type and content_type == media_type:
        return
    app.logger.error("Invalid Content-Type: %s", content_type)
    abort(
        status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        f"Content-Type must be {media_type}",
    )
