"""rms_rmes - various functions used to calculate mean and median-filtered envelopes"""
import sys
import numpy as np
DEFAULT_N_CHUNKS = 20.0
DEFAULT_OVERLAP = 0.75

### RMS
def window_rms(tr, window_length, overlap, logfile):
    """Return timeseries of RMS average amplitude over given windows"""

    # redirect output to log file:
    sys.stdout = open(logfile, 'a+')
    sys.stderr = sys.stdout

#    # decimate to speed things up
#    factor = 4
#    tr.decimate(factor)

    # remove mean
    tr.detrend(type="demean")

    # check inputs
    length_seconds = (tr.stats.npts/tr.stats.sampling_rate)

    overlap = float(overlap)
    if not (0 <= overlap <= 1):
        print("Warning: overlap outside [0-1] range. Adjusting to default: ", DEFAULT_OVERLAP)
        overlap = DEFAULT_OVERLAP

    #print "length_seconds =", length_seconds
    if window_length >= length_seconds/2:
        print("Warning: incompatible window size. Adjusting to defaults")
        window_length = (length_seconds/DEFAULT_N_CHUNKS)
        overlap = DEFAULT_OVERLAP

    # convert overlap to step size
    step = float((1 - overlap)*window_length)

    # calculate rms and time in each window
    rms_times = np.asarray([tr2rms(wtr) for wtr in \
    tr.slide(window_length=window_length, step=step, include_partial_windows=True)])

    ## 'slide' function's include_partial_windows option only includes partial windows
    # at THE END of the trace - so here we calculate the average of partial windows
    # at BEGINNING of the trace for nice symmetric output:
    t = tr.stats.starttime
    # set counter
    mytime = step
    # initialise arrays
    rms_start_partial = np.array([])
    time_start_partial = np.array([])
    # begin while loop:
    while mytime < window_length:

        # get average of partial windowed trace
        myav, mytt = tr2rms(tr.slice(t, t+mytime))
        rms_start_partial = np.append(rms_start_partial, myav)
        time_start_partial = np.append(time_start_partial, mytt)
        # increment counter by step:
        mytime += step

    ## append mean and time values to the beginning:
    rms = np.concatenate([rms_start_partial, rms_times[:, 0]])
    times = np.concatenate([time_start_partial, rms_times[:, 1]])

    return rms, times

### RMeS
def window_rmes(tr, window_length, overlap, logfile):
    """Return timeseries of RMeS average amplitude over given windows"""

    # redirect output to log file:
    sys.stdout = open(logfile, 'a+')
    sys.stderr = sys.stdout

#    # decimate to speed things up
#    factor = 4
#    tr.decimate(factor)

    # remove mean
    tr.detrend(type="demean")

    # check inputs
    length_seconds = (tr.stats.npts/tr.stats.sampling_rate)

    overlap = float(overlap)
    if not (0 <= overlap <= 1):
        print("Warning: overlap outside [0-1] range. Adjusting to default: ", DEFAULT_OVERLAP)
        overlap = DEFAULT_OVERLAP

    #print "length_seconds =", length_seconds
    if window_length > length_seconds/2:
        print("Warning: incompatible window size. \
        Adjusting to defaults: length_seconds/", str(DEFAULT_N_CHUNKS))
        window_length = (length_seconds/DEFAULT_N_CHUNKS)
        overlap = DEFAULT_OVERLAP
    # convert overlap to step size
    step = float((1 - overlap)*window_length)

    # calculate rmes and time in each window
    rmes_times = np.asarray([tr2rmes(wtr) for wtr in \
    tr.slide(window_length=window_length, step=step, include_partial_windows=True)])

    ## 'slide' function's include_partial_windows option only includes partial windows
    # at THE END of the trace - so here we calculate the average of partial windows
    # at BEGINNING of the trace for symmetric output:
    t = tr.stats.starttime
    # set counter
    mytime = step
    # initialise arrays
    rmes_start_partial = np.array([])
    time_start_partial = np.array([])
    # begin while loop:
    while mytime < window_length:

        # get average of partial windowed trace
        myav, mytt = tr2rmes(tr.slice(t, t+mytime))
        rmes_start_partial = np.append(rmes_start_partial, myav)
        time_start_partial = np.append(time_start_partial, mytt)
        # increment counter by step:
        mytime += step

    ## append median and time values to the beginning:
    rmes = np.concatenate([rmes_start_partial, rmes_times[:, 0]])
    times = np.concatenate([time_start_partial, rmes_times[:, 1]])

    return rmes, times

def tr2rms(tr):
    """function to return RMS and mean time of a single trace object"""
    tr_rms = np.sqrt(np.mean(tr.data**2)) # rms value of the trace
    # mean time of the trace:
    time = (tr.stats.starttime.matplotlib_date + tr.stats.endtime.matplotlib_date)/2
    return tr_rms, time

def tr2rmes(tr):
    """function to return RMeS and mean time of a single trace object"""
    tr_rmes = np.sqrt(np.median(tr.data**2)) # rmes value of the trace
    # mean time of the trace:
    time = (tr.stats.starttime.matplotlib_date + tr.stats.endtime.matplotlib_date)/2
    return tr_rmes, time
