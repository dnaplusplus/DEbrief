'''
DEbrief (c) University of Manchester 2015

DEbrief is licensed under the MIT License.

To view a copy of this license, visit <http://opensource.org/licenses/MIT/>.

@author:  neilswainston
'''
from matplotlib import pyplot
from scipy.cluster.hierarchy import dendrogram, linkage
import random

from mpl_toolkits.mplot3d import Axes3D
from synbiochem.utils import sequence_utils


def _get_sequence_data(num, length):
    '''Gets random sequence data.'''
    data = []
    labels = []

    for _ in range(num):
        seq = sequence_utils.get_random_aa(length)
        val = 0.1 + (random.random() * 0.8)
        data.append(sequence_utils.get_aa_props(seq)[0] + [val])
        labels.append(seq + ',' + '{0:.2f}'.format(val))

    return data, labels


def _plot_data(data):
    '''Plots data.'''
    fig = pyplot.figure()
    plt_axes = fig.add_subplot(111, projection='3d')
    plt_axes.scatter([datum[0] for datum in data],
                     [datum[1] for datum in data],
                     [datum[2] for datum in data],
                     zdir='z', c='red')
    pyplot.show()


def _cluster(data):
    '''Generate the linkage matrix.'''
    return linkage(data, 'ward')


def _plot_dendrogram(clusters, labels=None):
    '''Calculate full dendrogram.'''
    pyplot.figure()
    pyplot.title('Hierarchical Clustering Dendrogram')
    pyplot.xlabel('sample index')
    pyplot.ylabel('distance')
    dendrogram(clusters,
               leaf_font_size=8.0,  # font size for the x axis labels
               labels=labels,
               )
    pyplot.show()


def main():
    '''main method.'''
    data, labels = _get_sequence_data(100, 2)
    _plot_data(data)
    clusters = _cluster(data)
    _plot_dendrogram(clusters, labels)

if __name__ == '__main__':
    main()
