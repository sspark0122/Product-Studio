from boxsdk import OAuth2, Client
from boxsdk import JWTAuth
import json
import webbrowser

# Access Token is only valid for 60 mins
ACCESS_TOKEN = 'cmKK2UnhKlkj9ovwG8c9Y5OACJktp3qE'
CLIENT_SECRET = 'UN84SXcZteBGblTnkoM2ehlWu0TGIScQ'
CLIENT_ID = 'oxk0gwt6ge0ieult8h07jhiq9vzs7r9g'
FILE_URL = 'https://app.box.com/file/'
LIMIT = 10
OFFSET = 0
REDIRECT_URI = 'https://localhost:5000'

class BoxApiManager:

    # @TODO - Add oAuth2 authentication
    # Seach Box account for files
    def search_files(self, keyword):
        status_code = 200
        status_mesg = ''
        results = []

        auth = OAuth2(
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            access_token=ACCESS_TOKEN,
        )

        # Authorize the client
        client = Client(auth)

        # Get the user
        user = client.user().get()

        # Search the query
        search_results = client.search().query(
            keyword,
            limit=LIMIT,
            offset=OFFSET
            )

        for item in search_results:
            item_with_name = item.get(fields=['name'])
            fileUrl = FILE_URL + item_with_name.id
            results.append({
                'name': item_with_name.name,
                'id': item_with_name.id,
                'url': fileUrl})

        # Format JSON response
        # @TODO - Account should not be hardcoded
        message = {"account": "conorc273", "storage": "Box", "data": results}
        status_mesg = json.dumps(message)

        return status_code, status_mesg


############### Authorization funcs below ###############

    # def get_box_files2(self):

    #   with open('config.json') as file:
    #       data = json.load(file)
    #       clientID = data['boxAppSettings']['clientID']
    #       clientSecret = data['boxAppSettings']['clientSecret']
    #       publicKeyID = data['boxAppSettings']['appAuth']['publicKeyID']
    #       privateKey = data['boxAppSettings']['appAuth']['privateKey']
    #       passphrase = data['boxAppSettings']['appAuth']['passphrase']
    #       enterpriseID = data['enterpriseID']

    #       print('clientID: ' + data['boxAppSettings']['clientID'])
    #       print('clientSecret: ' + data['boxAppSettings']['clientSecret'])
    #       print('publicKeyID: ' + data['boxAppSettings']['appAuth']['publicKeyID'])
    #       print('privateKey: ' + data['boxAppSettings']['appAuth']['privateKey'])
    #       print('passphrase: ' + data['boxAppSettings']['appAuth']['passphrase'])
    #       print('enterpriseID: ' + data['enterpriseID'])


    #   # Configure JWT auth object
    #   sdk = JWTAuth(
    #     client_id=clientID,
    #     client_secret=clientSecret,
    #     enterprise_id=enterpriseID,
    #     jwt_key_id=publicKeyID,
    #     rsa_private_key_file_sys_path=privateKey,
    #     rsa_private_key_passphrase=passphrase
    #   )

    #   # Get auth client
    #   client = Client(sdk)

        # PERFORM API ACTIONS WITH CLIENT

    # def store_tokens(access_token, refresh_token):
    #   at = access_token
    #   rt = refresh_token
    #   print('access_token: ' + at + ', ' + 'refresh_token: ' + rt)

    # def get_box_files2(self):
    #   oauth = OAuth2(
 #          client_id=CLIENT_ID,
 #          client_secret=CLIENT_SECRET)

    #   csrf_token = ''
    #   auth_url, csrf_token = oauth.get_authorization_url(REDIRECT_URI)
    #   print('auth_url: ' + auth_url)
    #   print('csrf_token: ' + csrf_token)

    #   webbrowser.open(auth_url, new=2)

    # # Fetch access token and make authenticated request
    # @app.route('/return')
    # def capture():
    #   # Capture auth code and csrf token via state
    #   code = request.args.get('code')
    #   state = request.args.get('state')

    #   # If csrf token matches, fetch tokens
    #   assert state == csrf_token
    #   access_token, refresh_token = oauth.authenticate(code)

    #   print('access_token: ' + access_token)

############################################################
