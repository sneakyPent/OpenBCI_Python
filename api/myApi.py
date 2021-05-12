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
        if windowSize is None:
            self.windowSize = 0
        else:
            self.windowSize = windowSize
        self.connected = False
        self.printingDataConsole = False
        self.data = []
        self.filteredData = []
        # Define OpenBCI callback function
        self.windowedData = []
        self.windowedFilteredData = []
        self.window = lambda: self.samplingRate * self.windowSize

    def save_data(self, sample):
        # store the filtered data
        dt = []
        dtfl = []
        for i in range(len(sample.channel_data)):
            dt.append(sample.channel_data[i] * scale_fac_uVolts_per_count)
            dtfl.append(filters.bandpass(self.lowerBand, self.upperBand, [dt[i]]).item(0))
        self.data.append(dt)
        self.filteredData.append(dtfl)

        # check if windowed list is empty then get the first n sample, where n is the samplingRate*windowSize
        # else get the next samplingRate*windowSize/2
        if not self.windowedData and self.data.__len__() % self.window() == 0:
            firstWindow = self.data[:]
            self.windowedData.append(firstWindow)
            firstWindow = self.filteredData[:]
            self.windowedFilteredData.append(firstWindow)
        elif self.windowedData and self.data.__len__() % (self.window() / 2) == 0:
            newWindow = self.windowedData[-1][-(int(self.window() / 2)):] + self.data[-(int(self.window() / 2)):]
            self.windowedData.append(newWindow)
            newWindow = self.windowedFilteredData[-1][-(int(self.window() / 2)):] + self.filteredData[-(int(self.window() / 2)):]
            self.windowedFilteredData.append(newWindow)

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
            self.store()

    def disconnect(self):
        if not self.connected:
            print('Not connected board')
        else:
            self.board.disconnect()
            self.connected = False

    def store(self):
        name = "test1"
        hf = h5py.File(name + '.hdf5', 'w')
        hf.create_dataset("signal", data=self.data)
        hf.create_dataset("filtered signal", data=self.filteredData)
        hf.create_dataset("packages", data=self.windowedData)
        hf.create_dataset("filtered packages", data=self.windowedFilteredData)

