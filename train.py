import csv
import re

import pandas as pd
from nltk import SnowballStemmer

from models import *


def str2list(str):
    str.lower().split()
    # stops = set(stopwords.words("english"))
    # str = [w for w in str if not w in stops]
    str = " ".join(str)
    str = re.sub(r"e?li5:?", "", str)
    str = re.sub(r"[^A-Za-z0-9^'+=]", " ", str)
    str = re.sub(r"that's", "that is ", str)
    str = re.sub(r"it's", "it is ", str)
    str = re.sub(r"what's", "what is ", str)
    str = re.sub(r"\'s", " ", str)
    str = re.sub(r"\'ve", " have ", str)
    str = re.sub(r"can't", "cannot ", str)
    str = re.sub(r"n't", " not ", str)
    str = re.sub(r"i'm", "i am ", str)
    str = re.sub(r"\'re", " are ", str)
    str = re.sub(r"\'d", " would ", str)
    str = re.sub(r"\'ll", " will ", str)
    str = re.sub(r"\+", " and ", str)
    str = re.sub(r"\=", " equals ", str)
    str = re.sub(r"'", " ", str)
    str = re.sub(r":", " : ", str)
    str = re.sub(r" e.? g.? ", " for example ", str)
    str = re.sub(r" i.? e.? ", " that is ", str)
    str = re.sub(r" u s ", " america ", str)
    str = re.sub(r"\0s", "0", str)
    str = re.sub(r"\s{2,}", " ", str)

    str = str.split()
    stemmer = SnowballStemmer('english')
    stemmed_words = [stemmer.stem(word) for word in str]
    str = " ".join(stemmed_words)
    return str

words = pd.read_table(config['train']['embed'], sep=" ", index_col=0, header=None, quoting=csv.QUOTE_NONE)


def w2v(w):
    w.lower()
