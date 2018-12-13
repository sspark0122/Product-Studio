import json
import time
import dropbox
import webbrowser


class DropboxApiManager:

    def __init__(self):
        # Both generated in the Dropbox UI
        self.app_key = '7m7xe0tuaeiy7n9'
        self.token = 'Q_23zYRd1DAAAAAAAAAAH3NOdttsS32ILCW6GytFq1jLfNmOTPKw-80mcxAXmO5h'

    # Request a Dropbox token
    def get_token(self, email):
        status_code = 200
        status_mesg = ''

        redirect_url = 'http://localhost:5000/dropbox/set_token'

        # Direct user to login page to create a token
        # @TODO - Add CSRF validation
        login_url = 'https://www.dropbox.com/1/oauth2/authorize?client_id={}&response_type=token&redirect_uri={}&state={}'.format(self.app_key, redirect_url, '')

        # After login, user will be redirected
        webbrowser.open(login_url)

        # Hack - wait for user to authenticate
        time.sleep(5)

        # Format JSON response
        message = {"account": email, "storage": "Dropbox", "message": "Dropbox token has been requested"}
        status_mesg = json.dumps(message)

        return status_code, status_mesg

    # Add a Dropbox account
    def add_account(self, email):
        status_code = 200
        status_mesg = ''

        # Trivial email validation
        if '@' not in email:
            status_code = 422
            status_mesg = 'Email account is not a valid format'
            print('ERROR: ' + status_mesg)
            return status_code, status_mesg

        # Get account name
        # @TODO - Store account
        email_account = email[:email.find('@')]

        print('Adding account {} to Dropbox').format(email_account)

        # Request a token
        status_code, status_mesg = self.get_token(email)

        return status_code, status_mesg

    # Set the user token
    def set_token(self, access_token):
        status_code = 200
        status_mesg = ''

        # Assign token and values
        self.token = access_token

        print 'Adding token to Dropbox account'

        # Format JSON response
        message = {"storage": "Dropbox", "message": "Dropbox token has been added"}
        status_mesg = json.dumps(message)

        return status_code, status_mesg

    # Get files from Dropbox
    def search_files(self, keyword):
        status_code = 200
        status_mesg = ''
        results = []

        # Instantiate a dropbox object
        dbx = dropbox.Dropbox(self.token)

        # Link the user account
        dbx.users_get_current_account()

        # Search files with keywords
        res = dbx.files_search('', keyword, 0)

        # Parse each match
        for match in res.matches:
            data = match.metadata
            name = data.name

            try:
                link = dbx.files_get_temporary_link(data.path_lower).link
            except dropbox.exceptions.HttpError as err:
                status_code = 500
                status_mesg = 'Error getting temporary link: {}'.format(err)
                print('ERROR: ' + status_mesg)
                return status_code, status_mesg

            results.append({
                'name': name,
                'url': link
                })

        # Format JSON response
        # @TODO - Account should not be hardcoded
        message = {"account": "conorc273", "storage": "Dropbox", "data": results}
        status_mesg = json.dumps(message)

        return status_code, status_mesg
