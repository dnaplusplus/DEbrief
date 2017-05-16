'''
DEbrief (c) University of Manchester 2017

DEbrief is licensed under the MIT License.

To view a copy of this license, visit <http://opensource.org/licenses/MIT/>.

@author:  neilswainston
'''
import json
import os
import re
import tempfile
import urllib
import uuid

from Bio import SeqIO
from flask import Flask, Response, send_from_directory
from synbiochem.utils import seq_utils

from debrief_db import DEBriefDBClient


# Configuration:
DEBUG = True
SECRET_KEY = str(uuid.uuid4())

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
    sheet_id = '1-dcR5dPaYwtH38HNYqBieOSaqMz-31N8aEdEb3IqRkw'
    client = DEBriefDBClient(sheet_id, project_id, 'A:R')
    result = {'pdb': {'id': client.get_pdb_id()},
              'mutations': client.get_mutations().values()}

    return Response(json.dumps(result, indent=3, sort_keys=True),
                    mimetype='application/json')


@APP.route('/fasta/<project_id>')
def get_fasta(project_id):
    '''Gets a fasta file from a project id.'''
    sheet_id = '1-dcR5dPaYwtH38HNYqBieOSaqMz-31N8aEdEb3IqRkw'
    client = DEBriefDBClient(sheet_id, project_id, 'A:R')
    sequences = client.get_sequences()

    with open(seq_utils.write_fasta(sequences)) as fle:
        result = fle.read()

    response = Response(result, mimetype='application/text')
    response.headers['Content-Disposition'] = \
        'attachment; filename=%s.fasta' % project_id
    return response


@APP.route('/md-worklist/<project_id>')
def get_md_worklist(project_id):
    '''Gets a molecular dynamics worklist from a project id.'''
    sheet_id = '1-dcR5dPaYwtH38HNYqBieOSaqMz-31N8aEdEb3IqRkw'
    client = DEBriefDBClient(sheet_id, project_id, 'A:R')

    resp = '\n'.join(client.get_md_worklist())

    response = Response(resp, mimetype='application/text')
    response.headers['Content-Disposition'] = \
        'attachment; filename=%s_worklist.txt' % project_id
    return response
