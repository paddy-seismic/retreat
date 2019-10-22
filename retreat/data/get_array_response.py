"""get_array_response"""
#import obspy
#from obspy.clients.fdsn import Client
#from obspy.imaging.cm import obspy_sequential
from obspy.signal.array_analysis import array_transff_wavenumber
#from obspy.core import UTCDateTime
import numpy as np
#import matplotlib.pyplot as plt

def get_array_response(st, inv, array_resp):
    """returns array response and transfer function based on stream object and metadata"""
    # get arguments
#    scnl = array_resp["scnl"]
#    myclient = array_resp["myclient"]
    #client = Client(myclient)

#    print(st)
#    print(inv)
#    print(array_resp)

    # Process coordinates
    coords = []
    # grab from channels
    for tr in st:
        coords.append([
            inv.get_coordinates(tr.get_id(), tr.stats.starttime)["longitude"],
            inv.get_coordinates(tr.get_id(), tr.stats.starttime)["latitude"],
            inv.get_coordinates(tr.get_id(), tr.stats.starttime)["elevation"],
        ])
    # convert list to array
    coords = np.array(coords)

    if array_resp["elev_in_m"]:
        # convert elevation from km to m
        coords[:, 2] /= 1000.

    # set limits for wavenumber differences to analyze
    klim = array_resp["klim"]
    kxmin = -klim
    kxmax = klim
    kymin = -klim
    kymax = klim
    kstep = klim / array_resp["kstep_factor"]

    # compute transfer function as a function of wavenumber difference
    transff = array_transff_wavenumber(coords, klim, kstep, coordsys='lonlat')

    return transff, kxmin, kxmax, kymin, kymax, kstep
