import io

from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
from apiclient.http import MediaIoBaseDownload
import webbrowser
import json

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/drive', 'https://www.googleapis.com/auth/gmail.readonly']
GOOGLE_DRIVE = 'googledrive'
GMAIL = 'gmail'
IMAGE_SEARCH = 'image-search'
TEXT_DETECT = 'text-detection'
ALL = 'all'

class GoogleApiManager:

    def __init__(self, size=10):
        self.size = size
        self.drive_service = None
        self.gmail_service = None
        self.user_keyword = None
        self.platform = None
        
        
    def init_connection(self):
        store = file.Storage('token.json')
        creds = store.get()
        if not creds or creds.invalid:
            flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
            creds = tools.run_flow(flow, store)
            
        # Connect to Google Drive
        self.drive_service = build('drive', 'v3', http=creds.authorize(Http()))
        
        # Connect to Gmail
        self.gmail_service = build('gmail', 'v1', http=creds.authorize(Http()))

    def search(self, platform, user_keyword):
        self.results = {GOOGLE_DRIVE: [], GMAIL: []}
        self.platform = platform.lower()

        if user_keyword == '*':
            self.user_keyword = ''
        else:
            self.user_keyword = user_keyword.lower()
    
        if  self.platform == GOOGLE_DRIVE:
            # Search on Google Drive with a keyword
            self.get_files()

        elif  self.platform == GMAIL:
            # Search on Gmail with a keyword
            self.get_emails()

        elif  self.platform == IMAGE_SEARCH:
            # Search images on Google Drive with a self.keyword()
            self.search_images()

        elif self.platform == TEXT_DETECT:
            # Detect text in image
            self.parse_text_detection_result(self.detect_text())

        elif self.platform == ALL:
            self.get_files()
            self.get_emails()
        else:
            print('Please enter search query in [word] for [platform].')

        # Convert Dictionary to JSON object
        return json.dumps(self.results)
                
    def get_files(self):
        page_token = None
        
        while True:
            response = self.drive_service.files().list(q="name contains '{0}' or fullText contains '{0}'".format(self.user_keyword),
                                                  spaces='drive',
                                                  fields='nextPageToken, files(id, name, thumbnailLink, webViewLink)',
                                                  pageToken=page_token).execute()
                                                  
            print('\n[Files from Google Drive]')
            if response['files'] != []:
                for file in response.get('files', []):
                    print(file.get('name') + ' (' + file.get('id') + ')' + ' (' + file.get('webViewLink') + ')')
                    self.results[GOOGLE_DRIVE].append({
                        'name': file.get('name'), 
                        'id': file.get('id'), 
                        'thumbnailLink': file.get('thumbnailLink'),
                        'webViewLink': file.get('webViewLink')})
                page_token = response.get('nextPageToken', None)
                if page_token is None:
                    break
                
            else:
                print('File not found')
                break

    def get_emails(self):
        try: 
            # Get list contains Message IDs
            response = self.gmail_service.users().messages().list(userId='me', q=self.user_keyword).execute()
            
            # Check the response is empty
            print('\n[Emails from Gmail]')
            if response['resultSizeEstimate'] != 0:
                
                # Parse Message IDs into list
                msgIDs = []
                for k in response['messages']:
                    msgIDs.append(k['id'])
    
                # Return message with given Message ID
                for msgID in msgIDs:
                    message = self.gmail_service.users().messages().get(userId='me', id=msgID).execute()
                    header = []
                    email_subject = ''
                    email_from = ''
                    email_to = ''

                    for content in message.get('payload').get('headers'):
                        if content.get('name') == 'Subject':
                            header.insert(0, 'Subject: ' + content.get('value'))
                            email_subject = content.get('value')
                        if content.get('name') == 'From':
                            header.insert(1, 'From: ' + content.get('value'))
                            email_from = content.get('value')
                        if content.get('name') == 'To':
                            header.insert(2, 'To: ' + content.get('value'))
                            email_to = content.get('value')
                    
                    for elem in header:
                        print(elem)
                    print('Message: ' + message['snippet'] + '\n')
                    self.results[GMAIL].append({
                        'Subject': email_subject,
                        'From': email_from,
                        'To': email_to,
                        'Message': message['snippet']})

            else:
                print("Email not found")
                
        except errors.HttpError as error:
            print ('An error occurred: ' + (error))

    # Retrieve all images from the google drive.
    def get_images(self):
        page_token = None
        image_list = []
        while True:
            response = self.drive_service.files().list(q="mimeType contains 'image/'",
                                                  spaces='drive',
                                                  fields='nextPageToken, files(id, name, thumbnailLink, webViewLink)',
                                                  pageToken=page_token).execute()       
            if response['files'] != []:
                for file in response.get('files', []):
                    image_list.append(file)
                page_token = response.get('nextPageToken', None)
                if page_token is None:
                    break
            else:
                print('Image not found')
                break

        return image_list

    # Detects broad sets of categories within an image.
    def search_images(self):
        from google.cloud import vision
        from google.oauth2 import service_account

        # Retrieve all images.
        image_list = self.get_images()

        credentials = service_account.Credentials.from_service_account_file("vision_api_credentials.json")
        client = vision.ImageAnnotatorClient(credentials=credentials)
        image = vision.types.Image()

        images = []
        for img in image_list:
            # Retrieve original image uri from thumbnailLink
            thumbnailLink = img['thumbnailLink']
            originImgUri = thumbnailLink.split('=')
            image.source.image_uri = originImgUri[0]

            response = client.label_detection(image=image)
            labels = response.label_annotations

            for label in labels:
                if self.user_keyword == label.description:
                    images.append(img)

        print('\n[Search Images in Google Drive]')
        if images != []:
            for image in images:
                webbrowser.open(image['webViewLink'], new=2)
                self.results[GOOGLE_DRIVE].append({
                        'name': image['name'], 
                        'id': image['id'], 
                        'thumbnailLink': image['thumbnailLink'],
                        'webViewLink': image['webViewLink']})
        else:
            print('Image not found')

    # Detects dense document text in an image (Optical Character Recognition).
    def detect_text(self):
        from google.cloud import vision
        from google.oauth2 import service_account

        # Retrieve all images.
        image_list = self.get_images()

        credentials = service_account.Credentials.from_service_account_file("vision_api_credentials.json")
        client = vision.ImageAnnotatorClient(credentials=credentials)
        image = vision.types.Image()
        
        images = []
        for img in image_list:
            # Retrieve original image uri from thumbnailLink
            thumbnailLink = img['thumbnailLink']
            originImgUri = thumbnailLink.split('=')
            image.source.image_uri = originImgUri[0]

            response = client.text_detection(image=image)
            texts = response.text_annotations

            if self.is_empty(texts) == False:
                text = texts[0].description.lower()
                if self.user_keyword in text:
                    images.append(img)

            # for text in texts:
            #     # print('\n'+text.description)
            #     if self.user_keyword in text.description.lower():
            #         images.append(img)
            #         return images

        return images

    def parse_text_detection_result(self, images):
        print('\n[Detect Texts in Images on Google Drive]')
        if images != []:
            for image in images:
                webbrowser.open(image['webViewLink'], new=2)
                self.results[GOOGLE_DRIVE].append({
                        'name': image['name'], 
                        'id': image['id'], 
                        'thumbnailLink': image['thumbnailLink'],
                        'webViewLink': image['webViewLink']})
        else:
            print('Image not found')

    # Check if the argument is empty
    def is_empty(self, any_structure):
        if any_structure:
            return False
        else:
            return True