'''
DEbrief (c) University of Manchester 2015

DEbrief is licensed under the MIT License.

To view a copy of this license, visit <http://opensource.org/licenses/MIT/>.

@author:  neilswainston
'''
import random

from matplotlib import pyplot
from scipy.cluster.hierarchy import dendrogram, linkage
from synbiochem.utils import seq_utils


def _get_sequence_data(num, length):
    '''Gets random sequence data.'''
    data = []
    labels = []

    parent_seq = seq_utils.get_random_aa(length)

    for _ in range(num):
        seq = _mutate(parent_seq)
        val = 0.1 + (random.random() * 0.8)
        data.append(seq_utils.get_aa_props(seq)[0] + [val])
        labels.append(seq + ',' + '{0:.2f}'.format(val))

    return data, labels


def _mutate(seq, max_mutations=3):
    '''Mutates a given sequence.'''
    seq_lst = list(seq)

    for _ in range(random.randint(0, max_mutations)):
        seq_lst[random.randint(0, len(seq_lst) - 1)] = \
            random.choice(seq_utils.AA_PROPS.keys())

    return ''.join(seq_lst)


def _cluster(data):
    '''Generate the linkage matrix.'''
    return linkage(data, 'ward')


def _plot_dendrogram(data, clusters, labels=None):
    '''Calculate full dendrogram.'''
    # pyplot.figure()
    # pyplot.title('Hierarchical Clustering Dendrogram')
    # pyplot.xlabel('Distance')
    # pyplot.ylabel('Sequence / activity')
    # ddg = dendrogram(clusters, labels=labels, orientation='right',
    # truncate_mode='lastp', p=10
    #                )
    # pyplot.show()

    fig = pyplot.figure()
    ax1 = fig.add_axes([0.1, 0.1, 0.1, 0.8])
    ddg = dendrogram(
        clusters,
        labels=labels,
        leaf_font_size=6,
        leaf_rotation=90,
        orientation='right')
    ax1.set_xticks([])
    # ax1.set_yticks([])

    # Plot distance matrix.
    axmatrix = fig.add_axes([0.58, 0.1, 0.02, 0.8])
    activities = [[data[i][-1]] for i in ddg['leaves']]
    mat = axmatrix.matshow(
        activities,
        aspect='auto',
        origin='lower',
        cmap='hot')
    axmatrix.set_xticks([])
    axmatrix.set_yticks([])

    # Plot colorbar.
    axcolor = fig.add_axes([0.62, 0.1, 0.02, 0.8])
    pyplot.colorbar(mat, cax=axcolor)
    fig.show()
    fig.savefig('dendrogram.png')


def main():
    '''main method.'''
    data, labels = _get_sequence_data(20, 20)
    clusters = _cluster(data)
    _plot_dendrogram(data, clusters, labels)

if __name__ == '__main__':
    main()
