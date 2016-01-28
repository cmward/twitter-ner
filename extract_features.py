import sys
from collections import defaultdict

""" Read in twitter data and extract features for each word. 
Data files have one word per line.

Usage:
    python extract_features.py <path/to/corpus> <path/to/output>
"""

STANFORD_CLASS_PATH = "stanford-postagger."
JAVA_PATH = 'java'


class FeatureExtractor(object):
    """Extracts features for each word in corpus.

    Mallet input files are produced by reading in the corpus, 
    and creating a list of feature strings, i.e. `INITCAPS`,
    and writing the features to the corresponding lines in the
    created Mallet input file.

    Feature functions return feature string if the feature is
    present in the word, and None otherwise.

    """

    def __init__(self, corpus):
        self.corpus = corpus # path to corpus
        self.worddict = defaultdict(int)
    
    def get_word_counts(self):
        with open(self.corpus) as corpus:
            for line in corpus:
                word = line.split()[0]
                self.worddict[word] += 1

    ### Feature Functions ###
    # All features functions have to take word, prev, and next
    # as parameters to comply with the features method

    def init_caps(self, word, prev=None, next=None):
        return ("INITCAPS" if word[0].isupper() and not word.isupper()
                else None)

    def all_caps(self, word, prev=None, next=None):
        return "ALLCAPS" if word.isupper() else None

    def next_all_caps(self, word, prev=None, next=None):
        if next is not None:
            return "NEXTCAPS" if next.isupper() else None
        else:
            return None

    def next_init_caps(self, word, prev=None, next=None):
        if next is not None:
            return ("NEXTINITCAPS" if next[0].isupper()
                    and not next.isupper() else None)
        else:
            return None
    
    def features(self, word, prev, next):
        """Get the list of feature strings for `word`"""
        feat_fns = [self.init_caps,
                    self.all_caps,
                    self.next_init_caps,
                    self.next_all_caps]
        feat_strings = [feat_fn(word, prev, next) for feat_fn in feat_fns]
        return [feat for feat in feat_strings if feat is not None]

    def write_mallet_input(self, output_file):
        with open(self.corpus) as corpus, open(output_file, 'w+') as out:
            # reads the whole corpus into memory unfortunately
            lines = [line.strip() for line in corpus.readlines()
                     if line.strip() is not '']
            print lines
            for i, line in enumerate(lines):
                word, label = line.split()
                if i-1 >= 0:
                    prev = lines[i-1].split()[0]
                else: 
                    prev = None
                if i+1 < len(lines):
                    next = lines[i+1].split()[0]
                else:
                    next = None
                out.write('{} {} {}\n'.format(
                    word, ' '.join(self.features(word, prev, next)), label))

def main(corpus_file, output_file):
    fe = FeatureExtractor(corpus_file)
    fe.write_mallet_input(output_file)

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
