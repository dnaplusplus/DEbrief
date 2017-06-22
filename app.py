'''
DEbrief (c) University of Manchester 2017

DEbrief is licensed under the MIT License.

To view a copy of this license, visit <http://opensource.org/licenses/MIT/>.

@author:  neilswainston
'''
import json
import sys
import uuid


from apiclient import discovery
from oauth2client import client
from oauth2client.file import Storage
import flask
import httplib2

from debrief.debrief_db import DEBriefDBClient

APP = flask.Flask(__name__)


@APP.route('/')
def index():
    '''Renders homepage.'''
    credentials = _get_credentials()

    if not credentials or credentials.access_token_expired:
        return flask.redirect(flask.url_for('oauth2callback'))

    return APP.send_static_file('index.html')


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


@APP.route('/data/<project_id>')
def get_data(project_id):
    '''Gets a pdb id and mutations from a project id.'''
    debrief = _get_debrief(project_id)
    result = {'pdb': {'id': debrief.get_pdb_id()},
              'mutations': debrief.get_data().values()}

    return flask.Response(json.dumps(result, indent=3, sort_keys=True),
                          mimetype='application/json')


@APP.route('/fasta/<project_id>')
def get_fasta(project_id):
    '''Gets a fasta file from a project id.'''
    debrief = _get_debrief(project_id)
    response = flask.Response(debrief.get_fasta(), mimetype='application/text')
    response.headers['Content-Disposition'] = \
        'attachment; filename=%s.fasta' % project_id
    return response


@APP.route('/md-worklist/<project_id>/<batch_num>')
def get_md_worklist(project_id, batch_num):
    '''Gets a molecular dynamics worklist from a project id and batch num.'''
    debrief = _get_debrief(project_id)

    resp = '\n'.join(['\t'.join(vals)
                      for vals in debrief.get_md_worklist(batch_num)])

    response = flask.Response(resp, mimetype='application/text')
    response.headers['Content-Disposition'] = \
        'attachment; filename=%s_%s_worklist.txt' % (project_id, batch_num)
    return response


@APP.route('/b-factors/<project_id>')
def get_b_factors(project_id):
    '''Gets a molecular dynamics b-factors from a project id.'''
    debrief = _get_debrief(project_id)

    return flask.Response(json.dumps(debrief.get_b_factors(),
                                     indent=3,
                                     sort_keys=True),
                          mimetype='application/json')


def _get_debrief(project_id):
    '''Gets values.'''
    serv = _get_service()
    values = serv.spreadsheets().values().get(
        spreadsheetId='1-dcR5dPaYwtH38HNYqBieOSaqMz-31N8aEdEb3IqRkw',
        range=project_id + '!A:Z').execute()

    return DEBriefDBClient(values.get('values', []))


def _get_service():
    '''Gets service.'''
    credentials = _get_credentials()
    http = credentials.authorize(httplib2.Http())
    url = ('https://sheets.googleapis.com/$discovery/rest?version=v4')
    return discovery.build('sheets', 'v4', http=http, discoveryServiceUrl=url)


def _get_credentials():
    '''Gets credentials.'''
    store = Storage('credentials.json')
    credentials = store.get()

    if not credentials or credentials.invalid:
        return None

    return credentials


def main(argv):
    '''main method.'''
    APP.secret_key = str(uuid.uuid4())

    if len(argv) > 0:
        APP.run(host='0.0.0.0', threaded=True, port=int(argv[0]))
    else:
        APP.run(host='0.0.0.0', threaded=True)


if __name__ == '__main__':
    main(sys.argv[1:])
