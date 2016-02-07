import sys
import subprocess
import string
import zipfile
import csv
from collections import defaultdict
from nltk.corpus import names, gazetteers, wordnet as wn

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

    def __init__(self, corpus=None):
        self.corpus = corpus # path to corpus
        if self.corpus:
            self.clusterdict = {}
            with open('50mpaths2') as clusters:
                for line in clusters:
                    self.clusterdict[line.split()[1]] = line.split()[0]
            self.worddict, self.prevdict, self.nextdict = self.get_dicts()
            self.most_common_words = sorted(self.worddict,
                    key=self.worddict.get, reverse=True)[:100]

        #self.names_set = set(
        #        [name.lower() for name in names.words('male.txt')] +
        #        [name.lower() for name in names.words('female.txt')])
        #self.places_set = set(
        #        #[ca_prov.lower() for ca_prov in gazetteers.words('caprovinces.txt')] +
        #        [country.lower() for country in gazetteers.words('countries.txt')] + 
        #        #[country.lower() for country in gazetteers.words('isocountries.txt')] + 
        #        [city.lower() for city in gazetteers.words('uscities.txt')] + 
        #        #[abbrev.lower() for abbrev in gazetteers.words('usstateabbrev.txt')] + 
        #        [state.lower() for state in gazetteers.words('usstates.txt')])
        self.census_names = self.make_census_list()
        self.geo_cities = self.make_geo_cities_list()

        self.feat_fns = [self.init_caps,
                         self.all_caps,
                         #self.next_init_caps,
                         #self.next_all_caps,
                         #self.prev_init_caps,
                         #self.prev_all_caps,
                         self.prev_word,
                         self.next_word,
                         self.most_common,
                         self.cluster,
                         self.most_common_prev,
                         self.most_common_next,
                         self.starts_sent,
                         self.prev_pos,
                         self.next_pos,
                         #self.name,
                         #self.place,
                         self.char_ngrams,
                         self.census_name,
                         #self.bigram,
                         self.geo_city,
                         self.alpha,
                         self.has_digit, 
                         #self.in_wn
                         ]

    def print_feat_fns(self):
        print '\n'.join([f.__name__ for f in self.feat_fns])

    def make_geo_cities_list(self):
        geo_cities = []
        with zipfile.ZipFile('cities15000.zip') as cities:
            c = cities.open('cities15000.txt')
            for line in c:
                geo_cities.append(line.split('\t')[1].lower())
        return geo_cities

    def make_census_list(self):
        c_names = []
        with open('census_names/app_c.csv') as names:
            reader = csv.reader(names)
            for row in reader:
                c_names.append(row[0].lower())
        return c_names

    def get_dicts(self):
        worddict = defaultdict(int)
        prevdict = defaultdict(lambda : defaultdict(int))
        nextdict = defaultdict(lambda : defaultdict(int))
        with open(self.corpus) as corpus:
            lines = corpus.readlines()
            for i, line in enumerate(lines):
                try:
                    if line.strip() and lines[i-1].strip() and lines[i+1].strip():
                        word = line.split()[0]
                        worddict[word] += 1
                        prev = lines[i-1].split()[0]
                        prevdict[word][prev] += 1
                        next = lines[i+1].split()[0]
                        nextdict[word][next] += 1
                except IndexError:
                    continue
        return worddict, prevdict, nextdict

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
    # All features functions have to take word, prev, next, prevpos, 
    # and nextpos as parameters to comply with the features method

    def init_caps(self, word, prev=None, next=None,
            prevpos=None, nextpos=None):
        return ("INITCAPS" if word[0].isupper() and word[1:].islower()
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
                    and next[1:].islower() else None)
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
                    and prev[1:].islower() else None)
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

    def alpha(self, word, prev=None, next=None,
            prevpos=None, nextpos=None):
        if word.isalpha():
            return "ALPHA"

    def has_digit(self, word, prev=None, next=None,
            prevpos=None, nextpos=None):
        return "HASDIGIT" if any(char.isdigit() for char in word) else None

    def most_common(self, word, prev=None, next=None, 
            prevpos=None, nextpos=None):
        return "MOSTCOMMON" if word in self.most_common_words else None

    def suffix(self, word, prev=None, next=None,
            prevpos=None, nextpos=None):
        return "SUFFIX={}".format(word[-3:])

    def cluster(self, word, prev=None, next=None,
            prevpos=None, nextpos=None):
        try:
            return "CLUSTER={}".format(self.clusterdict[word])
        except KeyError:
            return None

    def most_common_prev(self, word, prev=None, next=None,
            prevpos=None, nextpos=None):
        try:
            return "MCPREV={}".format(sorted(self.prevdict[word].items(),
                key=lambda x: x[1], reverse=True)[0][0])
        except IndexError, KeyError:
            return None

    def most_common_next(self, word, prev=None, next=None, 
            prevpos=None, nextpos=None):
        try:
            return "MCNEXT={}".format(sorted(self.nextdict[word].items(),
                key=lambda x: x[1], reverse=True)[0][0])
        except IndexError, KeyError:
            return None

    def starts_sent(self, word, prev=None, next=None,
            prevpos=None, nextpos=None):
        return ("STARTSSENT" if not prev or prev in '?!.' or not prev.strip() 
                else None)

    def name(self, word, prev=None, next=None,
            prevpos=None, nextpos=None):
        return "NAME" if word.lower() in self.names_set else None

    def place(self, word, prev=None, next=None,
            prevpos=None, nextpos=None):
        return "PLACE" if word.lower() in self.places_set else None

    def prev_pos(self, word, prev=None, next=None,
            prevpos=None, nextpos=None):
        return "PREVPOS={}".format(prevpos) if prevpos is not None else None

    def next_pos(self, word, prev=None, next=None,
            prevpos=None, nextpos=None):
        return "NEXTPOS={}".format(nextpos) if nextpos is not None else None

    def char_ngrams(self, word, prev=None, next=None,
            prevpos=None, nextpos=None):
        ngrams = [['char-'+str(n)+'-gram='+word[i:i+n]
                  for i in range(len(word)-n+1)] for n in range(1,7)]
        ngrams_flat = [ng for sublist in ngrams for ng in sublist]
        return ' '.join(ngrams_flat)

    def bigram(self, word, prev=None, next=None,
            prevpos=None, nextpos=None):
        if prev:
            return "BIGRAM={}".format(' '.join([prev, word]))
        else:
            return None

    def geo_city(self, word, prev=None, next=None,
            prevpos=None, nextpos=None):
        if word.lower() in self.geo_cities:
            return "GEOCITY"
        if next:
            bigram = ' '.join([word.lower(), next.lower()])
            if bigram in self.geo_cities:
                return "GEOCITY"

    def census_name(self, word, prev=None, next=None,
            prevpos=None, nextpos=None):
        if word.lower() in self.census_names:
            return "CENSUS"

    def starts_with_symbol(self, word, prev=None, next=None,
            prevpos=None, nextpos=None):
        if word.startswith(('#', '@')):
            return "STARTSYMBOL"

    def in_wn(self, word, prev=None, next=None,
            prevpos=None, nextpos=None):
        if wn.synsets(word):
            return "INWN"

    def features(self, word, prev, next, prevpos, nextpos):
        """Get the list of feature strings for `word`"""
        feat_strings = [feat_fn(word, prev, next, prevpos, nextpos)
                        for feat_fn in self.feat_fns]
        return [feat for feat in feat_strings if feat is not None]

    def write_mallet_input(self, output_file):
        with open(self.corpus) as corpus, open(output_file, 'w+') as out:
            # reads the whole corpus into memory unfortunately
            lines = corpus.readlines()
            for i, line in enumerate(lines):
                if line.strip():
                    word, pos, label = line.split()
                    try:
                        prev = lines[i-1].split()[0]
                        prevpos = lines[i-1].split()[1]
                    except IndexError:
                        prev = None
                        prevpos = None
                    try:
                        next = lines[i+1].split()[0]
                        nextpos = lines[i+1].split()[1]
                    except IndexError:
                        next = None
                        nextpos = None
                    out.write('{} {} {} {}\n'.format(
                        word, pos,
                        ' '.join(self.features(word, prev, next, prevpos, nextpos)),
                        label))
                else:
                    out.write('\n')

def main(corpus_file, output_file):
    fe = FeatureExtractor(corpus_file)
    #fe.format_for_pos_tagging('train.formatted')
    #subprocess.call('./pos-tag.sh train.formatted', shell=True)
    #fe.reformat_for_ner('train.pos', 'train.pos.gold')
    fe.write_mallet_input(output_file)

if __name__ == "__main__":
    if sys.argv[1] == "print_features":
        fe = FeatureExtractor()
        fe.print_feat_fns()
    else:
        main(sys.argv[1], sys.argv[2])
