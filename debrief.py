'''
DEbrief (c) University of Manchester 2015

DEbrief is licensed under the MIT License.

To view a copy of this license, visit <http://opensource.org/licenses/MIT/>.

@author:  neilswainston
'''
import json
import uuid
from flask import Flask, render_template
from synbiochem.utils import sequence_utils

# Configuration:
DEBUG = True
SECRET_KEY = str(uuid.uuid4())

# Create application:
_APP = Flask(__name__)
_APP.config.from_object(__name__)


@_APP.route('/')
def home():
    '''Renders homepage.'''
    return render_template('index.html')


@_APP.route('/result/<result_id>')
def get_result(result_id):
    '''Gets result from id.'''
    entry = result_id
    result = {}
    result['id'] = result_id
    _get_uniprot_data(entry, result)
    return json.dumps(result)


def _get_uniprot_data(entry, res):
    '''Gets Uniprot data (sequence and secondary structure).'''
    fields = ['sequence', 'database(PDB)', 'feature(BETA STRAND)',
              'feature(HELIX)', 'feature(TURN)']
    uniprot_data = sequence_utils.get_uniprot_values([entry], fields)
    res.update(uniprot_data[entry])
    res['Cross-reference (PDB)'] = res['Cross-reference (PDB)'].split(';')
    res['Beta strand'] = res['Beta strand'].split('.; ')
    res['Helix'] = res['Helix'].split('.; ')
    res['Turn'] = res['Turn'].split('.; ')

if __name__ == '__main__':
    _APP.run(threaded=True)
