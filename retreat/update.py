"""update"""
# import necessary functions
import sys
import gc
import logging
import concurrent.futures
from obspy.signal.array_analysis import array_processing
from retreat.data.fdsn2st3 import fdsn2st
from retreat.data.slink2st3 import slink2st
from retreat.data.sds2st3 import sds2st
from retreat.data.fix_times import fix_times
from retreat.data.get_meta import get_meta
from retreat.data.array_preproc import array_preproc
from retreat.plot.update_plot import update_plot
from retreat.tools.processpool import get_nproc
#import numpy as np
#import datetime
#import time, os
#from multiprocessing import Process, Queue


def update(timing, mydata, preproc, kwargs, to_plot, spectro, array_resp, logfile):
    """Routine to fetch (new) data and update output and figures as necessary"""
    # redirect output to log file:
    sys.stdout = open(logfile, 'a+')
    sys.stderr = sys.stdout

    ##################### get data
    print("\n--------------------------\n")
    if to_plot["first"]:
        print("Fetching initial data")
    else:
        print("Fetching new data")
    global st, t_in, inv

    #### FIRST TIME THROUGH
    if to_plot["first"]:

        if mydata["replay"]: ## REPLAY MODE (LOCAL FILES DATA SOURCE)

            print("Replay mode selected: using local files as data source")

            # No need for backfilling flag
            # just use the given start time and desired plot length - fill the whole window
            tt_in = timing["tstart"]

#            # grab the data

            with concurrent.futures.ProcessPoolExecutor(max_workers=get_nproc()) as executor:
                st_in = executor.submit(sds2st, mydata["scnl"], mydata["sds_root"],\
                mydata["sds_type"], mydata["customfmt"], mydata["myFMTSTR"],\
                tt_in, timing["plot_window"], logfile).result()

#            #########
#            queue=Queue()
#            p = Process(target=mp_worker, name='sds2st', daemon=True, args=(queue, sds2st, \
#            mydata["scnl"],mydata["sds_root"],mydata["sds_type"],mydata["customfmt"],\
#            mydata["myFMTSTR"],tt_in,timing["plot_window"],logfile))
#            p.daemon = True
#            p.start()
#            st_in = queue.get()
#            #########

            #st_in = pool.starmap(sds2st, [ [ mydata["scnl"],mydata["sds_root"],mydata["sds_type"],\
#           mydata["customfmt"],mydata["myFMTSTR"],tt_in,timing["plot_window"],logfile ] ] )

#            st_in =  run_futures(sds2st,(mydata["scnl"],mydata["sds_root"],mydata["sds_type"],\
#                mydata["customfmt"],mydata["myFMTSTR"],tt_in,timing["plot_window"],logfile),30)

            #st_in = sds2st(mydata["scnl"],mydata["sds_root"],mydata["sds_type"],\
#           mydata["customfmt"],mydata["myFMTSTR"],tt_in,timing["plot_window"],logfile)

#                try:
#                    st_in = f.result(timeout=30)
#                except concurrent.futures.TimeoutError:
#                    stop_process_pool(executor)

                #mydata["customfmt"],mydata["myFMTSTR"],tt_in,timing["plot_window"],window).result()

#            print("Replay mode selected: using local files as data source")
#            # remove pre-buffer as for non-realtime source it is unnecessary:
#            tt_in = tt_in + timing["prebuf"]
#            st_in = sds2st(mydata["scnl"],mydata["sds_root"],mydata["sds_type"],\
#            mydata["customfmt"],mydata["myFMTSTR"],tt_in,timing["plot_window"],window)

#            if mydata["replay"]: ## REPLAY MODE (LOCAL FILES DATA SOURCE)

            st_end = min([st_in[i].stats.endtime for i in range(st_in.count())])
            t_in = st_end # - (timing["plot_window"])
