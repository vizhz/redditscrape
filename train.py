import csv
import gc
import re
import threading
from queue import Queue

import numpy as np
import pandas as pd
from keras.layers import Conv1D, MaxPooling1D, Dense
from keras.layers import Embedding, Flatten
from keras.models import Sequential
from keras.preprocessing.sequence import pad_sequences
from keras.preprocessing.text import Tokenizer
from keras.utils import to_categorical

from models import *

# from nltk import SnowballStemmer

useglove = False
glove_dim = int(config['train']['glove_dim'])


# processes common elements in text
def str2list(sent):
    sent = sent.lower().split()
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

    # sent = sent.split()
    # stemmer = SnowballStemmer('english')
    # stemmed_words = [stemmer.stem(word) for word in sent]
    # sent = " ".join(stemmed_words)
    return sent, len(sent.split())


def fetchGlove(que):
    logger.info('loading glove')
    que.put(pd.read_table(config['train']['embed'], sep=" ",
                          index_col=0,
                          header=None,
                          quoting=csv.QUOTE_NONE))
    logger.info('loaded glove')


queue = Queue()
thread_ = threading.Thread(target=fetchGlove, name='thread_1', args=[queue])
if useglove:
    thread_.start()

flairs = config['train']['flairs'].split()
flairmap = dict(zip(flairs, range(len(flairs))))

Xdata = []
ydata = []
maxlen = 0

logger.info('pre-processing text')
for sub in Submission.select().where(Submission.flair in flairs):
    txt = sub.title + ' ' + sub.body
    if (not sub.flair in flairs) or len(txt) < 15:
        continue
    txt, leng = str2list(txt)
    if (maxlen < leng):
        maxlen = leng
    Xdata.append(txt)
    ydata.append(flairmap[sub.flair])

tokenizer = Tokenizer(num_words=50000)
tokenizer.fit_on_texts(Xdata)
sequences = tokenizer.texts_to_sequences(Xdata)

word_index = tokenizer.word_index
logger.info('Found %s unique tokens.' % len(word_index))

data = pad_sequences(sequences, maxlen=maxlen)

labels = to_categorical(np.asarray(ydata))
logger.info('Shape of data tensor: ' + data.shape.__str__())
logger.info('Shape of label tensor: ' + labels.shape.__str__())

# split the data into a training set and a validation set
indices = np.arange(data.shape[0])
np.random.shuffle(indices)
data = data[indices]
labels = labels[indices]
nb_validation_samples = int(0.1 * data.shape[0])

x_train = data[:-nb_validation_samples]
y_train = labels[:-nb_validation_samples]
x_val = data[-nb_validation_samples:]
y_val = labels[-nb_validation_samples:]
logger.info('finished pre-processing')


def w2v(w):
    try:
        return words.loc[w].as_matrix()
    except KeyError:
        return None


embedding_matrix = np.zeros((len(word_index) + 1, glove_dim))
if useglove:
    thread_.join()
    words = queue.get()

    for word, i in word_index.items():
        embedding_vector = w2v(word)
        if embedding_vector is not None:
            embedding_matrix[i] = embedding_vector

gc.collect()
model = Sequential()
model.add(Embedding(len(word_index) + 1,
                    glove_dim,
                    input_length=maxlen,
                    weights=[embedding_matrix] if useglove else None,
                    trainable=not useglove))
model.add(Conv1D(75, 2, activation='tanh'))
model.add(MaxPooling1D())
model.add(Flatten())
model.add(Dense(75, activation='tanh'))
model.add(Dense(len(flairs), activation='softmax'))
model.compile(loss='categorical_crossentropy',
              optimizer='rmsprop',
              metrics=['acc'])
result = model.fit(x_train, y_train,
                   batch_size=32,
                   epochs=3,
                   validation_data=(x_val, y_val),
                   shuffle=True,
                   verbose=2)
