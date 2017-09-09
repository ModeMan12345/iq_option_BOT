import time
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
    # [3,window,1] -- [nFeatures, seqLen, 1]
    def __init__(self, nFeatures=1, seqLen=30, nCluster=1):
        #self.model = self.build_model2([nFeatures, seqLen, 1])
        self.model = self.build_model_OLD(seqLen)

    def build_model_OLD(self, seqLen, nCluster):
        model = Sequential()
        model.add(LSTM(
            input_dim=nCluster,
            output_dim=seqLen,
            return_sequences=True,
        ))
        model.add(Dropout(0.2))
        model.add(LSTM(seqLen * 2, return_sequences=False))  # nCluster*2, 100
        model.add(Dropout(0.2))
        model.add(Dense(output_dim=1))
        model.add(Activation('linear'))

        # LAYER
        model.compile(loss='mse', optimizer='rmsprop')

        return model

    def build_model(self, layers):
        model = Sequential()

        model.add(LSTM(
            input_dim=layers[0],
            output_dim=layers[1],
            return_sequences=True))
        model.add(Dropout(0.2))

        model.add(LSTM(
            layers[2],
            return_sequences=False))
        model.add(Dropout(0.2))

        model.add(Dense(
            output_dim=layers[2]))
        model.add(Activation("linear"))

        start = time.time()
        model.compile(loss="mse", optimizer="rmsprop", metrics=['accuracy'])
        print("Compilation Time : ", time.time() - start)
        return model

    def build_model2(self, layers):
        d = 0.2
        model = Sequential()
        model.add(LSTM(128, input_shape=(layers[1], layers[0]), return_sequences=True))
        model.add(Dropout(d))
        model.add(LSTM(64, input_shape=(layers[1], layers[0]), return_sequences=False))
        model.add(Dropout(d))
        model.add(Dense(16, init='uniform', activation='relu'))
        model.add(Dense(1, init='uniform', activation='relu'))
        model.compile(loss='mse', optimizer='adam', metrics=['accuracy'])
        return model

    def getTrainNpArrayFromDataframe(self, df):
        x_train = df.ix[:,:-1].as_matrix()
        y_train = df.ix[:,-1].as_matrix()

        return x_train, y_train

    def getPredictNpArrayFromDataframe(self, df):
        x_train = df.ix[:,:-1].as_matrix()

        return x_train

    def load_data(self, stock, seq_len):
        amount_of_features = len(stock.columns)
        data = stock.as_matrix()  # pd.DataFrame(stock)
        sequence_length = seq_len + 1
        result = []
        for index in range(len(data) - sequence_length):
            result.append(data[index: index + sequence_length])

        result = np.array(result)
        row = round(0.9 * result.shape[0])
        train = result[:int(row), :]
        x_train = train[:, :-1]
        y_train = train[:, -1][:, -1]
        x_test = result[int(row):, :-1]
        y_test = result[int(row):, -1][:, -1]

        x_train = np.reshape(x_train, (x_train.shape[0], x_train.shape[1], amount_of_features))
        x_test = np.reshape(x_test, (x_test.shape[0], x_test.shape[1], amount_of_features))

        return [x_train, y_train, x_test, y_test]

    def train(self, x_train, y_train):
        self.model.fit(x_train, y_train, nb_epochs=1, batch_size=512, validation_split=0.05)

    def predict(self, X_test):
        predicted = self.model.predict(X_test)
        return predicted

    def run(self, df):
        x_train, y_train, x_test, y_test = self.load_data(df, seq_len=1)# ToDo Test

        self.train(x_train, y_train)
        self.predict(x_test)
