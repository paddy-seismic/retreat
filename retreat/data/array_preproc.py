"""array_preproc"""
import numpy as np
import obspy, glob
from obspy.core.util import AttribDict
from obspy.core import UTCDateTime
from obspy import read, read_inventory, Stream
#from obspy.io.xseed import Parser
import sys, os
#import concurrent.futures
#from processpool import get_nproc

def array_preproc(st, inv, preproc,logfile):
    """Performs pre-processing on a stream object and returns processed data"""
    #print('Process p (array_preproc) id: {}'.format(os.getpid()))

    # redirect output to log file:
    sys.stdout = open(logfile,'a+')
    sys.stderr = sys.stdout

### PRE-PROCESS for array processing

    # select Z comps only
    if preproc["zcomps"]:
        st = st.select(component="Z");

    # pre-filter
    if preproc["prefilt"]:
        fmin = preproc["Fmin"]
        fmax = preproc["Fmax"]
        pre_filt = (0.5*fmin, fmin, fmax, 1.5*fmax)

    # remove instrument response
    if preproc["removeresponse"]:
        # reponse removal

        print("Starting response removal...")

        st.attach_response(inv)

        for tr in st:

            print(tr.id)

            tr.remove_response(output="VEL", inventory=inv, pre_filt=pre_filt, zero_mean=False, taper=False)

#            with concurrent.futures.ProcessPoolExecutor(max_workers=get_nproc()) as executor:
#                #tr = executor.submit(tr.remove_response,output="VEL", inventory=inv, pre_filt=pre_filt, zero_mean=False, taper=False).result()
#                executor.submit(tr.remove_response,output="VEL", inventory=inv, pre_filt=pre_filt, zero_mean=False, taper=False)
        print("...complete")

    # remove mean
    if preproc["demean"]:
        st.detrend("demean")

    # remove trend
    if preproc["linear"]:
        st.detrend("linear")

        # taper
    if preproc["taper"]:
        st.taper(max_percentage=preproc["taper_pc"])

    if preproc["bandpass"]:
        # bandpass filter 
        st.filter("bandpass", freqmin=fmin, freqmax=fmax)

    if preproc["decimate"]:
        # decimate to new samping rate
        for tr in st:
            factor=int(round(tr.stats.sampling_rate/preproc["newfreq"]))
            tr.decimate(factor)    

        # add coordinates
        for tr in st:
            # get lat and lon from inventory:
            seedid = tr.get_id()
            tr.stats.coordinates = inv.get_coordinates(seedid)    
#            # get lat and lon from dataless:
#            seedid = tr.get_id()
#            tr.stats.coordinates = parser.get_coordinates(seedid,datetime=None)
#            
    return st
