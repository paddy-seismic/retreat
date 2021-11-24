"""update"""
# import necessary functions
import sys
import gc
import concurrent.futures
from obspy.signal.array_analysis import array_processing
from retreat.data.beamforming_lsqr import do_inversion
#from retreat.data.fdsn2st3 import fdsn2st
from retreat.data.fdsn2st import fdsn2st
from retreat.data.slink2st3 import slink2st
from retreat.data.sds2st3 import sds2st
from retreat.data.ew2st import ew2st
from retreat.data.fix_times import fix_times
from retreat.data.get_meta import get_meta
from retreat.data.get_meta import read_ascii_scnl
from retreat.data.array_preproc import array_preproc
from retreat.data.check_for_gaps import merge_checks
from retreat.data.get_nth import get_nth
from retreat.plot.update_plot2 import update_plot
from retreat.tools.processpool import get_nproc

def update(timing, mydata, preproc, kwargs, to_plot, spectro, array_resp, logfile, st_end, narrays):
    """Routine to fetch (new) data and update output and figures as necessary"""
    # redirect output to log file:
    sys.stdout = open(logfile, 'a+')
    sys.stderr = sys.stdout
    sys.stdout.flush()

    #narrays=2 # two array case assumed here for now
    # counter for no data from each array
    no_data = 0

    # process SCNLs
    scnls = mydata["scnl"]
    scnls_supply = mydata["scnl_supply"]

  #  print('scnls top:', scnls)
 #   print(mydata)

    ##################### get data
    print("\n--------------------------\n")
    if to_plot["first"]:
        print("Fetching initial data")

        # replace SCNL if reading from a file:
        for n, supply in enumerate(scnls_supply):
            if supply:
                newscnl = read_ascii_scnl(mydata["scnl_file"][n], logfile)
                scnls[n] = newscnl

        mydata["scnl"] = scnls

    else:
        print("Fetching new data")
    global st, t_in, inv

    ### FIRST TIME THROUGH
    if to_plot["first"]:

        if mydata["replay"]: ## REPLAY MODE (LOCAL FILES DATA SOURCE)

            print("Replay mode selected: using local files as data source")

            # No need for backfilling   flag
            # just use the given start time and desired plot length - fill the whole window
            tt_in = timing["tstart"]

