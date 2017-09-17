import sys
import numpy as np
import pandas as pd
from PyQt5.QtWidgets import QDialog, QApplication, QPushButton, QVBoxLayout

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt
from matplotlib.finance import candlestick2_ohlc

import random

class QMatplotlib(QDialog):
    def __init__(self, parent=None):
        super(QMatplotlib, self).__init__(parent)

        # a figure instance to plot on
        self.figure = plt.figure()

        # this is the Canvas Widget that displays the `figure`
        # it takes the `figure` instance as a parameter to __init__
        self.canvas = FigureCanvas(self.figure)

        # this is the Navigation widget
        # it takes the Canvas widget and a parent
        self.toolbar = NavigationToolbar(self.canvas, self)

        # Just some button connected to `plot` method
        self.button = QPushButton('Plot')
        self.button.clicked.connect(self.plot)

        # set the layout
        layout = QVBoxLayout()
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)
        layout.addWidget(self.button)
        self.setLayout(layout)

        #store array
        self.prevision = []
        self.ordercolumns = ['DateTime', 'Open', 'Close', 'High', 'Low']
        self.currentData = pd.DataFrame({'DateTime': [], 'Open': [], 'Close': [], 'High': [], 'Low': []})

    def plot(self, df):
        ''' plot some random stuff '''
        # random data
        #data = [random.random() for i in range(50)]

        # create an axis
        ax = self.figure.add_subplot(111)

        # discards the old graph
        # ax.hold(False) # deprecated, see above
        candlestick2_ohlc(ax, df['Open'], df['High'], df['Low'], df['Close'], width=0.6)

        # plot data
        #ax.plot(data, 'x-')


        # refresh canvas
        self.canvas.draw()

    def addDataframe(self, df):
        self.currentData = df

    def addPrevision(self, val):
        pass

    def clear(self):
        self.figure.clear()

if __name__ == '__main__':
    import pandasmanager
    app = QApplication(sys.argv)

    main = QMatplotlib()
    test = pandasmanager.PandasManager()
    df = test.readAllDataframe()
    main.addDataframe(df=df)
    main.show()

    sys.exit(app.exec_())