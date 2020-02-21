import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# The ID and range of a sample spreadsheet.
SPREADSHEET_ID = '16A_rdYkhWwQFlRJMx18Gy95HOMu1FNMhuRt_8OHnD00'


# initializes the api client. Required for any operations on the sheet
def get_service():
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                '../credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('sheets', 'v4', credentials=creds)

    return service


# reads the spreadsheet and returns data from a specific location
def get_data(service, location: str):
    # Call the Sheets API
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID,
                                range=location).execute()
    values = result.get('values', [])

    return values


# pushes data to the spreadsheet
def push_data(service, location: str, data: list, user_entered: bool = False):
    sheet = service.spreadsheets()
    body = {"values": data}
    result = sheet.values().update(
        spreadsheetId=SPREADSHEET_ID, range=location,
        valueInputOption="USER_ENTERED" if user_entered else "RAW", body=body
    ).execute()