#            # grab the data
            st_in = [] # create empty lists
            st_end = []

            for n in range(narrays):

                with concurrent.futures.ProcessPoolExecutor(max_workers=get_nproc()) as executor:
                    st_ins = executor.submit(sds2st, scnls[n], scnls_supply[n],\
                    mydata["sds_root"][n], mydata["sds_type"][n], mydata["customfmt"][n], \
                        mydata["myFMTSTR"][n],\
                    tt_in, timing["plot_window"], logfile).result()
                try:
                    st_ends = min([st_ins[i].stats.endtime for i in range(st_ins.count())])
                except Exception as e:
                    print("Error retrieving data. Check input source")

                st_in.append(st_ins)
                st_end.append(st_ends)

            t_in = min(st_end)

        else:

        ## REALTIME DATA SOURCE

            # check whether we want to backfill entire plot window
            if timing["fill_on_start"]:

                print("Backfilling..")
                tt_in = mydata["t"] + timing["window_length"] - timing["plot_window"]
                # (NB this already includes prebuffer)

                st_in = [] # create empty list
                for n in range(narrays):

                    if mydata["connection"] == "FDSN":

                        with concurrent.futures.ProcessPoolExecutor(max_workers=get_nproc())\
                        as executor:
                            st_ins = executor.submit(fdsn2st, scnls[n], scnls_supply[n],\
                            mydata["myclient"][n], tt_in, timing["plot_window"], logfile).result()

                    elif mydata["connection"] == "seedlink":

                        with concurrent.futures.ProcessPoolExecutor(max_workers=get_nproc())\
                        as executor:
                            st_ins = executor.submit(slink2st, scnls[n], scnls_supply[n],\
                                mydata["myclient"][n], tt_in, timing["plot_window"], \
                                    logfile).result()

                    elif mydata["connection"] == "earthworm":

                        with concurrent.futures.ProcessPoolExecutor(max_workers=get_nproc())\
                        as executor:
                            st_ins = executor.submit(ew2st, scnls[n], scnls_supply[n],\
                                mydata["myclient"][n], tt_in, timing["plot_window"], \
                                    logfile).result()

                    else:
                        raise Exception("Invalid datasource specified")

                    st_in.append(st_ins)

                t_in = mydata["t"]

            else:
                # use current time and window length
                t_in = mydata["t"]

                st_in = [] # create empty list
                for n in range(narrays):

                    if mydata["connection"] == "FDSN":
                        with concurrent.futures.ProcessPoolExecutor(max_workers=get_nproc())\
                        as executor:
                            st_ins = executor.submit(fdsn2st, scnls[n], scnls_supply[n],\
                            mydata["myclient"][n], t_in, timing["window_length"], logfile).result()

                    elif mydata["connection"] == "seedlink":
                        with concurrent.futures.ProcessPoolExecutor(max_workers=get_nproc())\
                        as executor:
                            st_ins = executor.submit(slink2st, scnls[n], scnls_supply[n],\
                                mydata["myclient"][n], t_in, timing["window_length"], \
                                    logfile).result()

                    elif mydata["connection"] == "earthworm":
                        with concurrent.futures.ProcessPoolExecutor(max_workers=get_nproc())\
                        as executor:
                            st_ins = executor.submit(ew2st, scnls[n], scnls_supply[n],\
                                mydata["myclient"][n], t_in, timing["window_length"], \
                                    logfile).result()
                    else:
                        raise Exception("Invalid datasource specified")

                    if not st_ins:
                        no_data = no_data + 1
                        if no_data >= narrays:
                            raise Exception("No data found. Please check your source.")

                    st_in.append(st_ins)

            print("Initial data:")
            for stream in st_in:
                print(stream)

    else:
    ### APPENDING TO EXISTING DATA

        if mydata["replay"]: ## REPLAY MODE (LOCAL FILES DATA SOURCE)

            print("Replay mode selected: using local files as data source for new data")

            t_in = st_end

            st_in = [] # create empty lists
            #st_end = []
            for n in range(narrays):

                st_ins = sds2st(scnls[n], scnls_supply[n], mydata["sds_root"][n],\
                    mydata["sds_type"][n], mydata["customfmt"][n], mydata["myFMTSTR"][n], \
                    t_in, timing["window_length"], logfile)

                if not st_ins:
                    print("No data found", n)
                    no_data = no_data + 1
                    st_end = st_end + timing["window_length"] # advance end by the window length
                    # Will continue indefinitely unless more data found, OR end time is specified:
                    if timing["tstop"]:
                        print("End time specified, checking stream")
                        if st_end >= timing["tstop"]:
                            raise Exception("End time exceeded. Stopping.")
                        else:
                            print("Skipping array ", n+1)
                            #narrays=narrays-1
                    if no_data >= narrays:
                        return st_end

                if st_ins:
                # check if at the end of the available data:
                    if max(len(tr.data) for tr in st_ins) < 2 or max(tr.stats.endtime \
                        for tr in st_ins) <= max(tr.stats.endtime for tr in st[n]):
                        # i.e. new chunk has only 1 sample, or its endtime is the same or less than
                        # that of the current stream
                        no_data = no_data + 1
                        print("n, no_data, narrays=", n, no_data, narrays)
                        print(st_ins)
                        print(max(len(tr.data) for tr in st_ins))
                        print(max(tr.stats.endtime for tr in st_ins))
                        print(max(tr.stats.endtime for tr in st[n]))
                        if no_data >= narrays:
                            print("End of data, skipping")
                            st_end = st_end + 1 # advance end by 1 second to skip
                            return st_end

                st_in.append(st_ins)

            print("New data chunks:")
            for stream in st_in:
                print(stream)

        else: ## REALTIME DATA SOURCE

            # append new start time using window_length

            if timing["fill_on_start"]:
                print("Backfilling... adjusting new window start time")
                t_in = t_in + timing["update_interval"] # - 30 # to ensure overlap

                # check end time to prevent gaps and stop crashes
                #st_end = min([st[i].stats.endtime for i in range(st.count())])

                if t_in >= st_end:
                    t_in = st_end - (timing["window_length"] + timing["prebuf"])

                st_in = [] # create empty list
                for n in range(narrays):

                    if mydata["connection"] == "FDSN":
                        st_ins = fdsn2st(scnls[n], scnls_supply[n],\
                        mydata["myclient"][n], t_in, timing["window_length"], logfile)

                    elif mydata["connection"] == "seedlink":
                        st_ins = slink2st(scnls[n], scnls_supply[n],\
                        mydata["myclient"][n], t_in, timing["window_length"], logfile)

                    elif mydata["connection"] == "earthworm":
                        st_ins = ew2st(scnls[n], scnls_supply[n],\
                        mydata["myclient"][n], t_in, timing["window_length"], logfile)

                    else:
                        raise Exception("Invalid datasource specified")

                    st_in.append(st_ins)

            else:
                t_in = t_in + timing["update_interval"] # - 30 # to ensure overlap

                # check end time to prevent gaps and stop crashes
                #st_end = min([st[i].stats.endtime for i in range(st.count())])

                if t_in >= st_end:
                    t_in = st_end - (timing["window_length"] + timing["prebuf"])

                st_in = [] # create empty list
                for n in range(narrays):

                    if mydata["connection"] == "FDSN":
                        st_ins = fdsn2st(scnls[n], scnls_supply[n],\
                        mydata["myclient"][n], t_in, timing["window_length"], logfile)
                    elif mydata["connection"] == "seedlink":
                        st_ins = slink2st(scnls[n], scnls_supply[n],\
                        mydata["myclient"][n], t_in, timing["window_length"], logfile)
                    elif mydata["connection"] == "earthworm":
                        st_ins = ew2st(scnls[n], scnls_supply[n],\
                        mydata["myclient"][n], t_in, timing["window_length"], logfile)

                    else:
                        raise Exception("Invalid datasource specified")

                    if not st_ins:
                        print("No data found")
                        no_data = no_data + 1
                        st_end = st_end + timing["window_length"] # advance end by the window length
                        # Will continue trying indefinitely until more data found..
                        # or stopped manually
                        if no_data >= narrays:
                            return st_end

                    st_in.append(st_ins)

            ############
            print("New data chunks:")
            for stream in st_in:
                print(stream)

    if to_plot["first"]:
        if timing["fill_on_start"]: #and not mydata["replay"]:
            print("Stream start time = ", str(tt_in))

        st = st_in
    else:
        print("chunk start time = ", str(t_in))

        for n in range(narrays):
            if st_in[n]:
                st[n] += st_in[n]
                # use try/catch so (hopefully) we can continue if merging fails...
                try:
                    st[n].merge()
                except Exception as e:
                    print("Error merging stream data: ", e)
                    print("re-checking traces")
                    st[n] = merge_checks(st[n])
                    try:
                        st[n].merge()
                    except Exception as e:
                        print("Still error merging stream data: ", e)
                        st_end = st_end + timing["window_length"] # advance end by the window length
                        return st_end
    stimes = []
    etimes = []

    st_stas = []
    st_ends = []
    #for n, sti in enumerate(st):
    for n in range(narrays):
        sti = st[n]
        # trim to ensure it doesn't keep growing
        #st_sta = max([st[i].stats.starttime for i in range(st.count())])
        #st_end = min([st[i].stats.endtime for i in range(st.count())])
