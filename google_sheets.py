import os
import json
import google.auth
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google.oauth2 import service_account

# If modifying these SCOPES, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# The ID and range of the spreadsheet.
SPREADSHEET_ID = '10WN2qrDoYmacVKM7A_qAXtH6MSK7erpzCSUct5Q3URg'  # Replace with your Google Sheet ID
RANGE_NAME = 'Sheet1!A1'  # Starting range for the data (adjust as needed)

SERVICE_ACCOUNT_FILE = 'token.json'

# Authenticate the user and get the credentials
def authenticate_google_account():
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first time.
    # if os.path.exists('token.json'):
    #     creds, _ = google.auth.load_credentials_from_file('token.json')

    # # If there are no (valid) credentials available, let the user log in.
    # if not creds or not creds.valid:
    #     if creds and creds.expired and creds.refresh_token:
    #         creds.refresh(Request())
    #     else:
    #         flow = InstalledAppFlow.from_client_secrets_file(
    #             'token.json', SCOPES)
    #         creds = flow.run_local_server(port=0)

    #     # Save the credentials for the next run
    #     with open('token.json', 'w') as token:
    #         token.write(creds.to_json())
    credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)


    return build('sheets', 'v4', credentials=credentials)

# Function to write data to the sheet
def write_to_google_sheet(data):
    print("here")
    print(data)
    service = authenticate_google_account()
    # Prepare the data to insert
    values = [data]  # The data to write (list of lists)
    body = {
        'values': values
    }

    # Write the data to the spreadsheet
    service.spreadsheets().values().append(
        spreadsheetId=SPREADSHEET_ID,
        range=RANGE_NAME,
        valueInputOption="RAW",
        body=body
    ).execute()