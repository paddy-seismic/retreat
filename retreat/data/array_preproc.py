"""array_preproc"""
import sys
#import os
#import glob
#import numpy as np
#import obspy
#from obspy.core.util import AttribDict
#from obspy.core import UTCDateTime
#from obspy import read, read_inventory, Stream
#from obspy.io.xseed import Parser
#import concurrent.futures
#from retreat.tools.processpool import get_nproc
from retreat.data.check_for_gaps import check_for_gaps

def array_preproc(st, inv, preproc, logfile):
    """Performs pre-processing on a stream object and returns processed data"""
    #print('Process p (array_preproc) id: {}'.format(os.getpid()))

    # redirect output to log file:
    sys.stdout = open(logfile, 'a+')
    sys.stderr = sys.stdout

### PRE-PROCESS for array processing

    # select Z comps only
    if preproc["zcomps"]:
        st = st.select(component="Z")
    # now check for gaps
    if preproc["check_gaps"]:
        print("Checking stream for gaps")
        # NB if check_gaps AND demean are selected then demeaning is done by check_for_gaps
        st, gap_status = check_for_gaps(st, preproc["min_nchan"], preproc["max_gap_size"],\
            preproc["max_gap_ends"], preproc["demean"], logfile)
        print(st)
        # get/set end time of stream
        st_end = max([st[i].stats.endtime for i in range(st.count())])
    else:
        # demean not dealt with by gap function - so check and remove mean here
        gap_status = True
        # get/set end time of stream
        st_end = min([st[i].stats.endtime for i in range(st.count())])

        if preproc["demean"]:
            st.detrend("demean")

    sys.stdout.flush()

    if gap_status:
        # proceed with processing - (else: if not enough gap-free channels,
        # then no point in continuing...)

        # pre-filter
        if preproc["prefilt"]:
            fmin = preproc["Fmin"]
            fmax = preproc["Fmax"]
            pre_filt = (0.5*fmin, fmin, fmax, 1.5*fmax)
        else:
            pre_filt = None

        # remove instrument response
        if preproc["removeresponse"]:
            if type(inv).__name__ != "Inventory":
                print("Error. No response information specified in inventory")
                raise StopIteration

            # reponse removal
            print("Starting response removal...")
            st.attach_response(inv)


            for tr in st:
                print(tr.id)
                sys.stdout.flush()
                tr.remove_response(output="VEL", inventory=inv, zero_mean=False, \
                pre_filt=pre_filt, water_level=60)
#                with concurrent.futures.ProcessPoolExecutor(max_workers=get_nproc()) as executor:
#                    executor.submit(tr.remove_response,output="VEL", inventory=inv, \
#                        pre_filt=pre_filt, zero_mean=False, taper=False)

            print("...complete")

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
            # decimate to new sampling rate
            for tr in st:
                factor = int(round(tr.stats.sampling_rate/preproc["newfreq"]))
                tr.decimate(factor)

            # add coordinates
            for tr in st:
                # get lat and lon from inventory:
                seedid = tr.get_id()
                if type(inv).__name__ == "Inventory":

                    # check if any channel info:
                    if inv.get_contents()["channels"]:
                        tr.stats.coordinates = inv.get_coordinates(seedid)
                    else:
                        # try using stations only
                        mystat = tr.id.split(".")[1]
                        tr.stats.coordinates = dict(
                            latitude=inv.select(station=mystat)[0][0].latitude,
                            longitude=inv.select(station=mystat)[0][0].longitude,
                            elevation=inv.select(station=mystat)[0][0].elevation,
                            local_depth=0.0,
                        )
                else:
                    tr.stats.coordinates = dict(
                        latitude=inv[inv["id"] == seedid]["latitude"][0],
                        longitude=inv[inv["id"] == seedid]["longitude"][0],
                        elevation=inv[inv["id"] == seedid]["elevation"][0],
                        local_depth=0.0,
                    )
    else:
        print("Not enough channels without gaps. Skipping stream")

    return st, gap_status, st_end
