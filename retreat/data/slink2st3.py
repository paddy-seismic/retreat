"""slink2st3"""
import time
import sys
from obspy.clients.seedlink.basic_client import Client

def slink2st(scnl, myclient, t, length, logfile):
    """fetches stream object from server using seedlink client"""

    # redirect output to log file:
    sys.stdout = open(logfile, 'a+')
    sys.stderr = sys.stdout

    max_retries = 5
    nsleep = 10 # seconds to wait before retrying

    # set up client
    try:
        server, port = myclient.split(":")
    except ValueError:
        print("Error: Invalid seedlink server format. Please enter as SERVER:PORT")

    port = int(port)
    client = Client(server, port)#,debug=True)

    for _ in range(max_retries):

        try:
        # ... do stuff ...
            print("Connecting to server...")
            sys.stdout.flush()
            # fetch data
            st = client.get_waveforms(scnl["N"], scnl["S"], scnl["L"], scnl["C"], t, t + length)
        except Exception as e:
            # ... log it, sleep, etc. ...
            print('Connection error: '+ str(e))
            print("Will retry in ", str(nsleep), "s")
            sys.stdout.flush()
            time.sleep(nsleep)
            continue
        else:
            break
    else:
        st=None
        print("Can't connect to server. Giving up for now.")

    return st
