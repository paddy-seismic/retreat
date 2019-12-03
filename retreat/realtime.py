"""realtime"""
def realtime(gui_input, logfile):
    """Performs an update based on input from the GUI.
    Fetches data, performs processing and updates output."""
    # import necessary functions
    import time
    import sys
    import gc
    from retreat.tools.time_to_wait import time_to_wait
    from retreat.gui.get_param_gui import get_param
    from retreat.update import update

    # redirect output to log file:
    sys.stdout = open(logfile, 'a+')
    sys.stderr = sys.stdout

    print("#####################################")
    print("Starting logging: "+ time.strftime('%Y-%m-%d %H:%M:%S'))

    ## get input parameters
    print("Fetching parameters")
    #print(gui_input)

    timing, mydata, preproc, kwargs, to_plot, spectro, array_resp = get_param(gui_input)

    print("Target plot window length = {0:.2f}s".format(timing["plot_window"]))
    print("Amount of data to fetch each update = {0:.2f}s".format(timing["window_length"]))
    if not mydata["replay"]:
        print("Update interval = {0:.2f}s".format(timing["update_interval"]))

    ################ run once - to set up various things
    last_start_time = time.time()
    st_end = update(timing, mydata, preproc, kwargs, to_plot, spectro, array_resp, logfile)
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
            st_end = update(timing, mydata, preproc, kwargs, to_plot, spectro, array_resp, logfile)

        else: # realtime mode, so schedule recurring updates
            gc.collect()
            del gc.garbage[:]
            gc.collect()
#            scheduler.run_pending()
            print("Waiting for next update")
            time_to_wait(last_start_time, timing["update_interval"], st_end, logfile)
            last_start_time = time.time()
            st_end = update(timing, mydata, preproc, kwargs, to_plot, spectro, array_resp, logfile)

        gc.collect()
        del gc.garbage[:]
        gc.collect()

    return
