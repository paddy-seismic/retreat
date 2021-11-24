"""slink2st3"""
import time
import sys
from obspy.clients.seedlink.basic_client import Client
from obspy import Stream

def multiselect_request(client, multiselect, starttime, endtime):
    """
    Make a multiselect request to underlying seedlink client

    Multiselect string is one or more comma separated
    network/station/location/channel combinations as defined by seedlink
    standard, e.g.
    "NETWORK_STATION:LOCATIONCHANNEL,NETWORK_STATION:LOCATIONCHANNEL"
    where location+channel may contain '?' characters but should be exactly
    5 characters long.

    :rtype: :class:`~obspy.core.stream.Stream`
    """
    client._init_client()
    client._slclient.multiselect = multiselect
    client._slclient.begin_time = starttime
    client._slclient.end_time = endtime
    client._connect()
    client._slclient.initialize()
    client.stream = Stream()
    client._slclient.run(packet_handler=client._packet_handler)
    stream = client.stream
    stream.trim(starttime, endtime)
    client.stream = None
    stream.sort()
    return stream

def slink2st(scnl, scnl_supply, myclient, t, length, logfile):
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
            if not scnl_supply: # SCNL is simple or can be specified using wildcards
                st = client.get_waveforms(scnl["N"], scnl["S"], scnl["L"], scnl["C"], t, t + length)
            else: # SCNL has multiple stations/channels requiring reading a list from file
                # conver list to seedlink "multiselect" format, i.e.
                # "NETWORK_STATION:LOCATIONCHANNEL,NETWORK_STATION:LOCATIONCHANNEL" etc
                multiselect = ""
                for i, myid in enumerate(scnl):
                    if not myid[2]:
                        myid[2] = "  "
                    new_entry = myid[0]+"_"+myid[1]+":"+myid[2]+myid[3]
                    if i > 0:
                        new_entry = ","+new_entry
                    multiselect += new_entry
                st = multiselect_request(client, multiselect, t, t+length)

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
        st = None
        print("Can't connect to server. Giving up for now.")

    return st
