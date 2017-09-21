_author_ = 'Lorenzo Argentieri'

import time
import sys

#from Qt import QtWidgets, QtCore
from PyQtX import QtCore, QtWidgets

import iqoption as iq
import martingale
import pandasmanager
import QMatplotlib
import neuralnetwork as nn
#import model


class QtIQOption(QtWidgets.QWidget, QtCore.QObject):
    def __init__(self, parent=None):
        super(QtIQOption, self).__init__(parent)

        # Initialize Core
        self.martingale = martingale.Martingale()
        self.neural = nn.IqNeuralNetwork()
        self.iqStream = iq.IQOption()
        self.dataframeManager = pandasmanager.PandasManager()

        # Initialize UI
        self.setWindowTitle('IqOptionNeural')
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.layout = QtWidgets.QGridLayout()
        self.log = QtWidgets.QTextEdit()
        self.graph = QMatplotlib.QMatplotlib()

        # Layout
        self.layout.addWidget(self.log)
        self.layout.addWidget(self.graph)
        self.setLayout(self.layout)

        # TEST
        #self.execButton.clicked.connect(self.execFunction)

        # Startup
        self.bootstrapCounter = 0
        #self.updateLog()


        # Prepare Timer
        currentTime = QtCore.QTime.currentTime()
        nextMinute = QtCore.QTime(currentTime.hour(), currentTime.minute()+1)
        waitSignal = currentTime.secsTo(nextMinute)
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.callback)
        self.timer.start((waitSignal)*1000)

    def callback(self):
        print('Callback ')
        self.timer.start(60*1000)
        self.updateLog()


    def updateLog(self):
        # Boostrap
        candleData = self.iqStream.getCandles()
        if candleData:
            self.dataframeManager.appendIQCandleRow(candleData)
            print self.dataframeManager.df.shape
            print self.dataframeManager.df

            if self.bootstrapCounter > 30:
                result = self.iqStream.getResult()
                print 'TRADE RESULT: ', result
                self.martingale.calc(result)# ToDo

                #result = self.invest(self.martingale.getCurrentInvest())
            else:
                self.log.append('Whait ' + str(30-self.bootstrapCounter) + ' minutes to Start!')
                self.bootstrapCounter = self.bootstrapCounter + 1

            # update chart
            self.graph.clear()
            self.graph.addDataframe(self.dataframeManager.readLastNCluster(30))
            self.graph.plot()

    def invest(self, amount=1):
        data = self.iqStream.getDataFrame()
        while data.empty:
            time.sleep(1)
            data = self.iqStream.getDataFrame()
            print 'wait'

        if not data.empty:
            old, last, current = self.iqStream.getCandles()

            # add last candle
            price_predict = self.neural.predict()## to do

            # get last investment status
            result = self.iqStream.getResult()
            self.martingale.calc(result)
            investAmount = self.martingale.getCurrentInvest()

            lastClose = last[2]
            print 'FORECAST PRICE: ', price_predict

            if price_predict >= lastClose:
                self.iqStream.openPosition(amount=investAmount, direction="call")
                print 'BUY'
            else:
                self.iqStream.openPosition(amount=investAmount, direction="put")
                print 'SELL'

            return price_predict


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    mainApp = QtIQOption()
    mainApp.show()

    sys.exit(app.exec_())


