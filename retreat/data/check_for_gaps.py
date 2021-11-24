"""check_for_gaps.py"""
def check_start_end_times(tr, starts, ends, max_gap_ends, demean, myfill):
    """
    Checks the input trace for gaps at the start/end of trace compared to other
    traces in the containing stream. i.e. finds channels that start late/end early.
    Attempts to fill or removes any such channels depending on allowed gap size

    Args:
        tr (trace): single trace object
        starts: list of start times from stream object that tr belongs to
        ends: end times of stream containing tr
        max_gap_ends: maximum allowed/tolerated gap [in seconds] to fill/pad
        demean: Boolean demean parameter
        myfill: fill value (default is mean/zero

    Returns:
        tr: trace with (any) gaps filled
        remove: Boolean flag to specify if:
        False) trace start/end times were OK or was filled successfully
        or
        True) trace should be removed
    """
    import numpy as np

    remove = False
    # check start/end times
    if tr.stats.starttime > min(starts): # trace starts late
        # try to pad
        if (tr.stats.starttime - min(starts)) < max_gap_ends:
            print("Trace starts late, but gap less than max_gap_size. Padding...")
            if demean:
                if isinstance(tr.data, np.ma.masked_array):
                    tr.split().detrend('demean').trim(starttime=min(ends), pad=True, \
                        fill_value=0).merge()
                else:
                    tr.detrend('demean').trim(starttime=min(starts), pad=True, \
                        fill_value=0)
            else:
                tr.trim(starttime=min(starts), pad=True, fill_value=myfill)
        # else remove
        else:
            remove = True
            print(tr.id, "starts late, removing...")
    else:
        if tr.stats.endtime < max(ends): # trace ends early
            # try to pad
            if (max(ends) - tr.stats.endtime) < max_gap_ends:
                print("Trace ends early, but gap less than max_gap_size. Padding...")
                if demean:
                    if isinstance(tr.data, np.ma.masked_array):
                        tr.split().detrend('demean').trim(endtime=max(ends), pad=True, \
                            fill_value=0).merge()
                    else:
                        tr.detrend('demean').trim(endtime=max(ends), pad=True, \
                            fill_value=0)
                else:
                    tr.trim(endtime=max(ends), pad=True, fill_value=myfill)
            # else remove
            else:
                remove = True
                print(tr.id, "ends early, removing...")

    return tr, remove

def check_for_gaps(st, min_nchan, max_gap_size, max_gap_ends, demean, logfile):
    """
    Checks the input stream for gaps to ensure success of array_processing.
    Removes any channels with short duration or those that contain any gaps

    Args:
        st (stream): stream object
        min_nchan (integer): minimum of channels required in the stream
        max_gap_size: maximum acceptable gap size (in seconds) that can be filled
        max_gap_ends: maximum acceptable gap size (in seconds) that can be filled at
        the start/end of each trace
        demean: pre-processing parameter
        logfile: log file name

    Returns:
        st: stream object with (any) channels removed
        chan_status: True if sufficient good channels (>=min_nchan), False otherwise

    """
    import sys
    import numpy as np

    # redirect output to log file:
    #sys.stdout = open(logfile, 'a+')
    #sys.stderr = sys.stdout

    # merge
    st.merge()

    # get all start and end times
    starts = [tr.stats.starttime for tr in st]
    ends = [tr.stats.endtime for tr in st]

    ### check/set status
    chan_status = True
    nchan = len(st)

    # initialise counter
    _i = 0

    ### START LOOP OVER TRACES
    for tr in st:

        print("Checking trace", tr.id)

        myfill = 0
        if not demean: # grab and store mean to add back on later if needed
            mymean = np.mean(tr.data)
            myfill = int(np.round(mymean))

        # check start/end times
        tr2, remove = check_start_end_times(tr, starts, ends, max_gap_ends, demean, myfill)

        if remove:
            st.remove(tr)
            nchan = nchan - 1
            continue # skip to next trace/channel
        else:
            tr = tr2
            st[_i] = tr2

        # check nchan again before bothering to continue
        if nchan < min_nchan:
            print("Error: Only", nchan, "valid channels")
            chan_status = False
            break # no point continuing, exit loop completely

        else: # carry on and check for gaps

            # now check for gaps
            gaps = tr.split().get_gaps()

            if gaps: # we found SOME gaps

                # now check if any of the gaps are bigger than our acceptable threshold
                big_gaps = tr.split().get_gaps(min_gap=max_gap_size)

                if not big_gaps:

                    # ALL the gaps are less than max_gap_size, so fill them in
                    print("Found gaps in", tr.id, ", but all less than max_gap_size. \
                          Attempting to fill gaps...")

                    # split, demean, then fill gaps with zeroes during remerge
                    if demean:
                        tr = tr.split().detrend('demean').merge(fill_value=0)[0]
                        st[_i] = tr
                    else:
                        tr = tr.split().merge(fill_value=myfill)[0]
                        st[_i] = tr

                else: # we found some gaps, but larger than max_gap_size, so remove
                      # these channels
                    print("Found gaps in", tr.id, "larger than max_gap_size. \
                          Removing this channel...")
                    st.remove(tr)
                    nchan = nchan - 1
                    if nchan < min_nchan:
                        print("Error: Only", nchan, "valid channels")
                        chan_status = False
                        break # no point continuing, exit loop completely
                    continue  # skip to next trace/channel

            else:
                print("No gaps found in", tr.id)

        # check for weird bug where trace data is masked but ALL mask values are False
        # (i.e masked but there are NO GAPS!) - fix by replacing with normal np.array
        # Think this arises from earlier data being filled, but the stream object then
        # not being retained/passed back in the main update loop (can't due to
        # preproc/response removal etc)

            if isinstance(tr.data, np.ma.masked_array):

                # trace still masked... try and fix
                print(tr)
                print("trace", tr.id, "still masked. Checking if all False")

                if not any(tr.data.mask):
                    print("Fixing...")
                    tr.data = tr.data.data
                    print(type(tr.data))
                    print("Fixed.")
                else:
                    print("True masked array found. Checking trace again...")
                    # check start/end times again
                    tr2, remove = check_start_end_times(tr.split()[0], starts, ends, \
                        max_gap_size, demean, myfill)

                    if remove:
                        st.remove(tr)
                        nchan = nchan - 1
                        continue # skip to next trace/channel
                    else:
                        tr = tr2
                        st[_i] = tr2

            # remove mean if necessary
            if demean:
                tr.detrend('demean')

            # finally, advance counter:
            _i = _i+1

    # Final status check again after gap fill/removal
    nchan = len(st)
    if nchan < min_nchan:
        print("Error: Only", nchan, "channels without gaps")
        chan_status = False

    return st, chan_status

def merge_checks(st):
    """
    Sanity checks for merging.
    """
    sr = {}
    dtype = {}
    calib = {}
    for trace in st.traces:
        # skip empty traces
        if len(trace) == 0:
            continue
        # Check sampling rate.
        sr.setdefault(trace.id, trace.stats.sampling_rate)
        if trace.stats.sampling_rate != sr[trace.id]:
            st.remove(trace)
            break
        # Check dtype.
        dtype.setdefault(trace.id, trace.data.dtype)
        if trace.data.dtype != dtype[trace.id]:
            st.remove(trace)
            break
        # Check calibration factor.
        calib.setdefault(trace.id, trace.stats.calib)
        if trace.stats.calib != calib[trace.id]:
            st.remove(trace)
            break

    return st
