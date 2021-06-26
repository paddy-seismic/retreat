"""fdsn2st.py"""
import time
import sys
import numpy as np
from obspy.clients.fdsn import RoutingClient

def fdsn2st(scnl, scnl_supply, myclient, t, length, logfile):
    """
    Fetches a stream object from server using FDSN RoutingClient

    Args:
        scnl (dict): Dictionary containing desired SCNL values for the stream
        myclient (str): Name of client - must be "IRIS" for iris-federator OR
        "EIDA" for the EIDAWS routing web service (default="IRIS")
        t (UTCDateTime): Desired stream start time
        length (float): Desired length of stream in seconds
        logfile (str): name and path to the logfile

    Returns:
        st (stream): obspy stream object containing retrieved data
    """
    # redirect output to log file:
    sys.stdout = open(logfile, 'a+')
    sys.stderr = sys.stdout

    max_retries = 5
    nsleep = 10 # seconds to wait before retrying

    # test/check myclient
    if myclient == "IRIS":
        client = RoutingClient("iris-federator")
    elif myclient == "EIDA":
        client = RoutingClient("eida-routing")
    else:
        print('Error: FDSN client must be "IRIS" or "EIDA"')
        raise Exception("Stopping")

    for _ in range(max_retries):

        try:
            # grab the data
            print("Connecting to server...")
            sys.stdout.flush()

            if not scnl_supply: # simple SCNL list that can be constructed using wildcards
                st = client.get_waveforms(network=scnl["N"], station=scnl["S"], \
                    location=scnl["L"], channel=scnl["C"], starttime=t, endtime=(t + length))
            else: # more complicated list that is read from a file

                # replace single values with comma separated values
                myN = np.unique(scnl[:,0])
                if len(myN) > 1:
                    myN = ','.join(np.unique(scnl[:,0]).astype(str))
                else:
                    myN=myN[0]

                myS = np.unique(scnl[:,1])
                if len(myS) > 1:
                    myS = ','.join(np.unique(scnl[:,1]).astype(str))
                else:
                    myS=myS[0]

                myL = np.unique(scnl[:,2])
                if len(myL) > 1:
                    myL = ','.join(np.unique(scnl[:,2]).astype(str))
                else:
                    myL=myL[0]

                myC = np.unique(scnl[:,3])
                if len(myC) > 1:
                    myC = ','.join(np.unique(scnl[:,3]).astype(str))
                else:
                    myC=myC[0]

                # now fetch data
                print(myN,myS,myL,myC,t,length)
                st = client.get_waveforms(network=myN, station=myS, location=myL, channel=myC,\
                    starttime=t, endtime=(t+length))

        except Exception as e:
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
