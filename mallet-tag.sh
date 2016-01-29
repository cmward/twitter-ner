#!/bin/sh
MALLET_HOME=~/bin/mallet-2.0.8RC3
export CLASSPATH=$MALLET_HOME/class:$MALLET_HOME/dist/mallet-deps.jar
java -mx1000m cc.mallet.fst.SimpleTagger "$@"
