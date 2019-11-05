"""fix_times.py"""
def fix_times(st, kwargs):
    """
    Fixes the start and end times of keyword arguments passed to the array_processing module

    Adjusts the `stime` and `etime` values of kwargs to be the LATEST start and
    EARLIEST end times of the traces in the given stream object - ensure no gaps.

    Args:
        st (stream): stream object
        **kwargs: Keyword arguments (for array_processing) containing the start and end times

    Returns:
        **kwargs: modified keyword arguments with new start and end times

    """
    stime = max([st[i].stats.starttime for i in range(st.count())])
    etime = min([st[i].stats.endtime for i in range(st.count())])

    kwargs["stime"] = stime
    kwargs["etime"] = etime - 0.1# fudge factor buffer

    return kwargs
