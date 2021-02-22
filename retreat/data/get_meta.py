"""get_meta"""
import sys
import os
from obspy.clients.fdsn import Client
from obspy import read_inventory
import numpy as np

def read_ascii_meta(myfile, logfile):
    """retrieves station coordinates ONLY from an ASCII file. No other metadata"""
    # redirect output to log file:
    sys.stdout = open(logfile, 'a+')
    sys.stderr = sys.stdout

    # import the coordinates from the given file
    if os.path.isfile(myfile):
        with open(myfile, 'r') as f:
            inv = np.genfromtxt(f, dtype=[('id', 'U16'), ('longitude', '<f8'),\
                    ('latitude', '<f8'), ('elevation', '<f8')])
    else:
        print("Error reading file: ",myfile," Check your filename is correct")
        raise SystemExit("Stopping")

    return inv

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
            client = Client(mydata["myclient"])

            inv = client.get_stations(network=mydata["scnl"]["N"], \
            station=mydata["scnl"]["S"], channel=mydata["scnl"]["C"], \
            location=mydata["scnl"]["L"], level='response')

        else:
            print("No valid inventory specified.")
            raise Exception("Stopping")

    return  inv
