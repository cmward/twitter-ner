#!/bin/sh

#Usage: bash pipeline.sh <test_directory> <"Comment about features used">

mkdir -p "$1"

echo "Running extract_features"
python extract_features.py train.gold.tpos train.gold.feats 
python extract_features.py dev.gold.tpos dev.gold.feats 

./mallet-tag.sh --train true --model-file train.model train.gold.feats 

./mallet-tag.sh --model-file train.model dev.gold.feats > output.txt

#echo "$2" > README.md

python evaluate-ner.py dev.gold.tpos output.txt > "$1"/README.md
python evaluate.py dev.gold.tpos output.txt >> "$1"/README.md 

echo "\n$2" >> "$1"/README.md

mv train.gold.feats dev.gold.feats train.model output.txt ./"$1"
