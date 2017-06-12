'''
DEbrief (c) University of Manchester 2017

DEbrief is licensed under the MIT License.

To view a copy of this license, visit <http://opensource.org/licenses/MIT/>.

@author:  neilswainston
'''
from collections import defaultdict
from operator import itemgetter
import re


class DEBriefDBClient(object):
    '''Client class for DBBrief-DB.'''

    def __init__(self, values):
        self.__values = values

    def get_pdb_id(self):
        '''Get pdb id.'''
        for row in self.__values[2:]:
            if len(row[3]):
                return row[2]

        return None

    def get_activity(self, name):
        '''Get activity data.'''
        for row in self.__values[2:]:
            if row[4] == name:
                return row[6] == 'TRUE'

        raise ValueError(name)

    def get_mutations(self):
        '''Get mutation data.'''
        mutations = defaultdict(dict)

        for row in self.__values[2:]:
            if len(row[4]):
                mutations[row[4]]['name'] = row[4]
                mutations[row[4]]['positions'] = _parse_mutation(row[4])
                mutations[row[4]]['active'] = row[6] == 'TRUE'

        return mutations

    def get_sequences(self):
        '''Get sequence data.'''
        sequences = {}
        name_prefix = ''
        templ_seq = ''

        for row in self.__values[2:]:
            if len(row[3]) and row[3] == 'TRUE' and len(row[15]):
                name_prefix = row[0]
                templ_seq = row[15]
                break

        for mutation in self.get_mutations().values():
            sequences[(name_prefix + mutation['name']).replace(' ', '') +
                      '|' + name_prefix + '|' + mutation['name']] = \
                _apply_mutations(templ_seq, mutation['positions'])

        return sequences

    def get_md_worklist(self):
        '''Get molecular dynamics worklist.'''
        return sorted(list(set([row[4] for row in self.__values[2:]
                                if len(row) < 17])),
                      key=itemgetter(0))


def _parse_mutation(mut_str):
    '''Parse mutation string.'''
    return [(mut[0], int(mut[1]), mut[2])
            for mut in [re.compile(r'(\d*)').split(mutation)
                        for mutation in mut_str.split()]]


def _apply_mutations(seq, mutations):
    '''Applies mutations to sequence.'''
    seq = list(seq)

    for mutation in mutations:
        if mutation[0] != seq[mutation[1] - 1]:
            raise ValueError('Invalid mutation at position %d.' +
                             'Amino acid is %s but mutation is of %s.') \
                % mutation[1], seq[mutation[1] - 1], mutation[0]

        seq[mutation[1] - 1] = mutation[2]

    return ''.join(seq)