#        st_sta = min([tr.stats.starttime for tr in sti])
#        st_end = max([tr.stats.endtime for tr in sti])
        st_stas.append(min([tr.stats.starttime for tr in sti]))
        st_ends.append(max([tr.stats.endtime for tr in sti]))

        if (st_ends[n] - st_stas[n]) > timing["plot_window"]:
            print("Trimming waveform, Array", n+1)
            sti.trim(st_ends[n]-timing["plot_window"]+0.1, st_ends[n])

        kwargsn = get_nth(kwargs, n)
        dummyw = fix_times(sti, kwargsn)
        stimes.append(dummyw['stime'])
        etimes.append(dummyw['etime'])

    st_sta = min(st_stas)
    st_end = max(st_ends)

    #print("st_ends=",st_ends)
    #print("st_end=",st_end)

    kwargs['stime'] = stimes
    kwargs['etime'] = etimes

    sys.stdout.flush()

    ###################### get metadata
    if to_plot["first"]:
        inv = []
        for n in range(narrays):
            array_mydata = get_nth(mydata, n)
            with concurrent.futures.ProcessPoolExecutor(max_workers=get_nproc()) as executor:
                inv.append(executor.submit(get_meta, array_mydata, logfile).result())

    print("Data stream to process and plot:")
    for n, sti in enumerate(st):
        print('Array', n+1)
        print(sti)

    ###################### pre-process
    print("Pre-processing data")

    st_loop = []
    global array_results
    array_results = []
    gap_status = []

    st_ends = []
    for n, sti in enumerate(st):
        print('Array', n+1)
        st_loops = sti.copy()
        preproc_n = get_nth(preproc, n)
        kwargsn = get_nth(kwargs, n)

        with concurrent.futures.ProcessPoolExecutor(max_workers=get_nproc()) as executor:
            #st_loop = executor.submit(array_preproc, st_loop, inv, preproc, logfile).result()
            st_loops, gap_stat, st_endn = executor.submit(array_preproc, st_loops, \
                inv[n], preproc_n, logfile).result()

        st_loop.append(st_loops)
        gap_status.append(gap_stat)
        st_ends.append(st_endn)

        if gap_status[n]:
            ###################### array processing

            print("Updating array results")

            if array_resp["lsq"][n]: # Use least-squares inversion/beamforming (infrasound)
                print("Using Least-Square inversion for beamforming instead of f-k")
                with concurrent.futures.ProcessPoolExecutor(max_workers=get_nproc()) as executor:
                    array_resultsi = executor.submit(do_inversion, st_loop[n], **kwargsn).result()
            else: # standard obspy f-k (DEFAULT)
                print('Starting f-k')
                with concurrent.futures.ProcessPoolExecutor(max_workers=get_nproc()) as executor:
                    array_resultsi = executor.submit(array_processing, st_loop[n],\
                        **kwargsn).result()

            array_results.append(array_resultsi)
    #
    st_end = max(st_ends)

    # reset narrays based on gap_status:
    if sum(gap_status) < 1:
        narrays = None
    else:
        narrays = sum(gap_status)

    #print("gap_status, narrays=",gap_status,narrays)

    ###################### update plot
    print("Updating plots")

    update_plot(st_loop, array_results, kwargs, to_plot, spectro, inv, array_resp, narrays, logfile)

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

    #print("st_end=",st_end)
    return st_end
