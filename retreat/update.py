"""update"""
# import necessary functions
import sys
import gc
import concurrent.futures
from obspy.signal.array_analysis import array_processing
from retreat.data.beamforming_lsqr import do_inversion
from retreat.data.fdsn2st3 import fdsn2st
from retreat.data.slink2st3 import slink2st
from retreat.data.sds2st3 import sds2st
from retreat.data.ew2st import ew2st
from retreat.data.fix_times import fix_times
from retreat.data.get_meta import get_meta
from retreat.data.get_meta import read_ascii_scnl
from retreat.data.array_preproc import array_preproc
from retreat.data.check_for_gaps import merge_checks
from retreat.plot.update_plot import update_plot
from retreat.tools.processpool import get_nproc

def update(timing, mydata, preproc, kwargs, to_plot, spectro, array_resp, logfile, st_end):
    """Routine to fetch (new) data and update output and figures as necessary"""
    # redirect output to log file:
    sys.stdout = open(logfile, 'a+')
    sys.stderr = sys.stdout
    sys.stdout.flush()

    ##################### get data
    print("\n--------------------------\n")
    if to_plot["first"]:
        print("Fetching initial data")
        
        # replace SCNL if reading from a file:
        if mydata["scnl_supply"]:
            mydata["scnl"] = read_ascii_scnl(mydata["scnl_file"], logfile)
        
    else:
        print("Fetching new data")
    global st, t_in, inv

    ### FIRST TIME THROUGH
    if to_plot["first"]:

        if mydata["replay"]: ## REPLAY MODE (LOCAL FILES DATA SOURCE)

            print("Replay mode selected: using local files as data source")

            # No need for backfilling flag
            # just use the given start time and desired plot length - fill the whole window
            tt_in = timing["tstart"]

