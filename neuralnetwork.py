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
    #input_shape(nb_samples, timesteps, input_dim) --- (4999, 30, 1)

    # [3,window,1] -- [nFeatures, seqLen, 1]
    # layer --- len , seqLen, nFeatures
    def __init__(self, nFeatures=5, seqLen=30, nCluster=1):
        self.model = self.build_model([nFeatures, seqLen, 1])

    def build_model(self, layers):
        d = 0.2
        model = Sequential()
        model.add(LSTM(128, input_shape=(layers[1], layers[0]), return_sequences=True))
        model.add(Dropout(d))
        model.add(LSTM(64, input_shape=(layers[1], layers[0]), return_sequences=False))
        model.add(Dropout(d))
        model.add(Dense(16, kernel_initializer='uniform', activation='relu'))
        model.add(Dense(1, kernel_initializer='uniform', activation='relu'))
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

        self.x_train, self.y_train, self.x_test, self.y_test = [x_train, y_train, x_test, y_test]

        return [x_train, y_train, x_test, y_test]

    def train(self, x_train, y_train):
        self.model.fit(x_train, y_train, epochs=500, batch_size=512, validation_split=0.05)

    # def train(self):
    #     self.model.fit(self.x_train, self.y_train, epochs=500, batch_size=512, validation_split=0.05)

    def predict(self, X_test):
        predicted = self.model.predict(X_test)
        return predicted

    def run(self, df):
        x_train, y_train, x_test, y_test = self.load_data(df, seq_len=1)# ToDo Test

        self.train(x_train, y_train)
        self.predict(x_test)
