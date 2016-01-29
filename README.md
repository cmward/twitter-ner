# Twitter NER

To featurize pos tagged train set:
```
python extract_features.py train.gold.pos train.gold.feats
python extract_features.py dev.gold.pos dev.gold.feats
```

To train model using Mallet:
```
./mallet-tag.sh --train true --model-file <MODEL_FILE> train.gold.feats
```
NOTE: To use the `mallet-tag.sh`, set `MALLET_HOME` to where you installed Mallet.

To tag using trained model:
```
/mallet-tag.sh --model-file <MODEL_FILE> dev.gold.feats > output.txt  
```

To evaluate results:
```
python evaluate.py <GOLD_FILE> output.txt
```
