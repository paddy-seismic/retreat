# ------------------------------------------------------------------
# Filename: beamforming_lsqr.py
# Purpose: Functions for performing Least-Squares beamforming
# Author: Paddy Smith, DIAS. 2020
# Adapted for python from: https://github.com/silvioda/Infrasound-Array-Processing-Matlab
# which was written for Matlab by Silvio De Angelis. See https://doi.org/10.3389/feart.2020.00169
# Email: psmith@cp.dias.ie
# --------------------------------------------------------------------
"""
Functions for  performing Least-Squares beamforming
"""
import numpy as np
from numpy.linalg.linalg import multi_dot
from obspy.signal.array_analysis import get_spoint, get_geometry
import matplotlib.dates as mdates

def do_inversion(st, **kwargs):
    """
    # DO_INVERSION least-squares inversion of (infrasonic) array data for backazimuth to
    # the source and apparent horizontal velocity (& slowness) across the array
    #
    :param stream: Stream object, the trace.stats dict like class must
        contain an :class:`~obspy.core.util.attribdict.AttribDict` with
        'latitude', 'longitude' (in degrees) and 'elevation' (in km), or 'x',
        'y', 'elevation' (in km) items/attributes. See param ``coordsys``.
    :type win_len: float
    :param win_len: Sliding window length in seconds
    :type win_frac: float
    :param win_frac: Fraction of sliding window to use for step
    :type stime: :class:`~obspy.core.utcdatetime.UTCDateTime`
    :param stime: Start time of interest
    :type etime: :class:`~obspy.core.utcdatetime.UTCDateTime`
    :param etime: End time of interest
    :type timestamp: str
    :param timestamp: valid values: 'julsec' and 'mlabday'; 'julsec' returns
        the timestamp in seconds since 1970-01-01T00:00:00, 'mlabday'
        returns the timestamp in days (decimals represent hours, minutes
        and seconds) since '0001-01-01T00:00:00' as needed for matplotlib
        date plotting (see e.g. matplotlib's num2date)
    :return: :class:`numpy.ndarray` of timestamp, variance of azimuth for each window,
        variance of velocity for each window, backazimuth, slowness, velocity
    #
    # Original author: Silvio De Angelis, University of Liverpool
    # Adapted for python by Paddy Smith, DIAS
    """

    # get args
    win_len = kwargs["win_len"]
    win_frac = kwargs["win_frac"]
    stime = kwargs["stime"]
    etime = kwargs["etime"]

    # defaults
    coordsys = 'lonlat' # ASSUME this
    verbose = False
    timestamp = 'mlabday'

    if 'coordsys' in kwargs:
        coordsys = kwargs["coordsys"]
    if 'verbose' in kwargs:
        verbose = kwargs["verbose"]
    if 'timestamp' in kwargs:
        timestamp = kwargs["timestamp"]

    # initialise
    res = []
    eotr = True

    nstat = len(st)

    # Sampling frequency (must be the same for all channels)
    # so check that sampling rates do not vary
    fs = st[0].stats.sampling_rate
    if len(st) != len(st.select(sampling_rate=fs)):
        msg = 'Sampling rates of traces in stream are not equal'
        raise ValueError(msg)

    # Get array geometry
    geom = get_geometry(st, coordsys=coordsys, verbose=verbose)

    # Inter-station distances and azimuths across the array
    d = np.array([])
    az = np.array([])

    for ii in range(nstat):
        for jj in range(ii+1, nstat):

            xdiff = (geom[ii, 0] - geom[jj, 0])
            ydiff = (geom[ii, 1] - geom[jj, 1])

            dist = np.sqrt(xdiff**2 + ydiff**2)
            azi = 90-(np.arctan2(ydiff, xdiff)*180/np.pi)+180

            az = np.append(az, azi)
            d = np.append(d, dist)

    # offset of arrays
    spoint, _epoint = get_spoint(st, stime, etime)

    if verbose:
        print("geometry:")
        print(geom)
        print("stream contains following traces:")
        print(st)
        print("stime = " + str(stime) + ", etime = " + str(etime))

    # Follow the method of obspy array_processing routine to create a loop
    # of sliding windows over the trace data
    #
    nsamp = int(win_len * fs)
    nstep = int(nsamp * win_frac)
    newstart = stime
    offset = 0

    # initialise data array
    dat = np.empty((nstat, nsamp))

    # begin while loop over windows
    while eotr:
        try:
            for i, tr in enumerate(st):
                dat[i, :] = tr.data[spoint[i] + offset:spoint[i] + offset + nsamp]
        except IndexError:
            break

        # Time lags and max cross-correlation coefficients between all station pairs in the array
        lags = np.array([])
        cmax = np.array([])

        for ii in range(nstat):
            for jj in range(ii+1, nstat):

                ll, cc = xcorr(dat[ii, :], dat[jj, :], maxlags=None)

                cmax = np.append(cmax, np.max(cc))
                lags = np.append(lags, ll[np.argmax(cc)])

        # Convert time lags to seconds
        dt = lags/fs

        # Generalized inverse of slowness matrix
        Dm = np.transpose(np.array([d*np.cos(az*(np.pi/180)), d*np.sin(az*(np.pi/180))]))
        Gmi = np.linalg.inv(np.dot(np.transpose(Dm), Dm))

        # Solve for slowness using least squares
        sv = multi_dot([Gmi, np.transpose(Dm), np.transpose(dt)])

        # Obtain velocity from slowness
        slow = np.linalg.norm(sv)
        v = 1/slow

        # Cosine and Sine for backazimuth
        caz = v*sv[0]
        saz = v*sv[1]

        # 180 degree resolved backazimuth to source
        srcaz = np.arctan2(saz, caz)*(180/np.pi)
        if srcaz < 0:
            srcaz = srcaz+360

        # Estimate of data covariance from Szuberla and Olson (2004), their equation 5
        B = np.eye(len(Dm)) - multi_dot([Dm, Gmi, np.transpose(Dm)])
        sig2dt = (multi_dot([dt, B, np.transpose(dt)]))/(len(Dm)-2)
        # sig2dt = (dt*(eye(length(Dm))-Dm*Gmi*transpose(Dm))*transpose(dt))/(length(Dm)-2);

        # Model covariance in terms of slowness assuming independent, Gaussian noise
        sig2sx = np.dot(sig2dt, Gmi[0, 0])
        sig2sy = np.dot(sig2dt, Gmi[1, 1])
        covsxsy = np.dot(sig2dt, Gmi[0, 1])

        # Variance of trace velocity and azimuth, these are obtained by propagation of errors
        # and differentiation
        sig2vl = sig2sx*sv[0]**2*v**6 + sig2sy*sv[1]**2*(v**6) + 2*covsxsy*sv[0]*sv[1]*v**6
        sig2th = sig2sx*sv[1]**2*v**4 + sig2sy*sv[0]**2*(v**4) - 2*covsxsy*sv[0]*sv[1]*v**4

        ### Append results to output array
        res.append(np.array([newstart.timestamp, sig2vl, sig2th, srcaz, slow, v]))

        if verbose:
            print(newstart, (newstart + (nsamp / fs)), res[-1][1:])

        # exit loop if at end of trace
        if (newstart + (nsamp + nstep) / fs) > etime:
            eotr = False

        # otherwise advance to next window
        offset += nstep
        newstart += nstep / fs
        ### End of while loop

    res = np.array(res)

    if timestamp == 'julsec':
        pass
    elif timestamp == 'mlabday':
        res[:, 0] = res[:, 0] / (24. * 3600) + mdates.date2num(np.datetime64('1970-01-01'))
    else:
        msg = "Option timestamp must be one of 'julsec', or 'mlabday'"
        raise ValueError(msg)

    return np.array(res)

def xcorr(x, y, normed=True, detrend=False, maxlags=None):
    # Cross correlation of two signals of equal length
    # Returns the coefficients when normed=True
    # Returns inner products when normed=False
    # Usage: lags, c = xcorr(x,y,maxlags=len(x)-1)
    # Optional detrending e.g. mlab.detrend_mean

    Nx = len(x)
    if Nx != len(y):
        raise ValueError('x and y must be equal length')

    if detrend:
        import matplotlib.mlab as mlab
        x = mlab.detrend_mean(np.asarray(x)) # can set your preferences here
        y = mlab.detrend_mean(np.asarray(y))

    c = np.correlate(x, y, mode='full')

    if normed:
        n = np.sqrt(np.dot(x, x) * np.dot(y, y)) # this is the transformation function
        c = np.true_divide(c, n)

    if maxlags is None:
        maxlags = Nx - 1

    if maxlags >= Nx or maxlags < 1:
        raise ValueError('maglags must be None or strictly '
                         'positive < %d' % Nx)

    lags = np.arange(-maxlags, maxlags + 1)
    c = c[Nx - 1 - maxlags:Nx + maxlags]
    return lags, c
