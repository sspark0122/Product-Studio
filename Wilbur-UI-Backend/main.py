from flask import Flask
from flask import Response
from flask import jsonify
from flask import json
from flask import request
from urlparse import urlparse

# Import each API manager
from google_api_manager import GoogleApiManager
from dropbox_api_manger import DropboxApiManager
from box_api_manager import BoxApiManager

#
# Entry point to the backend.
# Define routes for each storage component we support.
#

# Initialize Flask
app = Flask(__name__)

# ====================== Google Routes ====================== #

# Add a Google account (Drive, Gmail, Vision)
@app.route('/google/add_account', methods=['POST'])
def add_google_account():
    status_code = 200
    status_mesg = 'Success'

    if request.headers['Content-Type'] == 'application/json':
        if 'email' in request.json:
            # Attempt to add an account
            status_code, status_mesg = g_api_manager.add_account(request.json['email'])
        else:
            status_code = 400
            status_mesg = 'Request requires "email" field'
    else:
        status_code = 415
        status_mesg = 'Server only accepts requests with "Content-Type" of "application/json"'

    # Format and return the response
    return Response(status_mesg, status=status_code)

# Remove a Google account (Drive, Gmail, Vision)
@app.route('/google/remove_account', methods=['DELETE'])
def remove_google_account():
    status_code = 200
    status_mesg = 'Success'

    if request.headers['Content-Type'] == 'application/json':
        if 'email' in request.json:
            # Attempt to remove an account
            status_code, status_mesg = g_api_manager.remove_account(request.json['email'])
        else:
            status_code = 400
            status_mesg = 'Request requires "email" field'
    else:
        status_code = 415
        status_mesg = 'Server only accepts requests with "Content-Type" of "application/json"'

    # Format and return the response
    return Response(status_mesg, status=status_code)

# Get files from a Google account (Drive)
@app.route('/google/get_files', methods=['GET'])
def search_google_files():
    status_code = 200
    status_mesg = 'Success'

    email_param = urlparse(request.args.get('email')).path
    keyword_param = urlparse(request.args.get('keyword')).path

    if request.headers['Content-Type'] == 'application/json':
        if email_param and keyword_param:
            # Attempt to search an account for files
            status_code, status_mesg = g_api_manager.search_files(email_param, keyword_param)
        else:
            status_code = 400
            status_mesg = 'Request requires "email" and "keyword" params'
    else:
        status_code = 415
        status_mesg = 'Server only accepts requests with "Content-Type" of "application/json"'

    # Format and return the response
    return Response(status_mesg, status=status_code)

# @TODO
# Get images from a Google account (Vision)
@app.route('/google/get_images', methods=['GET'])
def search_google_images():
    status_code = 200
    status_mesg = 'Success'

    email_param = urlparse(request.args.get('email')).path
    keyword_param = urlparse(request.args.get('keyword')).path

    if request.headers['Content-Type'] == 'application/json':
        if email_param and keyword_param:
            # Attempt to search an account for images
            status_code, status_mesg = g_api_manager.search_images(email_param, keyword_param)
        else:
            status_code = 400
            status_mesg = 'Request requires "email" and "keyword" params'
    else:
        status_code = 415
        status_mesg = 'Server only accepts requests with "Content-Type" of "application/json"'

    # Format and return the response
    return Response(status_mesg, status=status_code)

# Get mail from a Google account (Gmail)
@app.route('/google/get_mail', methods=['GET'])
def search_google_mail():
    status_code = 200
    status_mesg = 'Success'

    email_param = urlparse(request.args.get('email')).path
    keyword_param = urlparse(request.args.get('keyword')).path

    if request.headers['Content-Type'] == 'application/json':
        if email_param and keyword_param:
            # Attempt to search an account for mail
            status_code, status_mesg = g_api_manager.search_mail(email_param, keyword_param)
        else:
            status_code = 400
            status_mesg = 'Request requires "email" and "keyword" params'
    else:
        status_code = 415
        status_mesg = 'Server only accepts requests with "Content-Type" of "application/json"'

    # Format and return the response
    return Response(status_mesg, status=status_code)


# =========================================================== #

