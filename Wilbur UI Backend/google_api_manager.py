import os
import json
import base64
import webbrowser
from httplib2 import Http
from apiclient import errors
from oauth2client import file, client, tools
from googleapiclient.discovery import build

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/drive', 'https://www.googleapis.com/auth/gmail.readonly']
GMAIL_LIMIT = 20


class GoogleApiManager:

    # Initialize the manager.
    def __init__(self, size=10):
        self.size = size
        self.g_accounts = []
        self.drive_accs = {}
        self.gmail_accs = {}

    # Add a Google account.
    # On success, returns 200, <response>
    # On error, returns: <error code>, <error message>
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
        email_account = email[:email.find('@')]

        print('Adding account {} to Google').format(email_account)

        # Store token by account name
        # @TODO - Use multistore_file.
        store = file.Storage('token_' + email_account + '.json')
        try:
            creds = store.get()
        except:
            print('Token for account {} does not exist').format(email_account)

        # If we do not have a token, request one
        if not creds or creds.invalid:
            try:
                print('Retrieving token for account {}').format(email_account)
                flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
                flow.params['user_id'] = email
                creds = tools.run_flow(flow, store)
                print('Token for account {} written to {}').format(email_account, 'token_' + email_account + '.json')
            except errors.HttpError, error:
                print('An error occurred retrieving a token for account {}: {}').format(email_account, error)
                status_mesg = error
                status_code = 500
                return status_code, status_mesg

        # Connect to Google Drive
        try:
            self.drive_accs[email_account] = build('drive', 'v3', http=creds.authorize(Http()))
            print('Account {} is connected to Google Drive').format(email_account)
        except errors.HttpError, error:
            print('An error occurred connecting account {} to Google Drive: {}').format(email_account, error)
            status_mesg = error
            status_code = 500
            return status_code, status_mesg

        # Connect to Gmail
        try:
            self.gmail_accs[email_account] = build('gmail', 'v1', http=creds.authorize(Http()))
            print('Account {} is connected to Gmail').format(email_account)
        except errors.HttpError, error:
            print('An error occurred connecting account {} to Gmail: {}').format(email_account, error)
            status_mesg = error
            status_code = 500
            return status_code, status_mesg

        # Store account
        self.g_accounts.append(email_account)

        # Format JSON response
        message = {"account": email_account, "storage": "Google", "message": "Successfully linked Google account."}
        status_mesg = json.dumps(message)

        return status_code, status_mesg

    # Remove a Google account (delete the token file).
    # On success, returns 200, <response>
    # On error, returns <error code>, <error message>
    def remove_account(self, email):
        status_code = 200
        status_mesg = ''

        # Trivial email validation
        if '@' not in email:
            status_code = 422
            status_mesg = 'Email account is not a valid format'
            print('ERROR: ' + status_mesg)
            return status_code, status_mesg

        # Get account name
        email_account = email[:email.find('@')]

        # Get token file
        token_file = 'token_' + email_account + '.json'

        # Check if we already store the account
        if email_account not in self.g_accounts:
            status_code = 409
            status_mesg = 'Email account is not saved and cannot be removed'
            print('ERROR: ' + status_mesg)
            return status_code, status_mesg

        # Remove the token file
        if os.path.isfile(token_file):
            print('Removing token for account {}').format(email_account)
            os.remove(token_file)
        else:
            status_code = 409
            status_mesg = 'Email account is not saved and cannot be removed'
            print('ERROR: ' + status_mesg)

        # Remove account storage info
        self.g_accounts.remove(email_account)
        del self.gmail_accs[email_account]
        del self.drive_accs[email_account]

        # Format JSON response
        message = {"account": email_account, "storage": "Google", "message": "Successfully unlinked Google account."}
        status_mesg = json.dumps(message)

        return status_code, status_mesg

    # Search Google Drive account for the given keyword.
    # On success, returns: 200, <response>
    # On error, returns: <error code>, <error message>
    def search_files(self, email, keyword):
        page_token = None
        status_code = 200
        status_mesg = ''
        results = []

        # Initialize the query
        query = "name contains '{0}' or fullText contains '{0}'".format(keyword)

        # Trivial email validation
        if '@' not in email:
            status_code = 422
            status_mesg = 'Email account is not a valid format'
            print('ERROR: ' + status_mesg)
            return status_code, status_mesg

        # Get account name
        email_account = email[:email.find('@')]

        # Check if we already store the account
        if email_account not in self.g_accounts:
            status_code = 409
            status_mesg = 'Email account is not saved and cannot be searched'
            print('ERROR: ' + status_mesg)
            return status_code, status_mesg

        drive_service = self.drive_accs[email_account]

        # Iterate and return all the file results
        while True:
            try:
                # @TODO - Add max results limit
                response = drive_service.files().list(
                    spaces='drive',
                    fields='nextPageToken, files(id, name, thumbnailLink, webViewLink)',
                    pageToken=page_token,
                    q=query).execute()

                # Grab the results
                if response['files']:
                    results.extend(response['files'])
                    page_token = response.get('nextPageToken', None)
                else:
                    print('Drive files not found for account {}').format(email_account)
                    break

                # Check if there is more to search
                if page_token is None:
                    break

            except errors.HttpError, error:
                print('An error occurred searching Google Drive for account {}: {}').format(email_account, error)
                status_mesg = error
                status_code = 500
                return status_code, status_mesg

        # Format JSON response
        message = {"account": email_account, "storage": "Google", "platform": "Drive", "data": results}
        status_mesg = json.dumps(message)

        return status_code, status_mesg

    # Searches emails in a Google Drive account for the given keyword.
    # On success, returns: 200, <response>
    # On error, returns: <error code>, <error message>
    def search_mail(self, email, keyword):
        status_code = 200
        status_mesg = ''
        results = []
        page_token = None

        # Initialize the query
        query = keyword

        # Trivial email validation
        if '@' not in email:
            status_code = 422
            status_mesg = 'Email account is not a valid format'
            print('ERROR: ' + status_mesg)
            return status_code, status_mesg

        # Get account name
        email_account = email[:email.find('@')]

        # Check if we already store the account
        if email_account not in self.g_accounts:
            status_code = 409
            status_mesg = 'Email account is not saved and cannot be searched'
            print('ERROR: ' + status_mesg)
            return status_code, status_mesg

        gmail_service = self.gmail_accs[email_account]

        # Iterate and return Gmail results
        while True:
            try:
                # Get list of Message ID's
                response = gmail_service.users().messages().list(
                    userId='me',
                    pageToken=page_token,
                    q=query,
                    maxResults=GMAIL_LIMIT).execute()

                # Check if response is empty
                if response['messages']:

                    # Parse Message ID's into a list
                    msg_IDs = []
                    for resp_ids in response['messages']:
                        msg_IDs.append(resp_ids['id'])

                    # Get message for each given Message ID
                    for msgID in msg_IDs:
                        message = gmail_service.users().messages().get(
                            userId='me',
                            id=msgID).execute()

                        # Get header info
                        header = {}
                        for content in message.get('payload').get('headers'):
                            if content.get('name') == 'Subject':
                                header['subject'] = content.get('value')
                            if content.get('name') == 'From':
                                header['from'] = content.get('value')
                            if content.get('name') == 'To':
                                header['to'] = content.get('value')

                        # Get snippet
                        snippet = message.get('snippet')

                        # Get HTML body
                        body = message.get('payload').get('body').get('data')
                        if body:
                            body = base64.urlsafe_b64decode(body.encode('ASCII'))

                        results.append({"header": header, "snippet": snippet, "body": body})

                else:
                    print('Emails not found for account {}').format(email_account)
                    break

                # Check if there is more to search
                if page_token is None:
                    break

            except errors.HttpError, error:
                print('An error occurred searching Gmail for account {}: {}').format(email_account, error)
                status_mesg = error
                status_code = 500
                return status_code, status_mesg

        # Format JSON response
        message = {"account": email_account, "storage": "Google", "platform": "Gmail", "data": results}
        status_mesg = json.dumps(message)

        return status_code, status_mesg

