#!/bin/sh
STANFORD_HOME="/Users/chris/bin/stanford-corenlp-full-2015-12-09"
java -cp "$STANFORD_HOME/*" -Xmx2g edu.stanford.nlp.tagger.maxent.MaxentTagger -model $STANFORD_HOME/stanford-corenlp-3.6.0-models/edu/stanford/nlp/models/pos-tagger/english-left3words/english-left3words-distsim.tagger -textFile "$@" > pos-output.txt -tokenize false
