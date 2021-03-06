import Bio.SeqIO as sio
from Bio.Alphabet import IUPAC
from Bio import motifs

import numpy as np
import re
import os

L = {'A': 0,
     'a': 0,
     'C': 1,
     'c': 1,
     'G': 2,
     'g': 2,
     'T': 3,
     't': 3
     }


def _getOneHotSeq(seq):
    """Convert Biopython Seq to one-hot encoding.

    .. note:: Only internally used.
    """

    m = len(seq.alphabet.letters)
    n = len(seq)
    result = np.zeros((1,1, m, n), dtype=np.float32)
    for i in range(len(seq)):
        result[0, 0, L[seq[i]], i] = 1
    return result

def readSeqsFromFasta(filename):
    """Read sequences from multi-fasta file.

    Parameters
    -----------
    filename : str
        File containing DNA sequences in multi-fasta format.

    returns : list
        List of Biopython Seq objects.
    """

    seqs = []
    for faseq in sio.parse(open(filename), 'fasta', IUPAC.unambiguous_dna):
        match = re.search(r'N', str(faseq.seq), re.I)
        if match:
            print("skip sequence containing N")
            continue
        seqs.append(faseq)
    return seqs

def splitTrainingTest(filename, train_test_ratio, num_top_regions = None,\
        randomize =True):
    """Splits training and test set.

    The DNA sequences are read from filename.
    As output, two additional
    fasta files are generated 
    with prefixes being same as filename and suffixes
    *train.fa* and *test.fa*.
    
    Parameters
    -----------
    filename : str
        File containing DNA sequences in multi-fasta format.

    train_test_ratio : float
        Ratio between 0 and 1 for splitting the dataset into
        training and test. For instance, train_test_ratio=0.1 
        uses 10% and 90% of the dataset for test and training, respectively.
    num_top_regions : int
        Use only the first num_top_regions from 
        the fasta-file. Default: (None) all sequences are used.
    randomize : bool
        Randomize the dataset. Default: True.
    """

    seqs = readSeqsFromFasta(filename)

    # only extract the top N regions
    if num_top_regions:
        seqs = seqs[:num_top_regions]

    if randomize:
        idx_permut = list(np.random.permutation(len(seqs)))
    else:
        idx_permut = list(range(len(seqs)))

    itest = idx_permut[:int(len(seqs)*train_test_ratio)]
    itrain = idx_permut[int(len(seqs)*train_test_ratio):]
    trfilename = ".".join(filename.split(".")[:-1]) + "_train.fa"
    tefilename = ".".join(filename.split(".")[:-1]) + "_test.fa"
    trseq = [seqs[i] for i in itrain]
    teseq = [seqs[i] for i in itest]
    sio.write(trseq, trfilename, "fasta")
    sio.write(teseq, tefilename, "fasta")


def seqToOneHot(seqs):
    """Converts a set of Biopython DNA sequences to *one-hot* encoding.

    Parameters
    -----------
    seqs :list
        List of Biopython Sequence objects.

    returns : numpy-array
        4D Numpy array representing the 
        sequences in *one-hot* encoding.
    """

    onehots = []
    for seq in seqs:
        onehots.append(_getOneHotSeq(seq.seq))
    return np.concatenate(onehots, axis=0)


def load_sample():
    """
    Load sample sequences of Oct4 ChIP-seq peaks from H1hesc cell
    of ENCODE.
    The sequences are converted to one-hot encoding.

    Parameters
    -----------
    returns : numpy-array
        Sample DNA sequences in *one-hot* encoding.
    """
    
    
    fafile = os.path.join(os.path.dirname(__file__), 'data', 'oct4.fa')
    seqs = readSeqsFromFasta(fafile)
    onehot = seqToOneHot(seqs)

    return onehot
