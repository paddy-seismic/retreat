"""Launches the gui"""
import argparse
from retreat.start import start

parser = argparse.ArgumentParser()
parser.add_argument("-w", "--web", help="Run using web interface in browser rather than GUI window",
                    action="store_true")
parser.add_argument("-c", "--cmd", help="Run using command interface - NO GUI, \
                    parameters read from defaults file",
                    action="store_true")
args = parser.parse_args()

if __name__ == '__main__':
    start(args)
