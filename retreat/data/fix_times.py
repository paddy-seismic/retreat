"""fix_times"""
def fix_times(st, kwargs):
    """Adjusts the stime and etime to be the LATEST start \
    and EARLIEST end times of the traces in the stream object"""
    stime = max([st[i].stats.starttime for i in range(st.count())])
    etime = min([st[i].stats.endtime for i in range(st.count())])

    kwargs["stime"] = stime
    kwargs["etime"] = etime - 0.1# fudge factor buffer

    return kwargs
