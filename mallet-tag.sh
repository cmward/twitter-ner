#!/bin/sh
export CLASSPATH=$MALLET_HOME/class:$MALLET_HOME/dist/mallet-deps.jar
java -mx1000m cc.mallet.fst.SimpleTagger "$@"
