# Main function modified from: https://developers.google.com/sheets/api/quickstart/python

from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

import Constants as c
from Member import Member

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# THE ID and specified range to access our Google Sheet data.
SPOTIFY_SPREADSHEET_ID = '1kcdbFgniYEnsaoiGPkRPmQIR3hitxA7YbbYIR3DJg0M'
SPREADSHEET_RANGE = 'D4:H8'

'''
 Sets up credentials to open the spreadsheet
 and initializes it to be used.
'''


def main():
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.

    if os.path.exists('Credentials/token.pickle'):
        with open('Credentials/token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'Credentials/credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('Credentials/token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('sheets', 'v4', credentials=creds)

    # Call the Sheets API
    sheet = service.spreadsheets()

    return sheet


# Reads data from the spreadsheet's
# specified range to import to the
# Python function.
def read_sheet():
    # Initialize spreadsheet.
    sheet = main()

    # Read the results from the spreadsheet.
    result = sheet.values().get(spreadsheetId=SPOTIFY_SPREADSHEET_ID,
                                range=SPREADSHEET_RANGE).execute()

    # Parse the results.
    values = result.get('values', [])

    return values


# Writes data from the Python function
# to the specified spreadsheet range.
def write_sheet(data):
    # Initialize spreadsheet.
    sheet = main()

    # Writes the inputted data to
    # the online spreadsheet.
    sheet.values().update(
        spreadsheetId=SPOTIFY_SPREADSHEET_ID,
        valueInputOption='RAW',
        range=SPREADSHEET_RANGE,
        body=dict(
            majorDimension='ROWS',
            values=data)
    ).execute()


# This function reads data from the Google Sheets document,
# and compiles the information into Member objects.
# It returns the list of members, and the count of members
# that have a debt.
def read_members(data):
    # Initialize variables.
    member_list = []
    debtor_count = 0

    # Loop through each row of the data.
    for row in data:
        # name - row 0
        # months owed - row 1
        # months prepaid - row 3
        name = row[0]
        debt = (float(row[1]) - float(row[3])) * c.MONTHLY_COST

        # Increment debtor_count for any
        # debtor who owes money.
        if debt > 0:
            debtor_count += 1

        # Check that the Google Sheet member corresponds
        # to a recognized member in our program.
        name_in_list = c.NAMES.count(name) == 1

        # If the member is recognized,
        # we add them to the member list.
        if name_in_list:
            name_list_index = c.NAMES.index(name)
            user_id = c.USER_IDS[name_list_index]
            member_list.append(Member(name, debt, user_id))

    return member_list, debtor_count


if __name__ == '__main__':
    write_sheet(8)
