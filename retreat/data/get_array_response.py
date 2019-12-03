"""get_array_response"""
from obspy.signal.array_analysis import array_transff_wavenumber
import numpy as np

def get_array_response(st, inv, array_resp):
    """returns array response and transfer function based on stream object and metadata"""

    # Extract coordinates for Array response function plotting and convert units if needed
    coords = []
    trace = st[0]
    if 'latitude' in trace.stats.coordinates:
        for trace in st:
            coords.append(np.array([trace.stats.coordinates.longitude, trace.stats.coordinates.latitude, trace.stats.coordinates.elevation]))
        coords = np.array(coords)
    else:
        print('no coordinates found in stream')

    if array_resp["elev_in_m"]:
        # convert elevation from m to km
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
