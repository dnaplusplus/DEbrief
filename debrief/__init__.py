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
from flask import Flask, send_from_directory
from synbiochem.utils import seq_utils


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


@APP.route('/pdb_viewer')
def pdb_viewer():
    '''Renders pdb_viewer.'''
    return APP.send_static_file('pdb_viewer.html')


@APP.route('/result/<result_id>')
def get_result(result_id):
    '''Gets result from id.'''
    entry = result_id
    result = {}
    result['id'] = result_id
    _get_uniprot_data(entry, result)

    print json.dumps(result, indent=2)

    return json.dumps(result)


def _get_uniprot_data(entry, res):
    '''Gets Uniprot data (sequence and secondary structure).'''
    fields = ['sequence', 'database(PDB)', 'feature(BETA STRAND)',
              'feature(HELIX)', 'feature(TURN)']
    uniprot_data = seq_utils.get_uniprot_values([entry], fields)
    res.update(uniprot_data[entry])

    res['Cross-reference (PDB)'] = [
        _get_pdb_data(pdb_id)
        for pdb_id in res['Cross-reference (PDB)'].split(';')
        if len(pdb_id) > 0]

    res['Beta strand'] = _get_secondary_data(res['Beta strand'])
    res['Helix'] = _get_secondary_data(res['Helix'])
    res['Turn'] = _get_secondary_data(res['Turn'])


def _get_pdb_data(pdb_id):
    '''Returns PDB sequence data.'''
    url = 'http://www.rcsb.org/pdb/download/downloadFile.do' + \
        '?fileFormat=FASTA&compression=NO&structureId=' + \
        pdb_id

    temp_file = tempfile.NamedTemporaryFile()
    urllib.urlretrieve(url, temp_file.name)
    fasta_seqs = SeqIO.parse(open(temp_file.name), 'fasta')

    return {'id': pdb_id, 'chains': {fasta.id[len(pdb_id) + 1:len(pdb_id) + 2]:
                                     str(fasta.seq)
                                     for fasta in fasta_seqs}}


def _get_secondary_data(strng):
    '''Gets secondary structure data.'''
    if len(strng) > 0:
        fields = ['start', 'end', 'pdb']
        return [dict(zip(fields, _parse_secondary_struct(s)))
                for s in strng.split('.; ')]
    return []


def _parse_secondary_struct(strng):
    '''Parses secondary structure string.'''
    regex = r' (\d*) (\d*).*PDB:(\w*)'
    terms = re.findall(regex, strng)[0]
    return int(terms[0]), int(terms[1]), terms[2]
