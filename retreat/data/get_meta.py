"""get_meta"""
import logging
import sys
from obspy.clients.fdsn import Client
from obspy import read_inventory

def get_meta(mydata, logfile):
    """retrieves relevant network/array/stream metadata from source
    specified in mydata variable"""
    # redirect output to log file:
    sys.stdout = open(logfile, 'a+')
    sys.stderr = sys.stdout

    if mydata["inv_supply"]:
        #parser = Parser(mydata["inv_file"],format='STATIONXML')
        print("Importing inventory file: ", mydata["inv_file"])
        inv = read_inventory(mydata["inv_file"], format=mydata["inv_type"])
    else:

        if mydata["connection"] == "FDSN":
            client = Client(mydata["myclient"])

            inv = client.get_stations(network=mydata["scnl"]["N"], \
            station=mydata["scnl"]["S"], channel=mydata["scnl"]["C"], \
            location=mydata["scnl"]["L"], level='response')

            #parser = None
#           inv.write('my_inventory.xml', format='STATIONXML')

        else:
            print("No valid inventory specified.")
            logging.error("No valid inventory specified.")
            print("Stopping")
            raise SystemExit("Stopping")

    return  inv
