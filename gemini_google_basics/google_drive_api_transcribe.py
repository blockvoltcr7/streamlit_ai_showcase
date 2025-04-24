import os.path
import sys
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
CREDENTIALS_FILE = 'credentials.json' # Downloaded from Google Cloud Console
TOKEN_FILE = 'token.json'

def authenticate():
    """Handles OAuth 2.0 authentication for the Google Drive API."""
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception as e:
                print(f"Error refreshing token: {e}")
                print(f"Deleting {TOKEN_FILE} and re-authenticating.")
                os.remove(TOKEN_FILE)
                creds = None # Force re-authentication
        if not creds: # Need to authenticate
             if not os.path.exists(CREDENTIALS_FILE):
                 print(f"Error: Credentials file '{CREDENTIALS_FILE}' not found.")
                 print("Please download it from Google Cloud Console and place it in the script directory.")
                 sys.exit(1)
             flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIALS_FILE, SCOPES)
             # Run local server flow opens browser for user authorization
             creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())

    return creds

def list_files_in_folder(service, folder_id):
    """Lists files within a specific Google Drive folder."""
    files_list = []
    page_token = None
    try:
        while True:
            # Call the Drive v3 API
            # Query excludes folders ('mimeType != ...') and includes only files directly in the specified folder ('<folder_id>' in parents)
            # 'trashed=false' ensures we don't list deleted files.
            results = service.files().list(
                q=f"'{folder_id}' in parents and mimeType != 'application/vnd.google-apps.folder' and trashed=false",
                spaces='drive',
                fields='nextPageToken, files(id, name)',
                pageToken=page_token
            ).execute()

            items = results.get('files', [])
            if not items:
                print('No files found in this folder.')
                break
            else:
                files_list.extend(items)

            page_token = results.get('nextPageToken', None)
            if page_token is None:
                break # Exit loop if no more pages
    except HttpError as error:
        print(f'An API error occurred: {error}')
        return None
    except Exception as e:
        print(f'An unexpected error occurred: {e}')
        return None

    return files_list

if __name__ == '__main__':
    target_folder_id = input("1XdYXUh-HEnM9isRpAsPCFZhGeVnMTZ2H")
    if not target_folder_id:
        print("Folder ID cannot be empty.")
        sys.exit(1)

    print("Authenticating...")
    creds = authenticate()

    if not creds:
        print("Authentication failed. Exiting.")
        sys.exit(1)

    try:
        print("Building Drive service...")
        service = build('drive', 'v3', credentials=creds)

        print(f"Fetching files for folder ID: {target_folder_id}...")
        files = list_files_in_folder(service, target_folder_id)

        if files is not None:
            print("\n--- Files in Folder ---")
            if files:
                 for file_item in files:
                    print(f"Name: {file_item.get('name')}, ID: {file_item.get('id')}")
            else:
                 print("(No files found)") # Already printed inside function, but good to confirm here
            print("-----------------------")

    except Exception as e:
        print(f"An error occurred while building the service or listing files: {e}")
