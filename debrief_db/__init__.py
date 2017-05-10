'''
DEbrief (c) University of Manchester 2017

DEbrief is licensed under the MIT License.

To view a copy of this license, visit <http://opensource.org/licenses/MIT/>.

@author:  neilswainston
'''
import re
import sys

from google_sheets import sheets


class DEBriefDBClient(object):
    '''Client class for DBBrief-DB.'''

    def __init__(self, sheet_id, tab, sheet_range):
        self.__values = sheets.read_sheet(sheet_id, tab, sheet_range)

    def get_pdb(self):
        '''Get pdb data.'''
        for row in self.__values[1:]:
            if len(row[3]):
                return row[2]

        return None

    def get_mutations(self):
        '''Get mutation data.'''
        mutations = {}

        for row in self.__values[1:]:
            mutations[row[4]] = _parse_mutation(row[4])

        return mutations


def _parse_mutation(mut_str):
    '''Parse mutation string.'''
    return [(mut[0], int(mut[1]), mut[2])
            for mut in [re.compile(r'(\d*)').split(mutation)
                        for mutation in mut_str.split()]]


def main(args):
    '''main methods.'''
    client = DEBriefDBClient(args[0], args[1], args[2])
    print client.get_mutations()


if __name__ == '__main__':
    main(sys.argv[1:])
