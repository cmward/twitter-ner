#!/bin/sh
java -cp "$STANFORD_HOME/*" -Xmx2g edu.stanford.nlp.tagger.maxent.MaxentTagger -model $STANFORD_HOME/stanford-corenlp-3.6.0-models/edu/stanford/nlp/models/pos-tagger/gate-EN-twitter.model -textFile "$@" > "$@".tpos -tokenize false -outputFormat tsv -sentenceDelimeter newline
