"""sds2st3"""
import os
import sys
from obspy.clients.filesystem.sds import Client
from obspy import Stream
from retreat.data.check_for_gaps import merge_checks

def sds2st(scnl, scnl_supply, sds_root, sds_type, customfmt, myfmtstr, t, length, logfile):
    """Fetches stream object from local storage using SDS directory structure"""
    # redirect output to log file:s
    sys.stdout = open(logfile, 'a+')
    sys.stderr = sys.stdout

    # set up client
    client = Client(sds_root, sds_type=sds_type)
    if customfmt:
        print('Using custom directory structure:')
        print(myfmtstr)
        client.FMTSTR = myfmtstr

    # check directory
    if os.path.isdir(sds_root) is False:
        print("Error: sds_root directory does not exist! Please check input")
        raise StopIteration

    print("Retrieving data from filesystem...")

    debug = False

### DEBUGGING
    if debug:
        print("FMTSTR=%s"%client.FMTSTR)
        print("format=%s"%client.format)
        print("sds_root=%s"%client.sds_root)
        print("sds_type=%s"%client.sds_type)
        print("t=", t)
        print("length=", length)
        print("scnl_supply=", scnl_supply)
        print("SCNL=", scnl)
        print(client)
###
    if not scnl_supply: # simple SCNL list that can be constructed using wildcards
        # fetch data
        st = client.get_waveforms(scnl["N"], scnl["S"], scnl["L"], scnl["C"], t, t+length, merge=1)
        if debug:
            #for ii, ss in enumerate(scnl):
            #    print(ii,ss)
            #print(client.get_all_nslc())
            print("has data:", client.has_data(scnl["N"], scnl["S"], scnl["L"], scnl["C"]))
            print(st)
    else: # something more complicated that requires a list read from a file

        # Simply loop over the supplied SEED ids
        # multiple connections to server not an issue as offline read - may be slightly slower
        # but not running in real-time so speed is not as critical
        st = Stream()
        for myid in scnl:
            st_id = client.get_waveforms(myid[0], myid[1], myid[2], myid[3], t, t+length, merge=1)
            if debug:
                #print(client.get_all_nslc())
                for ii, dd in enumerate(myid):
                    print(ii, dd)
                print("has_data: ", client.has_data(myid[0], myid[1], myid[2], myid[3]))
                print(st)
            st += st_id

    # check for empty stream:
    if not st or len(st) < 1:
        print("Error: Stream empty - please check your data source")
        st = None
    else:
        # try to merge any data in multiple traces:
        try:
            st.merge(method=1)
        except Exception as e:
            print("Error merging stream data: ", e)
            print("re-checking traces")
            st = merge_checks(st)
            try:
                st.merge()
            except Exception as e:
                print("Still error merging stream data: ", e)
                st = None

    return st
