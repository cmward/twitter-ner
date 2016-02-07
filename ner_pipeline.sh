#!/bin/sh

#Usage: bash pipeline.sh <test_directory> <"Comment about features used">

mkdir -p "$1"

echo "Running extract_features"
python extract_features.py train.gold.tpos train.gold.feats
python extract_features.py test.gold.tpos test.gold.feats
python extract_features.py print_features > "$1/README.md"

./mallet-tag.sh --train true --model-file train.model train.gold.feats 
./mallet-tag.sh --model-file train.model test.gold.feats > output.txt

python evaluate-ner.py test.gold.tpos output.txt >> "$1"/README.md
python evaluate.py test.gold.tpos output.txt >> "$1"/README.md 
echo "\n$2" >> "$1"/README.md

mv train.gold.feats test.gold.feats train.model output.txt ./"$1"
head -n 40 "$1"/README.md
