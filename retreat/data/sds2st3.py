"""sds2st3"""
import os
import sys
from obspy.clients.filesystem.sds import Client
#import time
#from obspy import UTCDateTime
#import PySimpleGUI as sg
#import concurrent.futures

def sds2st(scnl, sds_root, sds_type, customfmt, myfmtstr, t, length, logfile):
    """Fetches stream object from local storage using SDS directory structure"""
    # redirect output to log file:s
    sys.stdout = open(logfile, 'a+')
    sys.stderr = sys.stdout

    #print('Process p (sds2st) id: {}'.format(os.getpid()))

    # set up client
    client = Client(sds_root, sds_type)
    if customfmt:
        print('Using custom directory structure:')
        print(myfmtstr)
        client.FMTSTR = myfmtstr

    # check directory
    if os.path.isdir(sds_root) is False:
        print("Error: sds_root directory does not exist! Please check input")
        raise StopIteration

    try:
        # ... do stuff ...
        print("Retrieving data from filesystem...")
        #window.Refresh()

        # fetch data

### DEBUGGING
#        print(client.FMTSTR)
#        print(client.format)
#        print(client.sds_root)
#        print(client.sds_type)
#        print(t)
#        print(length)
######
        st = client.get_waveforms(scnl["N"], scnl["S"], scnl["L"], scnl["C"], t, t+length, merge=1)

#        with concurrent.futures.ProcessPoolExecutor(max_workers=1) as executor:
#                st = executor.submit(client.get_waveforms,scnl["N"], scnl["S"], scnl["L"],\
#                scnl["C"], t, t + length,merge=1).result()

        # check for empty stream:
        if len(st) < 1:
            print("Error: Stream empty - please check your data source")
            msg = "Empty stream object"
            raise IndexError(msg)
        else:
            # try to merge any data in multiple traces:
            st.merge(method=1)
            #print(st)

    except Exception as e:
        # ... log it, sleep, etc. ...
        print('Error retrieving data: '+ str(e))

    return st
