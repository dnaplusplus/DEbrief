'''
DEbrief (c) University of Manchester 2017

DEbrief is licensed under the MIT License.

To view a copy of this license, visit <http://opensource.org/licenses/MIT/>.

@author:  neilswainston
'''
import StringIO
import json
import os
import re
import tempfile
import urllib
import uuid

from Bio import Seq, SeqIO, SeqRecord
from apiclient import discovery
from flask import Flask, Response, redirect, send_from_directory, url_for
from oauth2client import client
from oauth2client.file import Storage
import httplib2

from debrief_db import DEBriefDBClient


# Create application:
_STATIC_FOLDER = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                              '../static')
APP = Flask(__name__, static_folder=_STATIC_FOLDER)
APP.config.from_object(__name__)


@APP.route('/')
def home():
    '''Renders homepage.'''
    return APP.send_static_file('index.html')


@APP.route('/data/<project_id>')
def get_data(project_id):
    '''Gets a pdb id and mutations from a project id.'''
    debrief = _get_debrief(project_id)
    result = {'pdb': {'id': debrief.get_pdb_id()},
              'mutations': debrief.get_mutations().values()}

    return Response(json.dumps(result, indent=3, sort_keys=True),
                    mimetype='application/json')


@APP.route('/fasta/<project_id>')
def get_fasta(project_id):
    '''Gets a fasta file from a project id.'''
    debrief = _get_debrief(project_id)
    records = [SeqRecord.SeqRecord(Seq.Seq(seq), id=seq_id, name='',
                                   description='')
               for seq_id, seq in debrief.get_sequences().iteritems()]

    result = StringIO.StringIO()
    SeqIO.write(records, result, 'fasta')

    response = Response(result.getvalue(), mimetype='application/text')
    response.headers['Content-Disposition'] = \
        'attachment; filename=%s.fasta' % project_id
    return response


@APP.route('/md-worklist/<project_id>')
def get_md_worklist(project_id):
    '''Gets a molecular dynamics worklist from a project id.'''
    debrief = _get_debrief(project_id)
    resp = '\n'.join(debrief.get_md_worklist())

    response = Response(resp, mimetype='application/text')
    response.headers['Content-Disposition'] = \
        'attachment; filename=%s_worklist.txt' % project_id
    return response


def _get_debrief(project_id):
    '''Gets values.'''
    values = _get_service().spreadsheets().values().get(
        spreadsheetId='1-dcR5dPaYwtH38HNYqBieOSaqMz-31N8aEdEb3IqRkw',
        range=project_id + '!' + 'A:R').execute()

    return DEBriefDBClient(values.get('values', []))


def _get_service():
    '''Gets service.'''
    credentials = _get_credentials()

    if not credentials:
        return redirect(url_for('oauth2callback'))
    elif credentials.access_token_expired:
        return redirect(url_for('oauth2callback'))

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
