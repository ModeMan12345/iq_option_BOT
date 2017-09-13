_author_ = 'Lorenzo Argentieri'

import time
import sys
import datetime

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
        self.updateLog()
        self.timer()

    def timer(self):
        self.currentTime = QtCore.QTime.currentTime()
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.updateLog)
        self.timer.start(1000*60)
        print('Timer Started')

    def updateLog(self):
        # Boostrap
        if self.bootstrapCounter > 30:
            result = self.iqStream.getResult()
            print 'TRADE RESULT: ', result
            self.martingale.calc(result)# ToDo

            self.invest(self.martingale.getCurrentInvest())
        else:
            self.log.append('Whait ' + str(30-self.bootstrapCounter) + ' minutes to Start!')
            # get last 3 Candle
            # Draw chart
            self.bootstrapCounter = self.bootstrapCounter + 1

    def invest(self, amount=1):
        data = self.iqStream.getDataFrame()
        while data.empty:
            time.sleep(1)
            data = self.iqStream.getDataFrame()
            print 'wait'

        if not data.empty:
            old, last, current = self.iqStream.getCandles()

            # add last candle
            result = self.neural.predict()## to do

            lastClose = last[2]
            print 'FORECAST PRICE: ', result

            if result >= lastClose:
                self.iqStream.openPosition(amount=amount, direction="call")
                print 'BUY'
            else:
                self.iqStream.openPosition(amount=amount, direction="put")
                print 'SELL'


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    mainApp = QtIQOption()
    mainApp.show()

    sys.exit(app.exec_())


