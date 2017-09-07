import numpy as np
import pandas as pd
from keras.models import Sequential
from keras.layers.core import Dense, Activation, Dropout
from keras.layers.recurrent import LSTM

#from sklearn.preprocessing import StandardScaler
#StandardScaler().fit_transform(data)

class IqNeuralNetwork():
    # LSTM
    #layer
        # neuron 6 -- 3 -- 1
    def __init__(self, inputShape, nCluster=30):
        self.WINDOW = 2
        self.EMB_SIZE = 5
        self.STEP = 1
        self.FORECAST = 1

        self.X = []
        self.Y = []

        self.model = Sequential()
        self.model.add(LSTM(
            input_dim=inputShape,
            output_dim=nCluster,
            return_sequences=True
        ))
        self.model.add(Dropout(0.2))
        self.model.add(LSTM(nCluster*2, return_sequences=False)) #nCluster*2, 100
        self.model.add(Dropout(0.2))
        self.model.add(Dense(output_dim=1))
        self.model.add(Activation('linear'))

        # LAYER
        self.model.compile(loss='mse', optimizer='rmsprop')

    def getTrainNpArrayFromDataframe(self, df):
        x_train = df.ix[:,:-1].as_matrix()
        y_train = df.ix[:,-1].as_matrix()

        return x_train, y_train

    def getPredictNpArrayFromDataframe(self, df):
        x_train = df.ix[:,:-1].as_matrix()

        return x_train

    def train(self, x_train, y_train):
        self.model.fit(x_train, y_train, nb_epochs=1, batch_size=512, validation_split=0.05)

    def predict(self, X_test):
        predicted = self.model.predict(X_test)
        return predicted

    def convertToList(self, data_original):
        y_i = [1, 0]
        try:
            timestamp = data_original['Timestamp'].tolist()
            open = data_original['Open'].tolist()
            close = data_original['Close'].tolist()
            high = data_original['High'].tolist()
            low = data_original['Low'].tolist()
        except:
            pass

        for i in range(0, len(data_original), self.STEP):
            try:

                t = timestamp[i:i + self.WINDOW]
                o = open[i:i + self.WINDOW]
                c = close[i:i + self.WINDOW]
                h = high[i:i + self.WINDOW]
                l = low[i:i + self.WINDOW]

                t = (np.array(t) - np.mean(t)) / np.std(t)
                o = (np.array(o) - np.mean(o)) / np.std(o)
                c = (np.array(c) - np.mean(c)) / np.std(c)
                h = (np.array(h) - np.mean(h)) / np.std(h)
                l = (np.array(l) - np.mean(l)) / np.std(l)

                print o

                x_i = close[i:i + self.WINDOW]
                y_i = close[i + self.WINDOW + self.FORECAST]

                last_close = x_i[-1]
                next_close = y_i

                if last_close < next_close:
                    y_i = [1, 0]
                else:
                    y_i = [0, 1]

                x_i = np.column_stack((t, o, c, h, l))

            except Exception as e:
                pass

            self.X.append(x_i)
            self.Y.append(y_i)

    def run(self, df):
        self.convertToList(df)

        #print self.X

        self.X, self.Y = np.array(self.X), np.array(self.Y)

        #print self.X
        X_train, X_test, Y_train, Y_test = create_Xt_Yt(self.X, self.Y)

        #print X_train.shape

        X_train = np.reshape(X_train, (X_train.shape[0], X_train.shape[1], self.EMB_SIZE))
        X_test = np.reshape(X_test, (X_test.shape[0], X_test.shape[1], self.EMB_SIZE))

        self.train(X_train, Y_train)
        self.predict(X_test)


def shuffle_in_unison(a, b):
    # courtsey http://stackoverflow.com/users/190280/josh-bleecher-snyder
    assert len(a) == len(b)
    shuffled_a = np.empty(a.shape, dtype=a.dtype)
    shuffled_b = np.empty(b.shape, dtype=b.dtype)
    permutation = np.random.permutation(len(a))
    for old_index, new_index in enumerate(permutation):
        shuffled_a[new_index] = a[old_index]
        shuffled_b[new_index] = b[old_index]
    return shuffled_a, shuffled_b


def create_Xt_Yt(X, y, percentage=0.9):
    p = int(len(X) * percentage)
    X_train = X[0:p]
    Y_train = y[0:p]

    X_train, Y_train = shuffle_in_unison(X_train, Y_train)

    X_test = X[p:]
    Y_test = y[p:]

    return X_train, X_test, Y_train, Y_test