#           t_in = mydata["t"]

        else:

        ## REALTIME DATA SOURCE

            # check whether we want to backfill entire plot window
            if timing["fill_on_start"]:

                print("Backfilling..")
                tt_in = mydata["t"] + timing["window_length"] - timing["plot_window"]
                # (NB this already includes prebuffer)

                if mydata["connection"] == "FDSN":
                    #st_in = fdsn2st(mydata["scnl"],mydata["myclient"],tt_in,
                    #timing["plot_window"],logfile)

                    with concurrent.futures.ProcessPoolExecutor(max_workers=get_nproc())\
                    as executor:
                        st_in = executor.submit(fdsn2st, mydata["scnl"], mydata["myclient"],\
                        tt_in, timing["plot_window"], logfile).result()

                elif mydata["connection"] == "seedlink":
                    #st_in = slink2st(mydata["scnl"],mydata["myclient"],
                    #tt_in,timing["plot_window"],logfile)

                    with concurrent.futures.ProcessPoolExecutor(max_workers=get_nproc())\
                    as executor:
                        st_in = executor.submit(slink2st, mydata["scnl"], mydata["myclient"],\
                        tt_in, timing["plot_window"], logfile).result()

                else:
                    logging.error("Invalid datasource specified")
                    print("Invalid datasource specified")

#                t_in = t_in = mydata["t"]
                t_in = mydata["t"]
#                t_in =  timing["tstart"] - ( timing["plot_window"] +
#                st_in = fdsn2st(mydata["scnl"],mydata["myclient"],
#                t_in,timing["plot_window"]+timing["tdiff"])

            else:
                # use current time and window length
                t_in = mydata["t"]
                if mydata["connection"] == "FDSN":
                    #st_in = fdsn2st(mydata["scnl"],mydata["myclient"],t_in,
                    #timing["window_length"],logfile)
                    with concurrent.futures.ProcessPoolExecutor(max_workers=get_nproc())\
                    as executor:
                        st_in = executor.submit(fdsn2st, mydata["scnl"], mydata["myclient"],\
                        t_in, timing["window_length"], logfile).result()

                elif mydata["connection"] == "seedlink":
                    #st_in = slink2st(mydata["scnl"],mydata["myclient"],\
                    #t_in,timing["window_length"],logfile)
                    with concurrent.futures.ProcessPoolExecutor(max_workers=get_nproc())\
                    as executor:
                        st_in = executor.submit(slink2st, mydata["scnl"], mydata["myclient"],\
                        t_in, timing["window_length"], logfile).result()
                else:
                    logging.error("Invalid datasource specified")
                    print("Invalid datasource specified")

    #            print str(datetime.datetime.utcnow())
    #            print "t_in = ", t_in
            print("Initial data:")
            print(st_in)

    else:
    ### APPENDING TO EXISTING DATA

        if mydata["replay"]: ## REPLAY MODE (LOCAL FILES DATA SOURCE)

            print("Replay mode selected: using local files as data source for new data")

#            from IPython.core.debugger import set_trace
#            set_trace()
#            print(type(print))
#            set_trace()

            st_end = min([st[i].stats.endtime for i in range(st.count())])

#            t_in = t_in + timing[""]#timing["update_interval"]#
            t_in = st_end

            #print(t_in)
            st_in = sds2st(mydata["scnl"], mydata["sds_root"], mydata["sds_type"],\
            mydata["customfmt"], mydata["myFMTSTR"], t_in, timing["window_length"], logfile)

            print("New data chunk:")
            print(st_in)

        else: ## REALTIME DATA SOURCE

            # append new start time using window_length

            if timing["fill_on_start"]:
                print("Backfilling... adjusting new window start time")
                t_in = t_in + timing["update_interval"] # - 30 # to ensure overlap
                # check end time to prevent gaps and stop crashes
                st_end = min([st[i].stats.endtime for i in range(st.count())])
                if t_in >= st_end:
                    t_in = st_end - (timing["window_length"] + timing["prebuf"])
    #            else:
    #                t_in = mydata["t"]

                if mydata["connection"] == "FDSN":
                    st_in = fdsn2st(mydata["scnl"], mydata["myclient"],\
                    t_in, timing["window_length"], logfile)
                elif mydata["connection"] == "seedlink":
                    st_in = slink2st(mydata["scnl"], mydata["myclient"],\
                    t_in, timing["window_length"], logfile)
                else:
                    logging.error("Invalid datasource specified")
                    print("Invalid datasource specified")

            else:
                t_in = t_in + timing["update_interval"] # - 30 # to ensure overlap
                # check end time to prevent gaps and stop crashes
                st_end = min([st[i].stats.endtime for i in range(st.count())])
                if t_in >= st_end:
                    t_in = st_end - (timing["window_length"] + timing["prebuf"])

                if mydata["connection"] == "FDSN":
                    st_in = fdsn2st(mydata["scnl"], mydata["myclient"], t_in,\
                    timing["window_length"], logfile)
                elif mydata["connection"] == "seedlink":
                    st_in = slink2st(mydata["scnl"], mydata["myclient"], t_in,\
                    timing["window_length"], logfile)
                else:
                    logging.error("Invalid datasource specified")
                    print("Invalid datasource specified")
            ############
            print("New data chunk:")
            print(st_in)

    if to_plot["first"]:
        if timing["fill_on_start"]: #and not mydata["replay"]:
            print("Stream start time = ", str(tt_in))
