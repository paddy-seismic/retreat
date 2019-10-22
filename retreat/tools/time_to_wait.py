"""time_to_wait"""

import time
import math
import sys

def time_to_wait(start_time, update, end_of_stream, logfile):
    """Calculates how long to wait (if at all) between updates"""
    # redirect output to log file:
    sys.stdout = open(logfile, 'a+')
    sys.stderr = sys.stdout

    fudge = 5
    now = time.time()
    diff = (now - start_time)
    delay = (now - end_of_stream.timestamp)

    print("Completed in {0:.2f}s".format(diff))
    print("Difference to real-time: {0:.2f}s".format(delay))

    if (diff + fudge) < update:
        # processing completed within update internal - wait for the remaining seconds:
        print("Starting next update")
        time.sleep(math.floor(update - diff - fudge))
    else:
        # processing of update took longer than the update interval - display warning and proceed
        print("*Warning! Processing of update took longer than update interval ({0:.1f}s)!*"\
        .format(update))
        print("*Real-time processing may lag*")
