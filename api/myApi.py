import sys
import filters

sys.path.append('..')
from openbci.cyton import *


class BoardCytonApi:
    def __init__(self, windowSize=None, board=None, lowerBand=None, upperBand=None, timeWindow=None,
                 samplingRate=None):
        if lowerBand is None:
            self.lowerBand = 5
        else:
            self.lowerBand = lowerBand
        if upperBand is None:
            self.upperBand = 50
        else:
            self.upperBand = upperBand
        if timeWindow is None:
            self.timeWindow = 5
        else:
            self.timeWindow = timeWindow
        if samplingRate is None:
            self.samplingRate = 250
        else:
            self.samplingRate = samplingRate
        if board is None:
            self.board = None
        else:
            self.board = board
        self.connected = False
        self.printingDataConsole = True
        self.data = [[0, 0, 0, 0, 0, 0, 0, 0]]
        self.filteredData = [[0, 0, 0, 0, 0, 0, 0, 0]]
        # Define OpenBCI callback function

    def save_data(self, sample):
        # store the filtered data
        dt = []
        dtfl = []
        for i in range(len(sample.channel_data)):
            dt.append(sample.channel_data[i] * scale_fac_uVolts_per_count)
            dtfl.append(filters.bandpass(self.lowerBand, self.upperBand, [dt[i]]).item(0))
        self.data.append(dt)
        self.filteredData.append(dtfl)
        if self.printingDataConsole:
            print([i for i in np.array(self.data[-1:]).tolist()])
            print([i for i in np.array(self.filteredData[-1:]).tolist()])

    # Define thread function
    def stream(self):
        if not self.connected:
            print('Not connected board')
        else:
            self.board.start_streaming(self.save_data)

    def connect(self):
        if not self.connected:
            self.board = OpenBCICyton()
            self.connected = True
        else:
            print('Already have a connection')

    def stop(self):
        if not self.connected:
            print('Not connected board')
        else:
            self.board.stop()

    def disconnect(self):
        if not self.connected:
            print('Not connected board')
        else:
            self.board.disconnect()
            self.connected = False

    def saveDataXls(self):
        self.printingDataConsole = not self.printingDataConsole
        # t_data = np.array(data[-fs * timeWindow:]).T
        # print(t_data)
