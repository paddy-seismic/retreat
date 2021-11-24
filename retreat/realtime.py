"""realtime"""
# import necessary functions
import time
import sys
import gc
from retreat.tools.time_to_wait import time_to_wait
from retreat.gui.get_param_gui import get_param, get_param2

def realtime(gui_input, logfile, narrays, cmd):
    """Performs an update based on input from the GUI.
    Fetches data, performs processing and updates output."""

    # redirect output to log file:
    sys.stdout = open(logfile, 'a+')
    sys.stderr = sys.stdout

    print("#####################################")
    print("Starting logging: "+ time.strftime('%Y-%m-%d %H:%M:%S'))

    ## get input parameters
    print("Fetching parameters")
    #print(gui_input)

    if narrays:
        timing, mydata, preproc, kwargs, to_plot, spectro, array_resp = \
            get_param2(gui_input, narrays, cmd)
        from retreat.update2 import update
        #update = update2
    else:
        timing, mydata, preproc, kwargs, to_plot, spectro, array_resp = \
            get_param(gui_input)
        from retreat.update import update
        narrays = None

    true_realtime = True
    if (time.time() - timing["tstart"].timestamp) > 10: # arbitrary 10 seconds value
        true_realtime = False

    print("Target plot window length = {0:.2f}s".format(timing["plot_window"]))
    print("Amount of data to fetch each update = {0:.2f}s".format(timing["window_length"]))
    if not mydata["replay"]:
        print("Update interval = {0:.2f}s".format(timing["update_interval"]))

    ################ run once - to set up various things
    last_start_time = time.time()
    st_end = []
    st_end = update(timing, mydata, preproc, kwargs, to_plot, spectro, array_resp, \
        logfile, st_end, narrays)
    gc.collect()
    del gc.garbage[:]
    gc.collect()
    ###############

    # reset flag
    to_plot["first"] = False

    ## begin update loop
    while True:

        if mydata["replay"]: # if in "replay" mode no need to wait!
            gc.collect()
            del gc.garbage[:]
            gc.collect()
            st_end = update(timing, mydata, preproc, kwargs, to_plot, spectro, array_resp, logfile,\
                    st_end, narrays)

        elif not mydata["replay"] and not true_realtime: # realtime mode, but using a start time \
            # in the past - perhaps using a server but looking at older data or something.
            # No need to wait here either
            gc.collect()
            del gc.garbage[:]
            gc.collect()
            st_end = update(timing, mydata, preproc, kwargs, to_plot, spectro, array_resp, logfile,\
                    st_end, narrays)

        else: # assuming normal realtime mode, so need to schedule recurring updates
            gc.collect()
            del gc.garbage[:]
            gc.collect()
#            scheduler.run_pending()
            # pause to allow figure updates to print:
            time.sleep(2)
            print("Waiting for next update")
            time_to_wait(last_start_time, timing["update_interval"], st_end, \
            timing["max_realtime_latency"], logfile)
            last_start_time = time.time()
            st_end = update(timing, mydata, preproc, kwargs, to_plot, spectro, array_resp, logfile,\
                    st_end, narrays)

        gc.collect()
        del gc.garbage[:]
        gc.collect()
