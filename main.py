_author_ = 'Lorenzo Argentieri'

import time
import sys
import datetime

#from Qt import QtWidgets, QtCore
from PyQtX import QtCore, QtWidgets

import iqoption as iq
import martingale
#import neuralnetwork as nn
import model


class QtIQOption(QtWidgets.QWidget, QtCore.QObject):
    def __init__(self, parent=None):
        super(QtIQOption, self).__init__(parent)

        self.iqStream = iq.IQOption()
        self.martingale = martingale.Martingale()

        self.setWindowTitle('IqOptionNeural')
        self.layout = QtWidgets.QGridLayout()
        self.log = QtWidgets.QTextEdit()

        self.layout.addWidget(self.log)
        self.setLayout(self.layout)

        #self.neural = nn.IqNeuralNetwork()
        self.iqStream = iq.IQOption()


        # TEST
        #self.execButton.clicked.connect(self.execFunction)
        #thread_instance = Thread()
        #thread_instance.start()
        self.timer()

    def timer(self):
        self.currentTime = QtCore.QTime.currentTime()
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.updateLog)
        self.timer.start(1000*60)
        print('Timer Started')

    def updateLog(self):
        result = self.iqStream.getResult()
        print 'TRADE RESULT: ', result
        self.martingale.calc(result)# ToDo

        self.invest(self.martingale.getCurrentInvest())

    def invest(self, amount=1):
        data = self.iqStream.getDataFrame()
        while data.empty:
            time.sleep(1)
            data = self.iqStream.getDataFrame()
            print 'wait'

        if not data.empty:
            old, last, current = self.iqStream.getCandles()

            result = model.expression(old[0], old[2], old[3], old[1],
                                      last[0], last[2], last[3], last[1],
                                      current[0], current[2], current[3])

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


