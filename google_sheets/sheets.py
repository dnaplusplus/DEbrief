'''
DEbrief (c) University of Manchester 2017

DEbrief is licensed under the MIT License.

To view a copy of this license, visit <http://opensource.org/licenses/MIT/>.

@author:  neilswainston
'''
# pylint: disable=no-member
import os
import re
from apiclient import discovery
from oauth2client import client, tools
from oauth2client.file import Storage
import httplib2

SCOPES = 'https://www.googleapis.com/auth/spreadsheets.readonly'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'DEBrief'


def read_sheet(sheet_id, tab, sheet_range):
    '''Reads a Google Sheet.'''
    service = _get_service()

    result = service.spreadsheets().values().get(
        spreadsheetId=sheet_id, range=tab + '!' + sheet_range).execute()

    return result.get('values', [])


def _get_service():
    '''Gets service.'''
    credentials = _get_credentials()
    http = credentials.authorize(httplib2.Http())
    url = ('https://sheets.googleapis.com/$discovery/rest?version=v4')
    return discovery.build('sheets', 'v4', http=http, discoveryServiceUrl=url)


def _get_credentials():
    '''Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    '''
    credential_dir = os.path.join(os.path.expanduser('~'), '.credentials')

    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)

    path = os.path.join(credential_dir,
                        'sheets.googleapis.com-python-quickstart.json')

    store = Storage(path)
    credentials = store.get()

    if not credentials or credentials.invalid:
        directory = os.path.dirname(os.path.realpath(__file__))
        secret_file = os.path.join(directory, CLIENT_SECRET_FILE)
        flow = client.flow_from_clientsecrets(secret_file, SCOPES)
        flow.user_agent = APPLICATION_NAME
        credentials = tools.run_flow(flow, store, None)

    return credentials


def main():
    '''Shows basic usage of the Sheets API.

    Creates a Sheets API service object and prints the names and majors of
    students in a sample spreadsheet:
    https://docs.google_sheets.com/spreadsheets/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms/edit
    '''
    sheet_id = '1-dcR5dPaYwtH38HNYqBieOSaqMz-31N8aEdEb3IqRkw'
    tab = 'MAO-N'
    sheet_range = 'A:O'

    values = read_sheet(sheet_id, tab, sheet_range)

    for row in values[1:]:
        if len(row[2]):
            seq = row[14]

        mutations = [re.compile(r'(\d*)').split(mutation)
                     for mutation in row[3].split()]

        for mutation in mutations:
            if mutation[0] != seq[int(mutation[1]) - 1]:
                print mutation[0] + '\t' + mutation[1] + '\t' + \
                    seq[int(mutation[1]) - 1]


if __name__ == '__main__':
    main()
