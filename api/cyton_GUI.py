#!/usr/bin/python
import traceback
from PyQt5.QtCore import QThread, QRunnable, pyqtSlot, QThreadPool, pyqtSignal, QObject, QTimer
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import pyqtgraph as pg
from myApi import *
from numpy import savetxt

ts_plot = []
bp_data = [[], [], [], [], [], [], [], []]

colors = 'rgbycmwr'


class WorkerSignals(QObject):
    '''
    Defines the signals available from a running worker thread.

    Supported signals are:

    finished
        No data

    error
        tuple (exctype, value, traceback.format_exc() )

    result
        object data returned from processing, anything

    progress
        int indicating % progress

    '''
    finished = pyqtSignal()
    error = pyqtSignal(tuple)
    result = pyqtSignal(object)
    progress = pyqtSignal(int)


class Worker(QRunnable):
    '''
    Worker thread

    Inherits from QRunnable to handler worker thread setup, signals and wrap-up.

    :param callback: The function callback to run on this worker thread. Supplied args and
                     kwargs will be passed through to the runner.
    :type callback: function
    :param args: Arguments to pass to the callback function
    :param kwargs: Keywords to pass to the callback function

    '''

    def __init__(self, fn, *args, **kwargs):
        super(Worker, self).__init__()

        # Store constructor arguments (re-used for processing)
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

        # Add the callback to our kwargs
        # self.kwargs['progress_callback'] = self.signals.progress

    @pyqtSlot()
    def run(self):
        '''
        Initialise the runner function with passed args, kwargs.
        '''

        # Retrieve args/kwargs here; and fire processing using them
        try:
            result = self.fn(*self.args, **self.kwargs)
        except:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        else:
            self.signals.result.emit(result)  # Return the result of the processing
        finally:
            self.signals.finished.emit()  # Don


class GUI(QMainWindow):

    def __init__(self):
        super().__init__()
        self.board = BoardCytonApi()
        self.timer = QTimer()
        self.timer.timeout.connect(self.graphUpdater)
        self.timer.setInterval(0)
        self.timer.start()
        self.thread = QThread()
        self.threadPool = QThreadPool()
        self.dock = QDockWidget(self)
        self.initUI()
        # ff
        widget = QWidget(parent=self)
        self.grid = QGridLayout(widget)
        self.setCentralWidget(widget)
        widget.setLayout(self.grid)
        self.show()

    def initUI(self):
        QToolTip.setFont(QFont('SansSerif', 10))
        menubar = self.menuBar()
        # Menu Bar options
        saveDataAction = QAction('Save in &xls file', self)
        startStreamAction = QAction('&Start streaming', self)
        stopStreamAction = QAction('Sto&p streaming', self)
        connectAction = QAction('&Connect', self)
        disconnectAction = QAction('&Disconnect', self)
        quitting = QAction('&QUIT', self)
        graphs = menubar.addMenu('&Add Graphs')
        timeSeriesPlotAction = QAction('Time series', self)
        fftPlotAction = QAction('FFT', self)
        bandsPlotAction = QAction('Bands', self)
        graphs.addActions([timeSeriesPlotAction, fftPlotAction, bandsPlotAction])
        menubar.addActions([saveDataAction, startStreamAction, stopStreamAction, connectAction, disconnectAction, quitting])
        """
                -MENU BAR ACTIONS FOR EACH OPTION 
                   
        Adding every action in thread so as the GUI not freezing,
        when waiting each process to finished. In order to do this 
        we create a worker object, pass the function as argument,
        and then add the worker object to QThreadPool of GUI-QMainWindow
        object. Lastly pass this action in connect as lambda expression
        
        """
        saveDataAction.triggered.connect(lambda : self.threadPool.start(Worker(self.board.saveDataXls)))
        startStreamAction.triggered.connect(lambda: self.threadPool.start(Worker(self.board.stream)))
        stopStreamAction.triggered.connect(lambda: self.threadPool.start(Worker(self.board.stop)))
        connectAction.triggered.connect(lambda: self.threadPool.start(Worker(self.board.connect)))
        disconnectAction.triggered.connect(lambda: self.threadPool.start(Worker(self.board.disconnect)))
        quitting.triggered.connect(QApplication.instance().quit)

        timeSeriesPlotAction.triggered.connect(self.addTimeSeriesPlot)
        fftPlotAction.triggered.connect(self.addFFTPlot)
        bandsPlotAction.triggered.connect(self.addBandsPlot)

        self.resize(2000, 1000)
        self.setStyleSheet("QMainWindow {background: 'black';}");
        self.dock.setWindowTitle('CYTON GUI')

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def addTimeSeriesPlot(self):
        # ts_plots = [win.addPlot(row=i, col=0, colspan=2, title='Channel %d' % i, labels={'left': 'uV'})
        for i in range(1, 9):
            graphWidget = pg.plot(title='Channel %d' % i,
                                  labels={'left': 'uV', 'bottom': 'sec'},
                                  )
            ts_plot.append(graphWidget)
            self.grid.addWidget(graphWidget, i, 0)

    def addFFTPlot(self):
        print('added fft plot')

    def addBandsPlot(self):
        print('added bands plot')

    def graphUpdater(self):
        t_data = np.array(self.board.filteredData[-self.board.samplingFrequency * self.board.timeWindow:]).T
        for i in range(8):
            if len(ts_plot) > 0:
                ts_plot[i].clear()
                ts_plot[i].plot(pen=colors[i]).setData(t_data[i])


if __name__ == '__main__':
    app = QApplication(sys.argv)
    gui = GUI()
    sys.exit(app.exec_())
