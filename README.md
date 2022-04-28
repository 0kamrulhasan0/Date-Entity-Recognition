
# Date-Entity-Recognition
From a dataset of text, it will recognize different date-time format and predict its position in the corpus.
```
pip3 install -r requirements.txt
python3 -m spacy download en_core_web_sm

python3 src/data/make_dataset.py
python4 src/models/make_model.py
```
