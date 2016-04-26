'''
synbiochem (c) University of Manchester 2015

synbiochem is licensed under the MIT License.

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
    entry = 'P46882'
    result = {}
    result['id'] = result_id
    result['uniprot_entry'] = entry
    _get_uniprot_data(entry, result)
    return json.dumps(result)


def _get_uniprot_data(entry, result):
    '''Gets Uniprot data (sequence and secondary structure).'''
    fields = ['sequence', 'feature(BETA%20STRAND)', 'feature(HELIX)',
              'feature(TURN)']
    uniprot_data = sequence_utils.get_uniprot_values([entry], fields)
    result.update(uniprot_data['entry'])

if __name__ == '__main__':
    _APP.run(threaded=True)
