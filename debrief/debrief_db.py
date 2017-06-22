'''
DEbrief (c) University of Manchester 2017

DEbrief is licensed under the MIT License.

To view a copy of this license, visit <http://opensource.org/licenses/MIT/>.

@author:  neilswainston
'''
from collections import defaultdict
from operator import itemgetter
import StringIO
import csv
import re

from Bio import Seq, SeqIO, SeqRecord
import requests


_COLS = {'NAME': 0,
         'PDB': 2,
         'TEMPLATE': 3,
         'MUTATIONS': 4,
         'ACTIVE': 6,
         'SEQ': 15,
         'BATCH': 17,
         'ID': 18,
         'B_FACTORS': 20}


class DEBriefDBClient(object):
    '''Client class for DBBrief-DB.'''

    def __init__(self, values):
        self.__values = values

    def get_pdb_id(self):
        '''Get pdb id.'''
        for row in self.__values[2:]:
            if len(row[_COLS['TEMPLATE']]):
                return row[_COLS['PDB']]

        return None

    def get_activity(self, mutation):
        '''Get activity data.'''
        for row in self.__values[2:]:
            if row[_COLS['MUTATIONS']] == mutation:
                return row[_COLS['ACTIVE']] == 'TRUE'

        raise ValueError(mutation)

    def get_data(self, seqs=True, b_factors=True):
        '''Get data.'''
        muts = defaultdict(dict)
        max_b_factor = -1

        if seqs:
            _, templ_seq = self._get_template()

        for row in self.__values[2:]:
            if len(row[_COLS['ID']]):
                mut = row[_COLS['MUTATIONS']]
                muts[mut]['id'] = row[_COLS['ID']]
                muts[mut]['name'] = mut.replace(' ', '_')
                muts[mut]['active'] = row[_COLS['ACTIVE']] == 'TRUE'
                muts[mut]['positions'] = _parse_mutation(mut)

                if seqs:
                    muts[mut]['sequence'] = \
                        _apply_mutations(templ_seq, muts[mut]['positions'])

                if b_factors:
                    try:
                        b_factors = _get_b_factors(row[_COLS['B_FACTORS']])
                        muts[mut]['b_factors'] = b_factors
                        max_b_factor = max(max_b_factor, max(b_factors))
                    except requests.HTTPError, err:
                        # Assume b-factor data has not yet been archived
                        print err

        return muts, max_b_factor

    def get_fasta(self):
        '''Gets fasta of sequence data.'''
        records = [SeqRecord.SeqRecord(Seq.Seq(vals[1]),
                                       id=seq_id,
                                       description=vals[0])
                   for seq_id, vals in self.get_sequences().iteritems()]

        records.sort(key=lambda x: int(x.id))

        result = StringIO.StringIO()
        SeqIO.write(records, result, 'fasta')
        return result.getvalue()

    def get_sequences(self):
        '''Get sequence data.'''
        seqs = {}
        name_prefix, _ = self._get_template()

        muts, _ = self.get_data(b_factors=False)

        for mutation in muts.values():
            name = name_prefix + '|' + mutation['name']
            seqs[mutation['id']] = (name, mutation['sequence'])

        return seqs

    def get_md_worklist(self, batch_num):
        '''Get molecular dynamics worklist.'''
        return sorted([(row[_COLS['ID']], row[_COLS['MUTATIONS']])
                       for row in self.__values[2:]
                       if len(row) > _COLS['ID']
                       and row[_COLS['BATCH']] == str(batch_num)],
                      key=itemgetter(0))

    def _get_template(self):
        '''Get template details.'''
        name_prefix = ''
        templ_seq = ''

        for row in self.__values[2:]:
            if len(row[_COLS['TEMPLATE']]) \
                    and row[_COLS['TEMPLATE']] == 'TRUE' \
                    and len(row[_COLS['SEQ']]):
                name_prefix = row[_COLS['NAME']]
                templ_seq = row[_COLS['SEQ']]
                break

        return name_prefix, templ_seq


def _parse_mutation(mut_str):
    '''Parse mutation string.'''
    return [(mut[0], int(mut[1]), mut[2])
            for mut in [re.compile(r'(\d*)').split(mutation)
                        for mutation in mut_str.split()]]


def _apply_mutations(seq, mutations):
    '''Applies mutations to sequence.'''
    seq = list(seq)
    offset = 1

    for mutation in mutations:
        if mutation[0] != seq[mutation[1] - offset]:
            err = 'Invalid mutation at position %d. ' % mutation[1] + \
                'Amino acid is %s ' % seq[mutation[1] - offset] + \
                'but mutation is of %s.' % mutation[0]

            raise ValueError(err)

        if mutation[2] == '-':
            # Deletion:
            del seq[mutation[1] - offset]
            offset += 1
        else:
            # Mutation:
            seq[mutation[1] - offset] = mutation[2]

    return ''.join(seq)


def _get_b_factors(url):
    '''Gets b-factors.'''
    b_factors = []

    if url:
        resp = requests.get(url)

        if resp.status_code is not 200:
            resp.raise_for_status()

        for row in csv.reader(resp.text.splitlines(),
                              delimiter='\t'):
            b_factors.append(float(row[1]))

    return b_factors
