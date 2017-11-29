'''
DEbrief (c) University of Manchester 2017

DEbrief is licensed under the MIT License.

To view a copy of this license, visit <http://opensource.org/licenses/MIT/>.

@author:  neilswainston
'''
import StringIO
from collections import defaultdict
import csv
import math
from operator import itemgetter

from Bio import Seq, SeqIO, SeqRecord
import requests

from synbiochem.utils import mut_utils


_URL = 'https://storage.googleapis.com/debrief'

_COLS = {'ID': 0,
         'NAME': 1,
         'PDB': 3,
         'TEMPLATE': 4,
         'MUTATIONS': 5,
         'SEQ': 7,
         'ACTIVE': 8,
         'BATCH': 17}


class DEBriefDBClient(object):
    '''Client class for DBBrief-DB.'''

    def __init__(self, project_id, values):
        self.__project_id = project_id
        self.__values = values

    def get_pdb_id(self):
        '''Get pdb id.'''
        for row in self.__values[2:]:
            if row[_COLS['TEMPLATE']]:
                return row[_COLS['PDB']]

        return None

    def get_activity(self, mutation):
        '''Get activity data.'''
        for row in self.__values[2:]:
            if row[_COLS['MUTATIONS']] == mutation:
                return row[_COLS['ACTIVE']] == 'TRUE'

        raise ValueError(mutation)

    def get_data(self, seqs=True, b_factors=True, active_site_rmsd=True):
        '''Get data.'''
        muts = defaultdict(dict)
        max_b_factor = -1
        max_active_site_rmsd = -1

        if seqs:
            _, templ_seq = self.__get_template()

        for row in self.__values[2:]:
            if row[_COLS['ID']]:
                mut = row[_COLS['MUTATIONS']]
                muts[mut]['id'] = row[_COLS['ID']]
                muts[mut]['name'] = mut
                muts[mut]['active'] = row[_COLS['ACTIVE']] == 'TRUE'
                muts[mut]['positions'] = mut_utils.parse_mut_str(mut)

                if seqs:
                    muts[mut]['sequence'] = \
                        mut_utils.apply_mutations(templ_seq,
                                                  muts[mut]['positions'])

                if b_factors:
                    try:
                        b_factors = self.__get_b_factors(row[_COLS['ID']])
                        muts[mut]['b_factors'] = _strip_nan(b_factors)
                        max_b_factor = max(max_b_factor, max(b_factors))
                    except requests.HTTPError, err:
                        # Assume b-factor data has not yet been archived
                        print err

                if active_site_rmsd:
                    try:
                        active_site_rmsd = \
                            self.__get_active_site_rmsd(row[_COLS['ID']])
                        muts[mut]['active_site_rmsd'] = \
                            _strip_nan(active_site_rmsd)
                        max_active_site_rmsd = \
                            max(max_active_site_rmsd, max(active_site_rmsd))
                    except requests.HTTPError, err:
                        # Assume active site data has not yet been archived
                        print err

        return muts, max_b_factor, max_active_site_rmsd

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
        name_prefix, _ = self.__get_template()

        muts, _, _ = self.get_data(b_factors=False)

        for mutation in muts.values():
            name = name_prefix + '|' + mutation['name'].replace(' ', '_')
            seqs[mutation['id']] = (name, mutation['sequence'])

        return seqs

    def get_md_worklist(self, batch_num):
        '''Get molecular dynamics worklist.'''
        return sorted([(row[_COLS['ID']], row[_COLS['MUTATIONS']])
                       for row in self.__values[2:]
                       if len(row) > _COLS['ID']
                       and row[_COLS['BATCH']] == str(batch_num)],
                      key=itemgetter(0))

    def __get_template(self):
        '''Get template details.'''
        name_prefix = ''
        templ_seq = ''

        for row in self.__values[2:]:
            if row[_COLS['TEMPLATE']] \
                    and row[_COLS['TEMPLATE']] == 'TRUE' \
                    and row[_COLS['SEQ']]:
                name_prefix = row[_COLS['NAME']]
                templ_seq = row[_COLS['SEQ']]
                break

        return name_prefix, templ_seq

    def __get_b_factors(self, seq_id):
        '''Gets b-factors.'''
        b_factors = []

        url = '%s/%s/b-factors/%s.txt' % (_URL, self.__project_id, seq_id)

        if url:
            resp = requests.get(url)

            if resp.status_code != 200:
                resp.raise_for_status()

            for row in csv.reader(resp.text.splitlines(),
                                  delimiter='\t'):
                b_factors.append(float(row[1]))

        return b_factors

    def __get_active_site_rmsd(self, seq_id):
        '''Gets active_site_rmsd.'''
        active_site_rmsd = []

        url = '%s/%s/active_site/%s.pdb' % (_URL, self.__project_id, seq_id)

        if url:
            resp = requests.get(url)

            if resp.status_code != 200:
                resp.raise_for_status()

            for line in resp.text.splitlines():
                if line.startswith('REMARK'):
                    active_site_rmsd.append(float(line.split()[1]))

        return active_site_rmsd


def _strip_nan(lst):
    '''Strip NaN from iterable.'''
    return [-1 if math.isnan(val) else val for val in lst]
