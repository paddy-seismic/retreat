"""fdsn2st3"""
import logging
import time
import sys
from obspy.clients.fdsn import Client
#from obspy.clients.fdsn.header import FDSNException
#from obspy import UTCDateTime
#import PySimpleGUI as sg

def fdsn2st(scnl, myclient, t, length, logfile):
    """Fetches stream object from server using FDSN client"""
    # redirect output to log file:
    sys.stdout = open(logfile, 'a+')
    sys.stderr = sys.stdout

    max_retries = 5
    nsleep = 10 # seconds to wait before retrying

    client = Client(myclient)

    for _ in range(max_retries):

        try:
                # ... do stuff ...
            print("Connecting to server...")
            st = client.get_waveforms(scnl["N"], scnl["S"], scnl["L"], scnl["C"], t, t + length)
        except Exception as e:
            # ... log it, sleep, etc. ...
            print('Connection error: '+ str(e))
            logging.error('Connection error: '+ str(e))
            print("Will retry in ", str(nsleep), "s")
            logging.info("Will retry in %ss", nsleep)
            time.sleep(nsleep)
            continue
        else:
            break
    else:
        print("Can't connect to server. Giving up")
        raise SystemExit("Can't connect to server. Giving up")

#	st = client.get_waveforms(scnl["N"], scnl["S"], scnl["L"], scnl["C"], t, t + length)

    return st
