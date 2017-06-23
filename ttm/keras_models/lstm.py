from keras.preprocessing.sequence import pad_sequences
from keras.utils import to_categorical
from keras.models import Sequential
from keras.layers import Dense, Embedding, LSTM, Bidirectional


class LSTMClassifier(object):

    def __init__(
            self,
            layers=1,
            units=128,
            dropout_rate=0.2,
            rec_dropout_rate=0.2,
            embedding_dim=128,
            max_seq_len=1000,
            bidirectional=False,
            epochs=15,
            batch_size=128):
        self.layers = layers
        self.units = units
        self.dropout_rate = dropout_rate
        self.rec_dropout_rate = rec_dropout_rate
        self.epochs = epochs
        self.batch_size = batch_size
        self.max_seq_len = max_seq_len
        self.embedding_dim = embedding_dim
        self.bidirectional = bidirectional

        self.vocab_size = None
        self.num_classes = None
        self.model = None

    def set_vocab_size(self, n):
        self.vocab_size = n

    def set_class_count(self, n):
        self.num_classes = n

    def fit(self, X, y):
        if self.vocab_size is None or self.num_classes is None:
            raise ValueError(
                "Must set vocab size and class count before training")

        padded_X = pad_sequences(X, self.max_seq_len)
        one_hot_y = to_categorical(y, num_classes=self.num_classes)

        model = Sequential()
        model.add(Embedding(self.vocab_size, self.embedding_dim))
        for i in range(1, self.layers + 1):
            # if there are more lstms downstream - return sequences
            return_sequences = i < self.layers
            layer = LSTM(
                self.units,
                dropout=self.dropout_rate,
                recurrent_dropout=self.rec_dropout_rate,
                return_sequences=return_sequences)
            if self.bidirectional:
                model.add(Bidirectional(layer))
            else:
                model.add(layer)

        model.add(Dense(self.num_classes, activation='softmax'))

        model.compile(loss='categorical_crossentropy',
                      optimizer='adam',
                      metrics=['accuracy'])

        model.fit(padded_X, one_hot_y,
                  batch_size=self.batch_size,
                  epochs=self.epochs)

        self.model = model
        return self

    def predict_proba(self, X):
        X = pad_sequences(X, self.max_seq_len)
        return self.model.predict(X)

    def predict(self, X):
        return self.predict_proba(X).argmax(axis=1)

    def __str__(self):
        s = "LSTMClassifier(layers=%s, units=%s, dropout_rate=%s, " \
               "rec_dropout_rate=%s, " \
               "embedding_dim=%s, max_seq_len=%s, epochs=%s, batch_size=%s)" % (
                   self.layers, self.units, self.dropout_rate, self.rec_dropout_rate,
                   self.embedding_dim, self.max_seq_len,
                   self.epochs, self.batch_size)
        if self.bidirectional:
            s = 'B' + s
        return s
