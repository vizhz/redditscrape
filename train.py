import csv
import re

import numpy as np
import pandas as pd
from nltk import SnowballStemmer

from models import *


def str2list(sent):
    sent.lower().split()
    # stops = set(stopwords.words("english"))
    # str = [w for w in str if not w in stops]
    sent = " ".join(sent)
    sent = re.sub(r"e?li5:?", "", sent)
    sent = re.sub(r"[^A-Za-z0-9^'+=]", " ", sent)
    sent = re.sub(r"that's", "that is ", sent)
    sent = re.sub(r"it's", "it is ", sent)
    sent = re.sub(r"what's", "what is ", sent)
    sent = re.sub(r"\'s", " ", sent)
    sent = re.sub(r"\'ve", " have ", sent)
    sent = re.sub(r"can't", "cannot ", sent)
    sent = re.sub(r"n't", " not ", sent)
    sent = re.sub(r"i'm", "i am ", sent)
    sent = re.sub(r"\'re", " are ", sent)
    sent = re.sub(r"\'d", " would ", sent)
    sent = re.sub(r"\'ll", " will ", sent)
    sent = re.sub(r"\+", " and ", sent)
    sent = re.sub(r"\=", " equals ", sent)
    sent = re.sub(r"'", " ", sent)
    sent = re.sub(r":", " : ", sent)
    sent = re.sub(r" e.? g.? ", " for example ", sent)
    sent = re.sub(r" i.? e.? ", " that is ", sent)
    sent = re.sub(r" u s ", " america ", sent)
    sent = re.sub(r"\0s", "0", sent)
    sent = re.sub(r"\s{2,}", " ", sent)

    sent = sent.split()
    stemmer = SnowballStemmer('english')
    stemmed_words = [stemmer.stem(word) for word in sent]
    sent = " ".join(stemmed_words)
    return sent

words = pd.read_table(config['train']['embed'], sep=" ", index_col=0, header=None, quoting=csv.QUOTE_NONE)

def w2v(w):
    try:
        return words.loc[w].as_matrix()
    except KeyError:
        diff = words.as_matrix() - w
        delta = np.sum(diff * diff, axis=1)
        i = np.argmin(delta)
        return words.loc[w].as_matrix()
    finally:
        return w
