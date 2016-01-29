import sys
import subprocess
from collections import defaultdict

""" Read in twitter data and extract features for each word. 
Data files have one word per line.

Usage:
    python extract_features.py <path/to/corpus> <path/to/output>

"""

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
        self.worddict = self.get_word_counts()
        self.most_common_words = sorted(self.worddict,
                key=self.worddict.get, reverse=True)[:100]
        with open('clusters.txt') as clusters:
            self.clusters = clusters.readlines()
        self.clusterdict = {}
        for c in self.clusters:
            self.clusterdict[c.split()[1]] = c.split()[0]
    
    def get_word_counts(self):
        worddict = defaultdict(int)
        with open(self.corpus) as corpus:
            for line in corpus:
                if line.strip() is not '':
                    word = line.split()[0]
                    worddict[word] += 1
        return worddict

    def format_for_pos_tagging(self, out_file):
        """Format the data as one tweet per line"""
        with open(self.corpus) as corpus, open(out_file, 'w+') as pos:
            for line in corpus:
                if line.strip() is not '':
                    word, label = line.split()
                    pos.write(word + ' ')
                else:
                    pos.write('\n')

    def reformat_for_ner(self, pos_file, out_file):
        """Put the data back into original format + POS tag feature"""
        # need to open train.gold to reinsert BIO 
        with open(pos_file) as pos, open(self.corpus) as corpus:
            with open(out_file, 'w+') as out:
                for gold_line, tagged_word in zip(corpus, pos):
                    if gold_line.strip() is not '':
                        out.write('{} {} {}\n'.format(gold_line.split()[0],
                            tagged_word.split()[1].strip(), 
                            gold_line.split()[1]))
                    else:
                        out.write('\n')
                
    ### Feature Functions ###
    # All features functions have to take word, prev, and next
    # as parameters to comply with the features method

    def init_caps(self, word, prev=None, next=None,
            prevpos=None, nextpos=None):
        return ("INITCAPS" if word[0].isupper() and not word.isupper()
                else None)

    def all_caps(self, word, prev=None, next=None,
            prevpos=None, nextpos=None):
        return "ALLCAPS" if word.isupper() else None

    def next_all_caps(self, word, prev=None, next=None, 
            prevpos=None, nextpos=None): 
        if next is not None:
            return "NEXTCAPS" if next.isupper() else None
        else:
            return None

    def next_init_caps(self, word, prev=None, next=None,
            prevpos=None, nextpos=None):
        if next is not None:
            return ("NEXTINITCAPS" if next[0].isupper()
                    and not next.isupper() else None)
        else:
            return None

    def prev_all_caps(self, word, prev=None, next=None,
            prevpos=None, nextpos=None):
        if prev is not None:
            return "PREVCAPS" if prev.isupper() else None
        else:
            return None

    def prev_init_caps(self, word, prev=None, next=None,
            prevpos=None, nextpos=None):
        if prev is not None:
            return ("PREVINITCAPS" if prev[0].isupper()
                    and not prev.isupper() else None)
        else:
            return None

    def prev_word(self, word, prev=None, next=None,
            prevpos=None, nextpos=None):
        if prev is not None:
            return "PREVWORD={}".format(prev)
        else:
            return None

    def next_word(self, word, prev=None, next=None,
            prevpos=None, nextpos=None):
        if next is not None:
            return "NEXTWORD={}".format(next)
        else:
            return None

    def most_common(self, word, prev=None, next=None, 
            prevpos=None, nextpos=None):
        return "MOSTCOMMON" if word in self.most_common_words else None

    def suffix(self, word, prev=None, next=None,
            prevpos=None, nextpos=None):
        return "SUFFIX={}".format(word[:-3])

    def cluster(self, word, prev=None, next=None,
            prevpos=None, nextpos=None):
        return "CLUSTER={}".format(self.clusterdict[word])

    def features(self, word, prev, next, prevpos, nextpos):
        """Get the list of feature strings for `word`"""
        feat_fns = [self.init_caps,
                    self.all_caps,
                    self.next_init_caps,
                    self.next_all_caps,
                    self.prev_init_caps,
                    self.prev_all_caps,
                    self.prev_word,
                    self.next_word,
                    self.most_common,
                    self.cluster]
        feat_strings = [feat_fn(word, prev, next, prevpos, nextpos)
                        for feat_fn in feat_fns]
        return [feat for feat in feat_strings if feat is not None]

    def write_mallet_input(self, output_file):
        with open(self.corpus) as corpus, open(output_file, 'w+') as out:
            # reads the whole corpus into memory unfortunately
            lines = [line.strip() for line in corpus.readlines()
                     if line.strip() is not '']
            for i, line in enumerate(lines):
                word, pos, label = line.split()
                if i-1 >= 0:
                    prev = lines[i-1].split()[0]
                    prevpos = lines[i-1].split()[1]
                else: 
                    prev = None
                    prevpos = None
                if i+1 < len(lines):
                    next = lines[i+1].split()[0]
                    nextpos = lines[i+1].split()[1]
                else:
                    next = None
                    nextpos = None
                out.write('{} {} {} {}\n'.format(
                    word, pos,
                    ' '.join(self.features(word, prev, next, prevpos, nextpos)),
                    label))

def main(corpus_file, output_file):
    fe = FeatureExtractor(corpus_file)
    #fe.format_for_pos_tagging(fe.corpus, 'train.formatted')
    #subprocess.call('./pos-tag.sh train.formatted', shell=True)
    #fe.reformat_for_ner('train.pos', 'train.pos.gold')
    fe.write_mallet_input(output_file)

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
