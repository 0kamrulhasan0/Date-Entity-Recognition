from spacy.util import minibatch, compounding
from pathlib import Path
import pandas as pd
import random
import spacy


def format_data(articles, LABEL):
    """Format the Training examples in the required format"""
    DATA = []
    for index, row in articles.iterrows():
        _, article, _, _, _, is_deadline, start, end = row
        entities = [] if not is_deadline else [(start, end, LABEL)]
        DATA.append((article, {"entities": entities}))
    return DATA


def test_train_split(DATA, split=0.8):
    """ Splits DATA into train and test according to split ratio  """
    random.shuffle(DATA)
    split_point = int(split * len(DATA))
    TRAIN_DATA = DATA[:split_point]
    TEST_DATA = DATA[split_point:]
    return TRAIN_DATA, TEST_DATA


def train_model(nlp, LABEL, TRAIN_DATA):
    """ Trains models """
    print("Training Start !")
    ner = nlp.get_pipe("ner")
    ner.add_label(LABEL)
    optimizer = nlp.resume_training()
    move_names = list(ner.move_names)
    pipe_exceptions = ["ner", "trf_wordpiecer", "trf_tok2vec"]
    other_pipes = [pipe for pipe in nlp.pipe_names if pipe not in pipe_exceptions]
    with nlp.disable_pipes(*other_pipes):
        sizes = compounding(1.0, 4.0, 1.001)
        for itn in range(5):
            random.shuffle(TRAIN_DATA)
            batches = minibatch(TRAIN_DATA, size=sizes)
            losses = {}
            for batch in batches:
                texts, annotations = zip(*batch)
                nlp.update(texts, annotations, sgd=optimizer, drop=0.35, losses=losses)
                print("Losses", losses)
    nlp.meta["name"] = "Date_Recognizer"
    print("Training End !")
    return nlp


def save_model(nlp, output_dir):
    """ Saves the trained model weights to output_dir"""
    nlp.to_disk(output_dir)
    print("Saved model to ", output_dir)


def test_model(nlp, TEST_DATA):
    """ Compares Prediction and Original """
    print("Compare Negative Data Points:")
    predicted = "Predicted"
    orinigal = "Original"
    print("-" * 50)
    print(f"{predicted:10} {orinigal}")
    negative_points = [t for t in TEST_DATA if not t[1]["entities"]]
    for data_point in negative_points:
        text, entity = data_point
        doc = nlp(text)
        for ent in doc.ents:
            print(f"{ent.text:10} {entity['entities']}")
    print("Compare Positive Data Points:")
    predicted = "Predicted"
    orinigal = "Original"
    print("-" * 50)
    print(f"{predicted:10} {orinigal}")
    positive_points = [t for t in TEST_DATA if t[1]["entities"]]
    for data_point in positive_points:
        text, entity = data_point
        doc = nlp(text)
        for ent in doc.ents:
            print(
                f"{ent.text:40} {text[entity['entities'][0][0]:entity['entities'][0][1]]}"
            )


def main():
    articles = pd.read_csv("data/processed/Processed_Articles.csv")
    output_dir = Path("model/")
    LABEL = "DATE"
    DATA = format_data(articles, LABEL)
    TRAIN_DATA, TEST_DATA = test_train_split(DATA, split=0.8)
    try:
        nlp = spacy.load(output_dir)
    except:
        pass
    finally:
        nlp = spacy.load("en_core_web_sm")
        nlp = train_model(nlp, LABEL, TRAIN_DATA)
        save_model(nlp)
    test_model(nlp, TEST_DATA)


if __name__ == "__main__":
    main()