#        else:
#            print("chunk start time = ",str(t_in))

        st = st_in
    else:
        print("chunk start time = ", str(t_in))
        st += st_in
        st.merge()

    # trim to ensure it doesn't keep growing
    st_sta = max([st[i].stats.starttime for i in range(st.count())])
    st_end = min([st[i].stats.endtime for i in range(st.count())])

    if (st_end - st_sta) > timing["plot_window"]:
        print("Trimming waveform")
        st.trim(st_end-timing["plot_window"]+0.1, st_end)

    kwargs = fix_times(st, kwargs)

    ###################### get metadata
    if to_plot["first"]:
        #inv = get_meta(mydata,logfile)
        with concurrent.futures.ProcessPoolExecutor(max_workers=get_nproc()) as executor:
            inv = executor.submit(get_meta, mydata, logfile).result()

#        #########
#        queue=Queue()
#        p = Process(target=mp_worker, name='getmeta', args=(queue, get_meta, mydata,logfile))
#        p.daemon = True
#        print('1')
#        p.start()
#        if p.exception:
#            print('EXCEPTION')
#        print('2')
#        inv = queue.get()
#        print('3')
#        p.join(timeout=1.0)

#        #########

    print("Data stream to process and plot:")
    print(st)

    ###################### pre-process
    print("Pre-processing data")

    st_loop = st.copy()

    with concurrent.futures.ProcessPoolExecutor(max_workers=get_nproc()) as executor:
        st_loop = executor.submit(array_preproc, st_loop, inv, preproc, logfile).result()
    #st_loop = array_preproc(st_loop,inv,preproc,logfile)

    ###################### array processing

    print("Updating array results")

    global array_results
#    ########
#    queue=Queue()
#    p = Process(target=mp_worker_d, name='array_processing',\
#    daemon=True, args=(queue, array_processing, st_loop, kwargs))
#    p.daemon = True
#    p.start()
#    print('Process p (array_processing) id: {}'.format(p.pid))
#    array_results = queue.get()
#    #########

    #array_results = array_processing(st_loop, **kwargs);

    with concurrent.futures.ProcessPoolExecutor(max_workers=get_nproc()) as executor:
        array_results = executor.submit(array_processing, st_loop, **kwargs).result()

#    array_results_loop = array_processing(st_loop, **kwargs);

#    if to_plot["first"]:
#        array_results = array_results_loop
#    else:
#        if to_plot["no_overlap"]:
#            # only append "newer" values at later times than currently exist
#            array_results_loop = array_results_loop[(array_results_loop[:,0] >
#        array_results[-1,0]).nonzero()]
#        # append new values to end of existing array
#        array_results = np.append(array_results,array_results_loop,axis=0)

#        #print([i for i in set(array_results) if array_results.count(i) > 1])

    ###################### update plot
    print("Updating plots")

    update_plot(st_loop, array_results, to_plot, spectro, inv, array_resp, logfile)

    #raise StopIteration

    # cleanup
    del st_loop, st_in, array_resp
    gc.collect()
    del gc.garbage[:]
    gc.collect()

#    if not mydata["replay"]:
#        time.sleep(3)
#        print("Waiting {:.0f}s for next update...".format(timing["update_interval"]))

    # RESET STDOUT/ERR to flush and print commands
    # redirect output to log file:
    sys.stdout = open(logfile, 'a+')
    sys.stderr = sys.stdout

    return st_end
