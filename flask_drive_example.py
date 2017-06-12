'''
Flask Drive Example App

@author Prahlad Yeri <prahladyeri@yahoo.com>
@date 30-12-2016
Dependency:
1. pip install flask google-api-python-client
2. make sure you have client_id.json in this same directory.
'''
import os
import uuid
from apiclient import discovery
from oauth2client import client
from oauth2client.file import Storage
import flask
import httplib2


APP = flask.Flask(__name__)


@APP.route('/')
def index():
    '''Index method.'''
    credentials = get_credentials()

    if not credentials:
        return flask.redirect(flask.url_for('oauth2callback'))
    elif credentials.access_token_expired:
        return flask.redirect(flask.url_for('oauth2callback'))

    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    url = ('https://sheets.googleapis.com/$discovery/rest?version=v4')
    service = discovery.build(
        'sheets', 'v4', http=http, discoveryServiceUrl=url)

    sheet_id = '1-dcR5dPaYwtH38HNYqBieOSaqMz-31N8aEdEb3IqRkw'
    result = service.spreadsheets().values().get(
        spreadsheetId=sheet_id, range='KSI' + '!' + 'A:R').execute()

    strng = ''

    for res in result.get('values', []):
        strng += str(res)

    return strng


@APP.route('/oauth2callback')
def oauth2callback():
    '''Callback method.'''
    flow = client.flow_from_clientsecrets(
        'client_id.json',
        scope='https://www.googleapis.com/auth/drive',
        redirect_uri=flask.url_for('oauth2callback', _external=True))

    flow.params['include_granted_scopes'] = 'true'

    if 'code' not in flask.request.args:
        auth_uri = flow.step1_get_authorize_url()
        return flask.redirect(auth_uri)
    else:
        auth_code = flask.request.args.get('code')
        credentials = flow.step2_exchange(auth_code)

    # write access token to credentials.json locally
    open('credentials.json', 'w').write(credentials.to_json())
    return flask.redirect(flask.url_for('index'))


def get_credentials():
    '''Gets credentials.'''
    store = Storage('credentials.json')
    credentials = store.get()

    if not credentials or credentials.invalid:
        return None

    return credentials


if __name__ == '__main__':
    if not os.path.exists('client_id.json'):
        print 'Client secrets file (client_id.json) not found in the app path.'
        exit()

    APP.secret_key = str(uuid.uuid4())
    APP.run(debug=True)
