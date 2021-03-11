"""ew2st"""
import time
import sys
import regex as re
import numpy as np
from obspy.clients.earthworm import Client
from obspy.clients.earthworm.waveserver import get_menu
from obspy import Stream

def ew2st(scnl_in, scnl_supply, myclient, t, length, logfile):
    """fetches stream object from server using Earthworm/Winston client"""

    # redirect output to log file:
    sys.stdout = open(logfile, 'a+')
    sys.stderr = sys.stdout

    max_retries = 5
    nsleep = 10 # seconds to wait before retrying

    # check server/port input is valid:
    try:
        server, port = myclient.split(":")
        if not isinstance(port,int):
            port=int(port)
    except ValueError:
        print("Error: Invalid server format. Please enter as 'SERVER:PORT'")

    client = Client(server, port)

    ### use call to get_menu to check channels and process (any) wildcard(s)

    chans=[]

    # call getmenu for server and store results:
    for _ in range(max_retries):
        try:
            print("Retrieving channel list from server...")
            sys.stdout.flush()
            chans = np.array(get_menu(server,port))
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

    # condense to scnl only
    chans = chans[:,1:5]
    shrunk=chans
    
    if not scnl_supply: # simple SCNL or can create list using wildcards:
        # check scnl for wildcards and create list of matching channels
        pos=[2,0,3,1]
        order_to_process = ("N","S","L","C")

        for ii, key in enumerate(order_to_process):
            if '*' in scnl_in[key] or '?' in scnl_in[key]:
                # replace wildcards with python regex values
                val = re.sub('\*','.+',scnl_in[key])
                val = re.sub('\?','.',val)
                reg = re.compile(val)
            else:
                reg = re.compile(scnl_in[key])
                try:
                    shrunk = shrunk[np.array([bool(re.match(reg, mystr)) for mystr \
                        in shrunk[:,pos[ii]]])]
                except Exception as e:
                    print('Channel error: '+ str(e))
    else: # more complicated SCNL list - requiring read from file
        # reorder columns:
        scnl_in = scnl_in[:, [1, 3, 0, 2]]
        # find overlap/intersection between the two arrays using sets:
        shrunk = np.array(list(set((tuple(i) for i in scnl_in)).intersection(set((tuple(i) for i in shrunk)))))

    if len(shrunk) < 1:
        raise Exception('Error: channels missing on server, check input')

    # initialise empty stream object
    st = Stream()

    for _ in range(max_retries):

        try:
            for row in shrunk:
                # append new channels
                try:
                    print("Connecting to server and fetching data...")
                    sys.stdout.flush()
                    st.append(client.get_waveforms(row[2], row[0], row[3], row[1],\
                        t, t + length)[0])
                except Exception as e:
                    print('Error fetching data:','.'.join(row))
                    print(str(e))
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
