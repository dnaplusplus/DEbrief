'''
PathwayGenie (c) University of Manchester 2017

PathwayGenie is licensed under the MIT License.

To view a copy of this license, visit <http://opensource.org/licenses/MIT/>.

@author:  neilswainston
'''
import sys
import uuid

from debrief import APP


def main(argv):
    '''main method.'''
    APP.secret_key = str(uuid.uuid4())

    if len(argv) > 0:
        APP.run(host='0.0.0.0', threaded=True, port=int(argv[0]))
    else:
        APP.run(host='0.0.0.0', threaded=True)


if __name__ == '__main__':
    main(sys.argv[1:])
