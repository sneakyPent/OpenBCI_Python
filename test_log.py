from __future__ import print_function
import time
import logging
from openbci import cyton as bci
import sys
import pdb

sys.path.append('..')  # help python find cyton.py relative to scripts folder


def printData(sample):
    # os.system('clear')
    print("----------------")
    print("%f" % (sample.id))
    print(sample.channel_data)
    print(sample.aux_data)
    print("----------------")


if __name__ == '__main__':
    port = '/dev/ttyUSB1'
    baud = 115200
    logging.basicConfig(filename="test.log", format='%(message)s', level=logging.DEBUG)
    logging.info('---------LOG START-------------')
    board = bci.OpenBCICyton(port=port, scaled_output=False, log=True)

    # 32 bit reset
    pdb.set_trace()
    board.ser.write('v')
    time.sleep(0.100)
    pdb.set_trace()

    # # connect pins to vcc
    # board.ser.write('p')
    # time.sleep(0.100)

    # # board.start_streaming(printData)
    # board.print_packets_in()