# ======================== Box Routes ======================= #

# @TODO
# Add a Box account
@app.route('/box/add_account', methods=['POST'])
def add_box_account():
    status_code = 501
    status_mesg = 'Adding Box account not implemented at this time'

    # Format and return the response
    return Response(status_mesg, status=status_code)

# @TODO
# Remove a Box account
@app.route('/box/remove_account', methods=['DELETE'])
def remove_box_account():
    status_code = 501
    status_mesg = 'Removing Box account not implemented at this time'

    # Format and return the response
    return Response(status_mesg, status=status_code)

# Get files from a Box account
@app.route('/box/get_files', methods=['GET'])
def search_box_files():
    status_code = 200
    status_mesg = 'Success'

    keyword_param = request.args.get('keyword')

    if request.headers['Content-Type'] == 'application/json':
        if keyword_param:
            # Attempt to search an account for dropbox
            status_code, status_mesg = b_api_manager.search_files(keyword_param)
        else:
            status_code = 400
            status_mesg = 'Request requires and "keyword" params'
    else:
        status_code = 415
        status_mesg = 'Server only accepts requests with "Content-Type" of "application/json"'

    # Format and return the response
    return Response(status_mesg, status=status_code)

# =========================================================== #

# ====================== Dropbox Routes ===================== #

# @TODO - Do not hardcode the email account
# Get files from a Dropbox account
@app.route('/dropbox/get_files', methods=['GET'])
def search_dropbox_files():
    status_code = 200
    status_mesg = 'Success'

    keyword_param = request.args.get('keyword')

    if request.headers['Content-Type'] == 'application/json':
        if keyword_param:
            # Attempt to search an account for dropbox
            status_code, status_mesg = db_api_manager.search_files(keyword_param)
        else:
            status_code = 400
            status_mesg = 'Request requires and "keyword" params'
    else:
        status_code = 415
        status_mesg = 'Server only accepts requests with "Content-Type" of "application/json"'

    # Format and return the response
    return Response(status_mesg, status=status_code)

# @TODO - Needs full authentication
# Add a Dropbox account
@app.route('/dropbox/add_account', methods=['POST'])
def add_dropbox_account():
    status_code = 501
    status_mesg = 'Adding Dropbox accounts not implemented at this time'

    # Format and return the response
    return Response(status_mesg, status=status_code)

    # status_code = 200
    # status_mesg = 'Success'

    # if request.headers['Content-Type'] == 'application/json':
    #     if 'email' in request.json:
    #         # Attempt to add an account
    #         status_code, status_mesg = db_api_manager.add_account(request.json['email'])
    #     else:
    #         status_code = 400
    #         status_mesg = 'Request requires "email" field'
    # else:
    #     status_code = 415
    #     status_mesg = 'Server only accepts requests with "Content-Type" of "application/json"'

    # # Format and return the response
    # return Response(status_mesg, status=status_code)

# @TODO
# Remove a Dropbox account
@app.route('/dropbox/remove_account', methods=['DELETE'])
def remove_dropbox_account():
    status_code = 501
    status_mesg = 'Removing Dropbox account not implemented at this time'

    # Format and return the response
    return Response(status_mesg, status=status_code)


# @TODO - Needs full authentication
# Get token for a Dropbox account
@app.route('/dropbox/set_token', methods=['GET'])
def set_token():
    status_code = 501
    status_mesg = 'Setting Dropbox token not implemented at this time'

    # Format and return the response
    return Response(status_mesg, status=status_code)

    # status_code = 200
    # status_mesg = 'Success'

    # access_token = request.args.get('code')

    # if access_token:
    #     # Attempt to save an access token
    #     status_code, status_mesg = db_api_manager.set_token(access_token)
    # else:
    #     status_code = 400
    #     status_mesg = 'Request requires "code"'

    # # Format and return the response
    # return Response(status_mesg, status=status_code)

# =========================================================== #

if __name__ == '__main__':
    # Initiate the managers
    g_api_manager = GoogleApiManager()
    db_api_manager = DropboxApiManager()
    b_api_manager = BoxApiManager()

    # Initiate the Flask server on localhost:5000
    app.run(debug=True)