############### Image processing funcs below ###############

    # # Retrieve all images from the google drive.
    # def get_images(self):
    #     page_token = None
    #     image_list = []
    #     while True:
    #         response = self.drive_service.files().list(q="mimeType contains 'image/'",
    #                                               spaces='drive',
    #                                               fields='nextPageToken, files(id, name, thumbnailLink, webViewLink)',
    #                                               pageToken=page_token).execute()
    #         if response['files'] != []:
    #             for file in response.get('files', []):
    #                 image_list.append(file)
    #             page_token = response.get('nextPageToken', None)
    #             if page_token is None:
    #                 break

    #         else:
    #             print('Image not found')
    #             break

    #     print('\n[Images from Google Drive]')
    #     image_result = self.analyze_images(image_list)
    #     if image_result != []:
    #         print(image_result)
    #         for image in image_result:
    #             webbrowser.open(image['webViewLink'], new=2)
    #             self.results[GOOGLE_DRIVE].append({
    #                     'name': image['name'],
    #                     'id': image['id'],
    #                     'thumbnailLink': image['thumbnailLink'],
    #                     'webViewLink': image['webViewLink']})
    #     else:
    #         print('Image not found')

    #     # print('\ndetect_document_uri')
    #     # self.detect_document(image_list)

    # # Detects broad sets of categories within an image.
    # def analyze_images(self, image_list):
    #     from google.cloud import vision
    #     from google.oauth2 import service_account

    #     credentials = service_account.Credentials.from_service_account_file("vision_api_credentials.json")
    #     client = vision.ImageAnnotatorClient(credentials=credentials)
    #     image = vision.types.Image()

    #     result = []
    #     for img in image_list:
    #         # Retrieve original image uri from thumbnailLink
    #         thumbnailLink = img['thumbnailLink']
    #         originImgUri = thumbnailLink.split('=')
    #         image.source.image_uri = originImgUri[0]

    #         response = client.label_detection(image=image)
    #         labels = response.label_annotations

    #         for label in labels:
    #             if self.user_keyword == label.description:
    #                 result.append(img)

    #     return result

    # # Detects dense document text in an image (Optical Character Recognition).
    # def detect_document(self, image_list):
    #     from google.cloud import vision

    #     client = vision.ImageAnnotatorClient()
    #     image = vision.types.Image()
    #     result = []

    #     for img in image_list:
    #         # Retrieve original image uri from thumbnailLink
    #         thumbnailLink = img['thumbnailLink']
    #         originImgUri = thumbnailLink.split('=')
    #         image.source.image_uri = originImgUri[0]

    #         response = client.document_text_detection(image=image)
    #         for page in response.full_text_annotation.pages:
    #             for block in page.blocks:
    #                 print('\nBlock confidence: {}\n'.format(block.confidence))

    #                 for paragraph in block.paragraphs:
    #                     print('Paragraph confidence: {}'.format(
    #                         paragraph.confidence))

    #                     for word in paragraph.words:
    #                         word_text = ''.join([
    #                             symbol.text for symbol in word.symbols
    #                         ])
    #                         print('Word text: {} (confidence: {})'.format(
    #                             word_text, word.confidence))

    #                         for symbol in word.symbols:
    #                             print('\tSymbol: {} (confidence: {})'.format(
    #                                 symbol.text, symbol.confidence))

    #     # image.source.image_uri = uri

    #     # response = client.document_text_detection(image=image)

    #     # for page in response.full_text_annotation.pages:
    #     #     for block in page.blocks:
    #     #         print('\nBlock confidence: {}\n'.format(block.confidence))

    #     #         for paragraph in block.paragraphs:
    #     #             print('Paragraph confidence: {}'.format(
    #     #                 paragraph.confidence))

    #     #             for word in paragraph.words:
    #     #                 word_text = ''.join([
    #     #                     symbol.text for symbol in word.symbols
    #     #                 ])
    #     #                 print('Word text: {} (confidence: {})'.format(
    #     #                     word_text, word.confidence))

    #     #                 for symbol in word.symbols:
    #     #                     print('\tSymbol: {} (confidence: {})'.format(
    #     #                         symbol.text, symbol.confidence))

    #     # def get_allFiles(self, num_files):
    #     # results = self.drive_service.files().list(
    #     #     pageSize=num_files, fields="nextPageToken, files(id, name)").execute()
    #     # items = results.get('files', [])

    #     # if not items:
    #     #     print('No files found.')
    #     # else:
    #     #     print('[Files from Google Drive]')
    #     #     for item in items:
    #     #         print(item['name'] + ' (' + item['id'] + ')')

############################################################
