#!/bin/sh

#Usage: bash pipeline.sh <test_directory> <"Comment about features used">

mkdir -p "$1"

echo "Running extract_features"
python extract_features.py train.gold.tpos train.gold.feats
python extract_features.py dev.gold.tpos dev.gold.feats
python extract_features.py print_features > "$1/README.md"

./mallet-tag.sh --train true --model-file train.model train.gold.feats 
./mallet-tag.sh --model-file train.model dev.gold.feats > output.txt

python evaluate-ner.py dev.gold.tpos output.txt >> "$1"/README.md
python evaluate.py dev.gold.tpos output.txt >> "$1"/README.md 
echo "\n$2" >> "$1"/README.md

mv train.gold.feats dev.gold.feats train.model output.txt ./"$1"
head -n 40 "$1"/README.md
