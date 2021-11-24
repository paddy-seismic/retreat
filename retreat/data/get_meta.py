"""get_meta"""
import sys
import os
#from obspy.clients.fdsn import Client
from obspy.clients.fdsn import RoutingClient
from obspy import read_inventory
import numpy as np

def read_ascii_meta(myfile, logfile):
    """retrieves station coordinates ONLY from an ASCII/text file. No other metadata"""
    # redirect output to log file:
    sys.stdout = open(logfile, 'a+')
    sys.stderr = sys.stdout

    # import the coordinates from the given file
    if os.path.isfile(myfile):
        with open(myfile, 'r') as f:
            inv = np.genfromtxt(f, dtype=[('id', 'U16'), ('longitude', '<f8'),\
                    ('latitude', '<f8'), ('elevation', '<f8')])
    else:
        print("Error reading file: ", myfile, " Check your filename is correct")
        raise Exception("Stopping")

    return inv

def read_ascii_scnl(myfile, logfile):
    """retrieves station SEED ids (SCNL) from an ASCII/text file"""
    # redirect output to log file:
    sys.stdout = open(logfile, 'a+')
    sys.stderr = sys.stdout

    # import the coordinates from the given file
    if os.path.isfile(myfile):
        with open(myfile, 'r') as f:
            scnl = np.genfromtxt(f, dtype=str, delimiter=".")
    else:
        print("Error reading file: ", myfile, "Check your filename is correct")
        #raise SystemExit("Stopping")
        raise Exception("Stopping")

    return scnl

def get_meta(mydata, logfile):
    """retrieves relevant network/array/stream metadata from source
    specified in mydata variable"""
    # redirect output to log file:
    sys.stdout = open(logfile, 'a+')
    sys.stderr = sys.stdout

    if mydata["inv_supply"]:
        print("Importing inventory file: ", mydata["inv_file"])
        if mydata["inv_type"] != "ASCII":
            inv = read_inventory(mydata["inv_file"], format=mydata["inv_type"])
        else:
            inv = read_ascii_meta(mydata["inv_file"], logfile)
    else:

        if mydata["connection"] == "FDSN":

            myclient = mydata["myclient"]

            # test/check myclient
            if myclient == "IRIS":
                client = RoutingClient("iris-federator")
            elif myclient == "EIDA":
                client = RoutingClient("eida-routing")
            else:
                print('Error: FDSN client must be "IRIS" or "EIDA"')
                raise Exception("Stopping")

            if not mydata["scnl_supply"]:
                inv = client.get_stations(network=mydata["scnl"]["N"], \
                station=mydata["scnl"]["S"], channel=mydata["scnl"]["C"], \
                location=mydata["scnl"]["L"], level='response')
            else:
                scnl = mydata["scnl"]
                # replace single values with comma separated values
                myN = np.unique(scnl[:, 0])
                if len(myN) > 1:
                    myN = ','.join(np.unique(scnl[:, 0]).astype(str))
                else:
                    myN = myN[0]

                myS = np.unique(scnl[:, 1])
                if len(myS) > 1:
                    myS = ','.join(np.unique(scnl[:, 1]).astype(str))
                else:
                    myS = myS[0]

                myL = np.unique(scnl[:, 2])
                if len(myL) > 1:
                    myL = ','.join(np.unique(scnl[:, 2]).astype(str))
                else:
                    myL = myL[0]

                myC = np.unique(scnl[:, 3])
                if len(myC) > 1:
                    myC = ','.join(np.unique(scnl[:, 3]).astype(str))
                else:
                    myC = myC[0]
                inv = client.get_stations(network=myN, station=myS,\
                    channel=myC, location=myL, level='response')

        else:
            print("No valid inventory specified.")
            raise Exception("Stopping")

    return inv