#            # grab the data

            with concurrent.futures.ProcessPoolExecutor(max_workers=get_nproc()) as executor:
                st_in = executor.submit(sds2st, mydata["scnl"], mydata["scnl_supply"],\
                mydata["sds_root"], mydata["sds_type"], mydata["customfmt"], mydata["myFMTSTR"],\
                tt_in, timing["plot_window"], logfile).result()
            try:
                st_end = min([st_in[i].stats.endtime for i in range(st_in.count())])
            except Exception as e:
                print("Error retrieving data. Check input source")
            t_in = st_end

        else:

        ## REALTIME DATA SOURCE

            # check whether we want to backfill entire plot window
            if timing["fill_on_start"]:

                print("Backfilling..")
                tt_in = mydata["t"] + timing["window_length"] - timing["plot_window"]
                # (NB this already includes prebuffer)

                if mydata["connection"] == "FDSN":

                    with concurrent.futures.ProcessPoolExecutor(max_workers=get_nproc())\
                    as executor:
                        st_in = executor.submit(fdsn2st, mydata["scnl"], mydata["scnl_supply"],\
                        mydata["myclient"], tt_in, timing["plot_window"], logfile).result()

                elif mydata["connection"] == "seedlink":

                    with concurrent.futures.ProcessPoolExecutor(max_workers=get_nproc())\
                    as executor:
                        st_in = executor.submit(slink2st, mydata["scnl"], mydata["scnl_supply"],\
                            mydata["myclient"], tt_in, timing["plot_window"], logfile).result()

                elif mydata["connection"] == "earthworm":

                    with concurrent.futures.ProcessPoolExecutor(max_workers=get_nproc())\
                    as executor:
                        st_in = executor.submit(ew2st, mydata["scnl"], mydata["scnl_supply"],\
                            mydata["myclient"], tt_in, timing["plot_window"], logfile).result()

                else:
                    raise Exception("Invalid datasource specified")

                t_in = mydata["t"]

            else:
                # use current time and window length
                t_in = mydata["t"]

                if mydata["connection"] == "FDSN":
                    with concurrent.futures.ProcessPoolExecutor(max_workers=get_nproc())\
                    as executor:
                        st_in = executor.submit(fdsn2st, mydata["scnl"], mydata["scnl_supply"],\
                        mydata["myclient"], t_in, timing["window_length"], logfile).result()

                elif mydata["connection"] == "seedlink":
                    with concurrent.futures.ProcessPoolExecutor(max_workers=get_nproc())\
                    as executor:
                        st_in = executor.submit(slink2st, mydata["scnl"], mydata["scnl_supply"],\
                            mydata["myclient"], t_in, timing["window_length"], logfile).result()

                elif mydata["connection"] == "earthworm":
                    with concurrent.futures.ProcessPoolExecutor(max_workers=get_nproc())\
                    as executor:
                        st_in = executor.submit(ew2st, mydata["scnl"], mydata["scnl_supply"],\
                            mydata["myclient"], t_in, timing["window_length"], logfile).result()
                else:
                    raise Exception("Invalid datasource specified")

            if not st_in:
                raise Exception("No data found. Please check your source.")

            print("Initial data:")
            print(st_in)

    else:
    ### APPENDING TO EXISTING DATA

        if mydata["replay"]: ## REPLAY MODE (LOCAL FILES DATA SOURCE)

            print("Replay mode selected: using local files as data source for new data")

            t_in = st_end

            st_in = sds2st(mydata["scnl"], mydata["scnl_supply"], mydata["sds_root"],\
                mydata["sds_type"], mydata["customfmt"], mydata["myFMTSTR"], \
                t_in, timing["window_length"], logfile)

            if not st_in:
                print("No data found")
                st_end = st_end + timing["window_length"] # advance end by the window length
                # Will continue indefinitely unless more data found, OR end time is specified:
                if timing["tstop"]:
                    print("End time specified, checking stream")
                    if st_end >= timing["tstop"]:
                        raise Exception("End time exceeded. Stopping.")
                return st_end

            # check if at the end of the available data:
            if max(len(tr.data) for tr in st_in) < 2 or max(tr.stats.endtime for tr in st_in) \
                    <= max(tr.stats.endtime for tr in st):
                # i.e. new chunk has only 1 sample, or its endtime is the same or less than
                # that of the current stream
                print("End of data, skipping")
                st_end = st_end + 1 # advance end by 1 second to skip
                return st_end

            print("New data chunk:")
            print(st_in)

        else: ## REALTIME DATA SOURCE

            # append new start time using window_length

            if timing["fill_on_start"]:
                print("Backfilling... adjusting new window start time")
                t_in = t_in + timing["update_interval"] # - 30 # to ensure overlap

                # check end time to prevent gaps and stop crashes
                #st_end = min([st[i].stats.endtime for i in range(st.count())])

                if t_in >= st_end:
                    t_in = st_end - (timing["window_length"] + timing["prebuf"])

                if mydata["connection"] == "FDSN":
                    st_in = fdsn2st(mydata["scnl"], mydata["scnl_supply"],\
                    mydata["myclient"],t_in, timing["window_length"], logfile)
                    
                elif mydata["connection"] == "seedlink":
                    st_in = slink2st(mydata["scnl"], mydata["scnl_supply"],\
                    mydata["myclient"],t_in, timing["window_length"], logfile)
                    
                elif mydata["connection"] == "earthworm":
                    st_in = ew2st(mydata["scnl"], mydata["scnl_supply"],\
                    mydata["myclient"],t_in, timing["window_length"], logfile)

                else:

                    raise Exception("Invalid datasource specified")

            else:
                t_in = t_in + timing["update_interval"] # - 30 # to ensure overlap

                # check end time to prevent gaps and stop crashes
                #st_end = min([st[i].stats.endtime for i in range(st.count())])

                if t_in >= st_end:
                    t_in = st_end - (timing["window_length"] + timing["prebuf"])

                if mydata["connection"] == "FDSN":
                    st_in = fdsn2st(mydata["scnl"], mydata["scnl_supply"],\
		    mydata["myclient"], t_in, timing["window_length"], logfile)
                elif mydata["connection"] == "seedlink":
                    st_in = slink2st(mydata["scnl"], mydata["scnl_supply"],\
                    mydata["myclient"], t_in, timing["window_length"], logfile)
                elif mydata["connection"] == "earthworm":
                    st_in = ew2st(mydata["scnl"], mydata["scnl_supply"],\
                    mydata["myclient"], t_in, timing["window_length"], logfile)

                else:
                    raise Exception("Invalid datasource specified")

            if not st_in:
                print("No data found")
                st_end = st_end + timing["window_length"] # advance end by the window length
                # Will continue trying indefinitely until more data found.. or stopped manually
                return st_end

            ############
            print("New data chunk:")
            print(st_in)

    if to_plot["first"]:
        if timing["fill_on_start"]: #and not mydata["replay"]:
            print("Stream start time = ", str(tt_in))

        st = st_in
    else:
        print("chunk start time = ", str(t_in))
        st += st_in
        # use try/catch so (hopefully) we can continue if merging fails...
        try:
            st.merge()
        except Exception as e:
            print("Error merging stream data: ",e)
            print("re-checking traces")
            st = merge_checks(st)
            try:
                st.merge()
            except Exception as e:
                print("Still error merging stream data: ",e)
                st_end = st_end + timing["window_length"] # advance end by the window length
                return st_end

    # trim to ensure it doesn't keep growing
    #st_sta = max([st[i].stats.starttime for i in range(st.count())])
    #st_end = min([st[i].stats.endtime for i in range(st.count())])
    st_sta = min([tr.stats.starttime for tr in st])
    st_end = max([tr.stats.endtime for tr in st])

    if (st_end - st_sta) > timing["plot_window"]:
        print("Trimming waveform")
        st.trim(st_end-timing["plot_window"]+0.1, st_end)

    kwargs = fix_times(st, kwargs)

    sys.stdout.flush()

    ###################### get metadata
    if to_plot["first"]:
        with concurrent.futures.ProcessPoolExecutor(max_workers=get_nproc()) as executor:
            inv = executor.submit(get_meta, mydata, logfile).result()

    print("Data stream to process and plot:")
    print(st)

    ###################### pre-process
    print("Pre-processing data")

    st_loop = st.copy()

    with concurrent.futures.ProcessPoolExecutor(max_workers=get_nproc()) as executor:
        #st_loop = executor.submit(array_preproc, st_loop, inv, preproc, logfile).result()
        st_loop, gap_status, st_end = executor.submit(array_preproc, st_loop, inv, preproc,\
            logfile).result()

    if gap_status:
        ###################### array processing

        print("Updating array results")

        global array_results

        if array_resp["lsq"]: # Use least-squares inversion/beamforming (infrasound)
            print("Using Least-Square inversion for beamforming instead of f-k")
            with concurrent.futures.ProcessPoolExecutor(max_workers=get_nproc()) as executor:
                array_results = executor.submit(do_inversion, st_loop, **kwargs).result()
        else: # standard obspy f-k (DEFAULT)
            with concurrent.futures.ProcessPoolExecutor(max_workers=get_nproc()) as executor:
                array_results = executor.submit(array_processing, st_loop, **kwargs).result()

        ###################### update plot
        print("Updating plots")

        update_plot(st_loop, array_results, kwargs, to_plot, spectro, inv, array_resp, logfile)

    # cleanup
    del st_loop, st_in, array_resp
    gc.collect()
    del gc.garbage[:]
    gc.collect()

    # RESET STDOUT/ERR to flush and print commands
    # redirect output to log file:
    sys.stdout = open(logfile, 'a+')
    sys.stderr = sys.stdout
    sys.stdout.flush()

    return st_end
