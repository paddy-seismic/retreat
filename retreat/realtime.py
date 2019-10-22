"""realtime"""
def realtime(gui_input, logfile):
    """Performs an update based on input from the gui.
    Fetches data, performs processing and updates output."""
    # import necessary functions
    import time
    import sys
    import gc
 #   import os
#    import schedule
#   from safe_schedule3 import SafeScheduler
    from retreat.tools.time_to_wait import time_to_wait
    from retreat.gui.get_param_gui import get_param
    from retreat.update import update
#    from obspy.core import UTCDateTime
#   # non-blocking window read:
#    from cancel import check_for_cancel_exit

    # redirect output to log file:
    sys.stdout = open(logfile, 'a+')
    sys.stderr = sys.stdout

    print("#####################################")
    print("Starting logging: "+ time.strftime('%Y-%m-%d %H:%M:%S'))

    #print('Process p (realtime) id: {}'.format(os.getpid()))
#    ## set up logs
#    import logging
#    logging.root.setLevel(logging.NOTSET)
#    logging.basicConfig(level=logging.INFO,format='%(asctime)s %(message)s')
#    logging.Formatter.converter = time.gmtime
#    logging.getLogger('schedule').setLevel(logging.CRITICAL + 10)

    ## get input parameters
    print("Fetching parameters")
    #print(gui_input)

    timing, mydata, preproc, kwargs, to_plot, spectro, array_resp = get_param(gui_input)

#    logging.info("target plot window length = %ss",timing["plot_window"])
#    logging.info("update_interval = %ss",timing["update_interval"])
#    logging.info("amount of data to fetch each update = %ss",timing["window_length"])
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

    #raise StopIteration

    # reset flag
    to_plot["first"] = False

#    if not mydata["replay"]:
#        ############# schedule loop ##### (REALTIME MODE ONLY)
#        scheduler = SafeScheduler()
#        scheduler.every(timing["update_interval"]).seconds.do(update, timing, mydata, \
#        preproc, kwargs, to_plot, spectro, array_resp, logfile)

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
