"""update_plot"""
import gc
import sys
import concurrent.futures
import numpy as np
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as mtick
from matplotlib.ticker import MaxNLocator
from matplotlib.colorbar import ColorbarBase
from matplotlib.colors import Normalize
from obspy.imaging.cm import obspy_sequential
from obspy.core import UTCDateTime
from obspy.core import Stream
from retreat.plot.rms_rmes import window_rms, window_rmes, tr2rms, tr2rmes
from retreat.data.get_array_response import get_array_response
from retreat.tools.processpool import get_nproc
from retreat.plot.add_logos import add_logos
from retreat.plot.set_font_sizes import set_font_sizes
from retreat.plot.shiftedColorMap import shiftedColorMap
from retreat.data.get_nth import get_nth

def update_plot(st, data, array_params, to_plot, spectro, inv, array_resp, narrays, logfile):
    """Updates output figures in the figure window based on the latest data"""

    # redirect output to log file:
    sys.stdout = open(logfile, 'a+')
    sys.stderr = sys.stdout

    # set font sizes:
    SMALL_SIZE, MEDIUM_SIZE, BIGGER_SIZE = set_font_sizes(to_plot["timelinex"], "timeline")
    #print(SMALL_SIZE, MEDIUM_SIZE, BIGGER_SIZE)
    plt.rc('font', size=SMALL_SIZE)          # controls default text sizes
    plt.rc('axes', titlesize=SMALL_SIZE)     # fontsize of the axes title
    plt.rc('axes', labelsize=MEDIUM_SIZE)    # fontsize of the x and y labels
    plt.rc('xtick', labelsize=SMALL_SIZE)    # fontsize of the tick labels
    plt.rc('ytick', labelsize=SMALL_SIZE)    # fontsize of the tick labels
    plt.rc('legend', fontsize=SMALL_SIZE)    # legend fontsize
    plt.rc('figure', titlesize=BIGGER_SIZE)  # fontsize of the figure title

    ### split data matrices

    # initialise empty lists
    time = []
    err_vel = []
    err_baz = []
    vel = []
    relpow = []
    abspow = []
    baz = []
    slow = []

    # tolerance for last tick to avoid labels extending beyond x-axis
    endper = 5

    for n, dat in enumerate(data):
        times = dat[:, 0]
        if array_resp["lsq"][n]:
            err_vels = np.sqrt(dat[:, 1]) # convert from variance to std
            err_bazs = np.rad2deg(np.sqrt(dat[:, 2])) # variance to std and then radians to degrees
            vels = dat[:, 5]
            relpows = dat[:, 6] # this is actually MCCM but label as relpow for convenience
            # so as to avoid repetiton of code
        else:
            relpows = dat[:, 1]
            abspows = dat[:, 2]
        bazs = dat[:, 3]
        slows = dat[:, 4]

        # make output human readable, adjust backazimuth to values between 0 and 360
        bazs[bazs < 0.0] += 360

        # append lists:
        time.append(times)
        baz.append(bazs)
        slow.append(slows)
        relpow.append(relpows)

        if array_resp["lsq"][n]:
            err_vel.append(err_vels)
            err_baz.append(err_bazs)
            vel.append(vels)
            #
            abspow.append([])
        else:
            abspow.append(abspows)
            #
            err_vel.append([])
            err_baz.append([])
            vel.append([])

    # get GUI slowness parameters for later use
    #print('array_params=',array_params)
    slm_x = array_params["slm_x"]
    slm_y = array_params["slm_y"]
    sll_x = array_params["sll_x"]
    sll_y = array_params["sll_y"]
    sl_s = array_params["sl_s"]

    # check if using infrasound data - for axis label(s):
    infra = False
    for sti in st:
        for tr in sti:
            if tr.stats.channel.endswith('F'):
                infra = True
                break
        else:
            # Continue if the inner loop wasn't broken.
            continue
        # Inner loop was broken, break the outer.
        break

    ### MAIN TIMELINE ######################################

    # process "to_plot" arg to get what to plot
    nsubplots = sum([value for key, value in to_plot.items() if key not in\
    ('polar', 'rmes_ovlp', 'rmes_wind', 'resp', 'timelinex', 'timeliney', 'arrayx', 'timestamp',\
    'arrayy', 'polarx', 'polary', 'slow_ymin', 'slow_ymax', 'baz_ymin', 'baz_ymax', 'usestack',\
    'rms_ymin', 'rms_ymax', 'seis_ymin', 'seis_ymax', 'relpow_ymin', 'relpow_ymax', 'savefig',\
    'figpath', 'webfigs', 'map_array_radius', 'bazmap', 'mapx', 'mapy', 'map_array_centre',\
    'mapfigname', 'lat_min', 'lat_max', 'lon_min', 'lon_max', 'nbin_baz', 'nbin_slow', 'norm',\
    'timelinefigname', 'polarfigname', 'arrayfigname', 'logos', 'savedata', 'datafile', 'first',\
    'arraysep')])

    #print("nsubplots=", nsubplots)

    # check if separate timeline plots needed for each array
    if to_plot["arraysep"]:
        # get number of possible extra plots required
        extra_subplots = sum([value for key, value in to_plot.items() if key in\
            ('baz', 'slow', 'rmes', 'relpow', 'seis')])
        nsubplots = nsubplots + extra_subplots

    # add on extra for spectrograms:
    if to_plot["spec"]:
        nsubplots = nsubplots + (narrays-1)

    print("Total number of subplots selected = ", nsubplots)

#    global fig, ax
#    global my_dpi

    # shrink figures *slightly* if webfigs output (to account for menu bar etc in browser):
    if to_plot["webfigs"]:
        shrinkage = 0.9
        for key in ('timelinex', 'timeliney', 'arrayx', 'arrayy',\
        'polarx', 'polary', 'mapx', 'mapy'):
            to_plot[key] = int(shrinkage*to_plot[key])

    my_dpi = 100
    fig, ax = plt.subplots(nsubplots, 1, sharex=False, sharey=False,\
    figsize=(to_plot["timelinex"]/my_dpi, to_plot["timeliney"]/my_dpi), squeeze=False, dpi=my_dpi)

    xlocator = mdates.AutoDateLocator()

    # initialise/reset subplot index
    aindex = 0

    pstart = []
    pend = []
    #my_time_label = []
    my_xlabel = []
    labels = []

#    for n, sti in enumerate(st):
    for n in range(narrays):
        sti = st[n]
        #print("n=",n)
        #print("sti=",sti)
        pstart.append(sti[0].stats.starttime.matplotlib_date)
        pend.append(sti[0].stats.endtime.matplotlib_date)

        # **NB** For matplotlib >= 3.3.0 the epoch for date format has changed from
        # 0000-12-31T00:00:00 to UNIX default of 1970-01-01T00:00:00 to allow greater
        # resolution. The array_analysis routine still returns dates relative to the oldepoch.
        # However we cannot assume this will ALWAYS be true, as it may change/be fixed
        # in future versions. Hence, we explicitly check the difference
        # between the trace starttime and the first time value from the
        # array processing to check for any epoch mismatch:
        if (time[n][0] - pstart[n]) >= 719163.0:
            time[n] = time[n] + mdates.date2num(np.datetime64('0000-12-31'))

       # my_time_label.append(sti[0].stats.starttime.strftime('%d-%b-%Y %H:%M:%S%Z') + ' to ' +\
       # sti[0].stats.endtime.strftime('%d-%b-%Y %H:%M:%S%Z'))

        my_xlabel.append('Time [UTC] ' + sti[0].stats.starttime.strftime('%d-%b-%Y'))

    #labels = ['Array 1:'+st[0][0].id[3:7],'Array 2:'+st[1][0].id[3:7]]
    #labels=[]
    #for n in range(narrays):
        #labels.append('Array '+str(n+1)+':'+st[0][0].id[3:7])
        labels.append('Array '+str(n+1)+':'+sti[0].id[3:7])
        filled_markers = ('o', 'X', 'v', 'P', '^', 's', '8', '<', '>', '*', 'h', 'H', 'D', 'd', 'p')

    # complete label outside loop, get extremes
    my_time_label = sti[np.argmin(pstart)].stats.starttime.strftime('%d-%b-%Y %H:%M:%S%Z')\
        + ' to ' +\
        sti[np.argmax(pend)].stats.endtime.strftime('%d-%b-%Y %H:%M:%S%Z')

    if to_plot["baz"]:

        if to_plot["arraysep"]:
            for n in range(narrays):
            # plot backazimuths
                print("Plotting back azimuths")
                ax[aindex, 0].cla()

                ax[aindex, 0].scatter(time[n], baz[n], c=slow[n], alpha=0.6, edgecolors='none',\
                    label=labels[n])
                ax[aindex, 0].set_xlim(pstart[n], pend[n])

                if (to_plot["baz_ymin"][n] != 'auto') or (to_plot["baz_ymax"][n] != 'auto'):
                    baz_ymin = float(to_plot["baz_ymin"][n])
                    baz_ymax = float(to_plot["baz_ymax"][n])
                    ax[aindex, 0].set_ylim(baz_ymin, baz_ymax)

                ax[aindex, 0].xaxis.set_major_locator(xlocator)

                # remove last ticklabel if too close to end
                myticks = ax[aindex, 0].get_xticks()
                if (np.abs(myticks[-1] - pend[n]) < (endper/100 * (pend[n] - pstart[n]))):
                    ax[aindex, 0].set_xticks(myticks[:-1])

                ax[aindex, 0].xaxis.set_major_formatter(mdates.AutoDateFormatter(xlocator))
                ax[aindex, 0].set_ylabel('Back Azimuth [$^\circ$]')
                ax[aindex, 0].legend(loc='upper right')

                if (aindex+1) == nsubplots:
                    ax[aindex, 0].set_xlabel(min(my_xlabel))
                aindex = aindex + 1

        else:
            # plot backazimuths
            print("Plotting back azimuths")
            ax[aindex, 0].cla()
            markers = filled_markers[0:narrays]
            for n in range(narrays):
                ax[aindex, 0].scatter(time[n], baz[n], c=slow[n], alpha=0.6, \
                    edgecolors='none', marker=markers[n], label=labels[n])

            ax[aindex, 0].set_xlim(min(pstart), max(pend))

            for n in range(narrays):
                if (to_plot["baz_ymin"][n] != 'auto') or (to_plot["baz_ymax"][n] != 'auto'):
                    baz_ymin = float(to_plot["baz_ymin"][n])
                    baz_ymax = float(to_plot["baz_ymax"][n])
                    ax[aindex, 0].set_ylim(baz_ymin, baz_ymax)
                    print('Warning: arraysep is False, but baz axis limits defined.')
                    print('Using limits for Array', n+1, 'for combined plot')
                    break

            ax[aindex, 0].xaxis.set_major_locator(xlocator)

            # remove last ticklabel if too close to end
            myticks = ax[aindex, 0].get_xticks()
            if (np.abs(myticks[-1] - pend[n]) < (endper/100 * (pend[n] - pstart[n]))):
                ax[aindex, 0].set_xticks(myticks[:-1])

            ax[aindex, 0].xaxis.set_major_formatter(mdates.AutoDateFormatter(xlocator))
            ax[aindex, 0].set_ylabel('Back Azimuth [$^\circ$]')
            ax[aindex, 0].legend(loc='upper right')
            if (aindex+1) == nsubplots:
                ax[aindex, 0].set_xlabel(min(my_xlabel))
            aindex = aindex + 1

    if to_plot["slow"]:

        if to_plot["arraysep"]:
            for n in range(narrays):
                print("Plotting slowness")
                ax[aindex, 0].cla()
                ax[aindex, 0].scatter(time[n], slow[n], label=labels[n])
                ax[aindex, 0].set_xlim(pstart[n], pend[n])

                if (to_plot["slow_ymin"][n] != 'auto') or (to_plot["slow_ymax"][n] != 'auto'):
                    slow_ymin = float(to_plot["slow_ymin"][n])
                    slow_ymax = float(to_plot["slow_ymax"][n])
                    ax[aindex, 0].set_ylim(slow_ymin, slow_ymax)
                else:
                    ax[aindex, 0].set_ylim(0, 1.05*max(slow[n]))

                ax[aindex, 0].xaxis.set_major_locator(xlocator)

                # remove last ticklabel if too close to end
                myticks = ax[aindex, 0].get_xticks()
                if (np.abs(myticks[-1] - pend[n]) < (endper/100 * (pend[n] - pstart[n]))):
                    ax[aindex, 0].set_xticks(myticks[:-1])

                ax[aindex, 0].xaxis.set_major_formatter(mdates.AutoDateFormatter(xlocator))
                ax[aindex, 0].set_ylabel('Slowness [skm$^{-1}$]')
                ax[aindex, 0].legend(loc='upper right')
                if (aindex+1) == nsubplots:
                    ax[aindex, 0].set_xlabel(my_xlabel[n])
                aindex = aindex + 1


        else:
            # plot slowness
            print("Plotting slowness")
            ax[aindex, 0].cla()
            #markers=['o','X']
            for n in range(narrays):
                ax[aindex, 0].scatter(time[n], slow[n], marker=markers[n], label=labels[n])
            ax[aindex, 0].set_xlim(min(pstart), max(pend))

            for n in range(narrays):
                if (to_plot["slow_ymin"][n] != 'auto') or (to_plot["slow_ymax"][n] != 'auto'):
                    slow_ymin = float(to_plot["slow_ymin"][n])
                    slow_ymax = float(to_plot["slow_ymax"][n])
                    ax[aindex, 0].set_ylim(slow_ymin, slow_ymax)
                    print('Warning: arraysep is False, but slowness axis limits defined.')
                    print('Using limits for Array', n+1, 'for combined plot')
                    break
                else:
                    ax[aindex, 0].set_ylim(0, 1.05*np.max(slow))

            ax[aindex, 0].xaxis.set_major_locator(xlocator)

            # remove last ticklabel if too close to end
            myticks = ax[aindex, 0].get_xticks()
            if (np.abs(myticks[-1] - pend[n]) < (endper/100 * (pend[n] - pstart[n]))):
                ax[aindex, 0].set_xticks(myticks[:-1])

            ax[aindex, 0].xaxis.set_major_formatter(mdates.AutoDateFormatter(xlocator))
            ax[aindex, 0].set_ylabel('Slowness [skm$^{-1}$]')
            ax[aindex, 0].legend(loc='upper right')
            if (aindex+1) == nsubplots:
                ax[aindex, 0].set_xlabel(min(my_xlabel))
            aindex = aindex + 1

    if to_plot["relpow"]:
            # plot relative power (or MCCM for LSQ)
        if not array_resp["lsq"]:
            print("Plotting relative power")
        else:
            print("Plotting MCCM")

        if to_plot["arraysep"]:
            for n in range(narrays):
                ax[aindex, 0].cla()
                ax[aindex, 0].scatter(time[n], relpow[n], label=labels[n])
                ax[aindex, 0].set_xlim(pstart[n], pend[n])

                if (to_plot["relpow_ymin"][n] != 'auto') or (to_plot["relpow_ymax"][n] != 'auto'):
                    slow_ymin = float(to_plot["relpow_ymin"][n])
                    slow_ymax = float(to_plot["relpow_ymax"][n])
                    ax[aindex, 0].set_ylim(relpow_ymin, relpow_ymax)

                ax[aindex, 0].xaxis.set_major_locator(xlocator)

                # remove last ticklabel if too close to end
                myticks = ax[aindex, 0].get_xticks()
                if (np.abs(myticks[-1] - pend[n]) < (endper/100 * (pend[n] - pstart[n]))):
                    ax[aindex, 0].set_xticks(myticks[:-1])

                ax[aindex, 0].xaxis.set_major_formatter(mdates.AutoDateFormatter(xlocator))
                if not array_resp["lsq"]:
                    ax[aindex, 0].set_ylabel('Relative power')
                else:
                    ax[aindex, 0].set_ylabel('MCCM')
                ax[aindex, 0].legend(loc='upper right')
                if (aindex+1) == nsubplots:
                    ax[aindex, 0].set_xlabel(my_xlabel[n])
                aindex = aindex + 1

        else:
            ax[aindex, 0].cla()
            for n in range(narrays):
                ax[aindex, 0].scatter(time[n], relpow[n], marker=markers[n], label=labels[n])
            ax[aindex, 0].set_xlim(min(pstart), max(pend))


            for n in range(narrays):
                if (to_plot["relpow_ymin"][n] != 'auto') or (to_plot["relpow_ymax"][n] != 'auto'):
                    slow_ymin = float(to_plot["relpow_ymin"][n])
                    slow_ymax = float(to_plot["relpow_ymax"][n])
                    ax[aindex, 0].set_ylim(relpow_ymin, relpow_ymax)
                    print('Warning: arraysep is False, but relpow axis limits defined.')
                    print('Using limits for Array', n+1, 'for combined plot')
                    break

            ax[aindex, 0].xaxis.set_major_locator(xlocator)

            # remove last ticklabel if too close to end
            myticks = ax[aindex, 0].get_xticks()
            if (np.abs(myticks[-1] - pend[n]) < (endper/100 * (pend[n] - pstart[n]))):
                ax[aindex, 0].set_xticks(myticks[:-1])

            ax[aindex, 0].xaxis.set_major_formatter(mdates.AutoDateFormatter(xlocator))

            if not array_resp["lsq"]:
                ax[aindex, 0].set_ylabel('Relative power')
            else:
                ax[aindex, 0].set_ylabel('MCCM')
            ax[aindex, 0].legend(loc='upper right')
            if (aindex+1) == nsubplots:
                ax[aindex, 0].set_xlabel(min(my_xlabel))
            aindex = aindex + 1

    sys.stdout.flush()

    if to_plot["usestack"]: # calculate stack to plot
        from retreat.data.stack import stack
        from obspy.signal.array_analysis import get_geometry, get_timeshift

        mystack = []
        hist = []
        max_xy = []
        max_val = []
        max_slow_hist = []

        print('Calculating stack')

        for n in range(narrays):

            # try to remove any bad traces first:
            prestack = Stream()
            for tr in st[n]:
    #            print(tr.stats.station, tr.stats.starttime,'-',tr.stats.endtime)
                if not np.any(np.isnan(tr.data)):
                    prestack.append(tr)

            # Use the best "beam" as the stack (i.e. time shifts corresponding to max power)

            # try to remove any NaNs in relpow before weighting. First find non-NaN values
            non_nan_mask = ~np.isnan(relpow[n])
            # if all are NOT true, then we have some NaNs
            if not np.all(non_nan_mask):
                print("Replacing NaNs in relpow")
                relpow[n] = np.nan_to_num(relpow[n], copy=True, nan=1.0)

            # choose number of fractions in plot (desirably 360 degree/N is an integer!)
            N = to_plot["nbin_baz"]
            N2 = to_plot["nbin_slow"]

            # create the azimuth and slowness bins
            abins = np.arange(N + 1) * 360. / N
            max_slow_hist.append(np.ceil(1.5*2* np.max(np.abs([sll_x[n], sll_y[n],\
                slm_x[n], slm_y[n]])))/2) # 1.5x max \
            # abs value in grid, ... then rounded up to nearest 0.5
            if max_slow_hist[n] < np.max(slow[n]): # check values are not outside this range!
                max_slow_hist[n] = np.ceil(np.max(slow[n]))
            sbins = np.linspace(0, max_slow_hist[n], N2 + 1)

            # create the histogram NOW:
            # get histogram, and weight by relative power (or MCCM for LSQ)
            with concurrent.futures.ProcessPoolExecutor(max_workers=get_nproc()) as executor:
                histi, baz_edges, sl_edges = executor.submit(np.histogram2d,\
                    baz[n], slow[n], bins=[abins, sbins], weights=relpow[n]).result()

            if to_plot["norm"]:
                histi = histi/len(data[n])

            hist.append(histi)

            # find the coordinates of maximum relative power:
            #max_xy = np.unravel_index(np.argmax(hist, axis=None), hist.shape)
            max_xy.append(np.unravel_index(np.argmax(hist[n], axis=None), hist[n].shape))
            max_val.append(np.argmax(hist[n], axis=None))

            max_baz = abins[max_xy[n][0]]
            max_slow = sbins[max_xy[n][1]]

            #print('max_baz,max_slow=',max_baz,max_slow)

            # map baz, slow to Sx, Sy
            Sx = max_slow * np.cos((90-max_baz)*np.pi/180.)
            Sy = max_slow * np.sin((90-max_baz)*np.pi/180.)

            # use GUI parameters to make the slowness grid
            grdpts_x = int(((slm_x[n] - sll_x[n]) / sl_s[n] + 0.5) + 1)
            grdpts_y = int(((slm_y[n] - sll_y[n]) / sl_s[n] + 0.5) + 1)

            # create horizontal slowness vectors
            sx = []
            sy = []
            for k in range(grdpts_x):
                sxx = sll_x + k * sl_s
                sx = np.append(sx, sxx)
            for l in range(grdpts_y):
                syy = sll_y + l * sl_s
                sy = np.append(sy, syy)

            # Map the maximum power in slowness/azimuth coords to -> slx, sly coords:
            idx = (np.abs(sx-Sx)).argmin()
            if not np.isscalar(idx):
                idx = idx[0]
            idy = (np.abs(sy-Sy)).argmin()
            if not np.isscalar(idy):
                idy = idy[0]

            # get geometry from stream
            geometry = get_geometry(prestack, coordsys=array_resp["coordsys"], verbose=False)

            # now use this to get time shifts:
            time_shift_table = get_timeshift(geometry, sll_x[n], sll_y[n],\
                sl_s[n], grdpts_x, grdpts_y)

            # extract station time shifts corresponding to the maximum from the table:
            shifts = time_shift_table[:, idx, idy]

            # Finally, apply the time shifts:
            for tr, j in zip(prestack, range(len(prestack))):
                tr.data = np.roll(tr.data, int(tr.stats.sampling_rate*shifts[j]))

            # Now stack linearly (already shifted to get "beam")
            try:
            # allow 30 seconds difference in trace length (realtime lag)
                mystack.append(stack(prestack, npts_tol=30*prestack[0].stats.sampling_rate,\
                    time_tol=1.0))
                # check for bad data/NaN:
                if np.any(np.isnan(mystack[n][0].data)):
                    print('Warning, bad data in stack - reverting to first station in array')
                    mystack[n][0] = st[n][0]
    #            print('stack', mystack[0].stats.starttime,'-',tr.stats.endtime)
            except ValueError:
                print('Warning, bad data in stack - reverting to first station in array')
                to_plot["usestack"] = False

    if to_plot["rmes"]:
        # plot RMeS / envelope
        print("Plotting RMeS")

        if to_plot["arraysep"]:
            for n in range(narrays):

                ax[aindex, 0].cla()

                if to_plot["usestack"]:
                    with concurrent.futures.ProcessPoolExecutor(max_workers=get_nproc()) \
                            as executor: rmes, rtimes = executor.submit(window_rmes, \
                            mystack[n][0], to_plot["rmes_wind"],\
                            to_plot["rmes_ovlp"], logfile).result()
                else:
                    with concurrent.futures.ProcessPoolExecutor(max_workers=get_nproc()) \
                            as executor: rmes, rtimes = executor.submit(window_rmes, \
                            st[n][0], to_plot["rmes_wind"],\
                            to_plot["rmes_ovlp"], logfile).result()

                ax[aindex, 0].plot(rtimes, rmes, label=labels[n])
                ax[aindex, 0].set_xlim(pstart[n], pend[n])

                if (to_plot["rms_ymin"][n] != 'auto') or (to_plot["rms_ymax"][n] != 'auto'):
                    rms_ymin = float(to_plot["rms_ymin"][n])
                    rms_ymax = float(to_plot["rms_ymax"][n])
                    ax[aindex, 0].set_ylim(rms_ymin, rms_ymax)

                ax[aindex, 0].xaxis.set_major_locator(xlocator)

                # remove last ticklabel if too close to end
                myticks = ax[aindex, 0].get_xticks()
                if (np.abs(myticks[-1] - pend[n]) < (endper/100 * (pend[n] - pstart[n]))):
                    ax[aindex, 0].set_xticks(myticks[:-1])

                ax[aindex, 0].xaxis.set_major_formatter(mdates.AutoDateFormatter(xlocator))

                if not infra:
                    ax[aindex, 0].set_ylabel('RMeS Velocity [ms$^{-1}$]')
                else:
                    ax[aindex, 0].set_ylabel('RMeS Pressure')

                ax[aindex, 0].legend(loc='upper right')

                #ax[aindex,0].ticklabel_format(axis='y', style='sci')
                ax[aindex, 0].yaxis.set_major_formatter(mtick.FormatStrFormatter('%.1e'))
                if (aindex+1) == nsubplots:
                    ax[aindex, 0].set_xlabel(my_xlabel[n])
                aindex = aindex + 1

        else:

            ax[aindex, 0].cla()

            for n in range(narrays):
                if to_plot["usestack"]:
                    with concurrent.futures.ProcessPoolExecutor(max_workers=get_nproc()) \
                            as executor: rmes, rtimes = executor.submit(window_rmes, \
                            mystack[n][0], to_plot["rmes_wind"],\
                            to_plot["rmes_ovlp"], logfile).result()
                else:
                    with concurrent.futures.ProcessPoolExecutor(max_workers=get_nproc()) \
                            as executor: rmes, rtimes = executor.submit(window_rmes, \
                            st[n][0], to_plot["rmes_wind"],\
                            to_plot["rmes_ovlp"], logfile).result()

                ax[aindex, 0].plot(rtimes, rmes, label=labels[n])

            ax[aindex, 0].set_xlim(min(pstart), max(pend))

            for n in range(narrays):
                if (to_plot["rms_ymin"][n] != 'auto') or (to_plot["rms_ymax"][n] != 'auto'):
                    rms_ymin = float(to_plot["rms_ymin"][n])
                    rms_ymax = float(to_plot["rms_ymax"][n])
                    ax[aindex, 0].set_ylim(rms_ymin, rms_ymax)
                    print('Warning: arraysep is False, but rmes axis limits defined.')
                    print('Using limits for Array', n+1, 'for combined plot')
                    break

            ax[aindex, 0].xaxis.set_major_locator(xlocator)

            # remove last ticklabel if too close to end
            myticks = ax[aindex, 0].get_xticks()
            if (np.abs(myticks[-1] - pend[n]) < (endper/100 * (pend[n] - pstart[n]))):
                ax[aindex, 0].set_xticks(myticks[:-1])

            ax[aindex, 0].xaxis.set_major_formatter(mdates.AutoDateFormatter(xlocator))

            if not infra:
                ax[aindex, 0].set_ylabel('RMeS Velocity [ms$^{-1}$]')
            else:
                ax[aindex, 0].set_ylabel('RMeS Pressure')

            ax[aindex, 0].legend(loc='upper right', frameon=False)
            #ax[aindex,0].ticklabel_format(axis='y', style='sci')
            ax[aindex, 0].yaxis.set_major_formatter(mtick.FormatStrFormatter('%.1e'))
            if (aindex+1) == nsubplots:
                ax[aindex, 0].set_xlabel(min(my_xlabel))
            aindex = aindex + 1

    sys.stdout.flush()

    if to_plot["seis"]:
        # plot seismogram
        print("Plotting waveforms")

        if to_plot["arraysep"]:
            for n in range(narrays):

                if to_plot["usestack"]:
                    ax[aindex, 0].plot(mystack[n][0].times(type="matplotlib"), mystack[n][0].data, \
                        'k', label=labels[n])
                else:
                    ax[aindex, 0].plot(st[n][0].times(type="matplotlib"), st[n][0].data, \
                        'k', label=labels[n])

                ax[aindex, 0].set_xlim(pstart[n], pend[n])

                if (to_plot["seis_ymin"][n] != 'auto') or (to_plot["seis_ymax"][n] != 'auto'):
                    seis_ymin = float(to_plot["seis_ymin"][n])
                    seis_ymax = float(to_plot["seis_ymax"][n])
                    ax[aindex, 0].set_ylim(seis_ymin, seis_ymax)

                ax[aindex, 0].xaxis.set_major_locator(xlocator)

                # remove last ticklabel if too close to end
                myticks = ax[aindex, 0].get_xticks()
                if (np.abs(myticks[-1] - pend[n]) < (endper/100 * (pend[n] - pstart[n]))):
                    ax[aindex, 0].set_xticks(myticks[:-1])

                ax[aindex, 0].xaxis.set_major_formatter(mdates.AutoDateFormatter(xlocator))

                if not infra:
                    ax[aindex, 0].set_ylabel('Velocity [ms$^{-1}$]')
                else:
                    ax[aindex, 0].set_ylabel('Pressure')

                ax[aindex, 0].legend(loc='upper right', frameon=False)
                ax[aindex, 0].yaxis.set_major_formatter(mtick.FormatStrFormatter('%.1e'))

                if (aindex+1) == nsubplots:
                    ax[aindex, 0].set_xlabel(min(my_xlabel))

                aindex = aindex + 1

        else:
            cmap = plt.get_cmap("tab10")

            ax[aindex, 0].cla()

            for n in range(narrays):

                if to_plot["usestack"]:
                    ax[aindex, 0].plot(mystack[n][0].times(type="matplotlib"), \
                        mystack[n][0].data, color=cmap(n), label=labels[n])
                else:
                    ax[aindex, 0].plot(st[n][0].times(type="matplotlib"), st[n][0].data, \
                        color=cmap(n), label=labels[n])

            ax[aindex, 0].set_xlim(min(pstart), max(pend))
            for n in range(narrays):
                if (to_plot["seis_ymin"][n] != 'auto') or (to_plot["seis_ymax"][n] != 'auto'):
                    seis_ymin = float(to_plot["seis_ymin"][n])
                    seis_ymax = float(to_plot["seis_ymax"][n])
                    ax[aindex, 0].set_ylim(seis_ymin, seis_ymax)
                    print('Warning: arraysep is False, but seismogram axis limits defined.')
                    print('Using limits for Array', n+1, 'for combined plot')
                    break

            ax[aindex, 0].xaxis.set_major_locator(xlocator)

            # remove last ticklabel if too close to end
            myticks = ax[aindex, 0].get_xticks()
            if (np.abs(myticks[-1] - pend[n]) < (endper/100 * (pend[n] - pstart[n]))):
                ax[aindex, 0].set_xticks(myticks[:-1])

            ax[aindex, 0].xaxis.set_major_formatter(mdates.AutoDateFormatter(xlocator))

            if not infra:
                ax[aindex, 0].set_ylabel('Velocity [ms$^{-1}$]')
            else:
                ax[aindex, 0].set_ylabel('Pressure')

            ax[aindex, 0].legend(loc='upper right', frameon=False)

            ax[aindex, 0].yaxis.set_major_formatter(mtick.FormatStrFormatter('%.1e'))

            if (aindex+1) == nsubplots:
                ax[aindex, 0].set_xlabel(min(my_xlabel))

            aindex = aindex + 1

    sys.stdout.flush()

    if to_plot["spec"]:
        # plot spectrogram
        print("Plotting spectrograms")

        global sfmin, sfmax, vmax
        if to_plot["first"]:
            sfmin = spectro["fmin"]
            sfmax = spectro["fmax"]
            del spectro["fmin"]
            del spectro["fmax"]
        else: # double-check again, in case there was a problem with
            # the data the first time round the loop, and hence no
            # spectrogram was plotted. Check for/remove fmin/fmax
            if "fmin" in spectro:
                sfmin = spectro["fmin"]
                del spectro["fmin"]
            if "fmax" in spectro:
                sfmax = spectro["fmax"]
                del spectro["fmax"]

        for n in range(narrays):

            ax[aindex, 0].cla()

            array_spectro = get_nth(spectro, n)
            array_spectro["axes"] = ax[aindex, 0]

            #dummy for legend
            ax[aindex, 0].plot([], [], ' ', label=labels[n])

            # CALCULATE SPECTROGRAM
            if to_plot["usestack"]:
                mystack[n][0].spectrogram(**array_spectro)
            else:
                st[n][0].spectrogram(**array_spectro)
            # Grab image for manipulation
            im = ax[aindex, 0].images[0]

            # convert x-axis to absolute time:
            ext = list(im.get_extent())
            for ll in range(2):
                ext[ll] = ext[ll]/(60.*60*24) + pstart[n]
            tuple(ext)
            im.set_extent(ext)

            # set colorscale limits
            clip = array_spectro["clip"]
            _range = float(im.get_array().max() - im.get_array().min())
            vmin = im.get_array().min() + clip[0] * _range
            vmax = im.get_array().min() + clip[1] * _range
            im.set_clim(vmin=vmin, vmax=vmax)

            # axis limts
            ax[aindex, 0].set_ylim(sfmin[n], sfmax[n])
            ax[aindex, 0].set_xlim(pstart[n], pend[n])

            ax[aindex, 0].xaxis.set_major_locator(xlocator)

            # remove last ticklabel if too close to end
            myticks = ax[aindex, 0].get_xticks()
            if (np.abs(myticks[-1] - pend[n]) < (endper/100 * (pend[n] - pstart[n]))):
                ax[aindex, 0].set_xticks(myticks[:-1])

            ax[aindex, 0].xaxis.set_major_formatter(mdates.AutoDateFormatter(xlocator))

            ax[aindex, 0].set_ylabel('Frequency [Hz]')

            ax[aindex, 0].legend(loc='upper right')#,frameon=False)
            #ax[aindex, 0].legend([labels[n]])

            if (aindex+1) == nsubplots:
                ax[aindex, 0].set_xlabel(my_xlabel[n])

            aindex = aindex + 1

    fig.tight_layout()

    # add logo
    if to_plot["logos"]:
        add_logos(fig, 20)

    # add timestamp
    if to_plot["timestamp"]:
        spt = ax[0, 0].set_title("Plot last updated: "+UTCDateTime.now().ctime(),\
        fontsize=BIGGER_SIZE)

    # SAVE FIGURE
    if to_plot["savefig"]:
        figname = "{}/{}-{}-{}.png".format(to_plot["figpath"], to_plot["timelinefigname"],\
        st[0][0].stats.network, st[0][0].stats.starttime.strftime("%Y%m%d_%H%M%S"))
    else:
        figname = "{}/{}.png".format(to_plot["figpath"], to_plot["timelinefigname"])
    print("Saving figure: ", figname)
    if to_plot["timestamp"]:
        fig.savefig(figname, bbox_extra_artists=[spt], bbox_inches='tight')
    else:
        fig.savefig(figname, bbox_inches='tight')

    # SAVE RAW DATA
    if to_plot["savedata"]:
        datafile = "{}/{}-{}-{}.txt".format(to_plot["figpath"], to_plot["datafile"],\
        st[0].stats.network, st[0].stats.starttime.strftime("%Y%m%d_%H%M%S"))
        with open(datafile, "wb+") as fid:
            np.savetxt(fid, np.array([time, baz, slow]).T)

    sys.stdout.flush()

    ### polar plot of f-k space ##############################
    if to_plot["polar"]:

        print("Plotting polar plot")

        # set font sizes:
        SMALL_SIZE, MEDIUM_SIZE, BIGGER_SIZE = set_font_sizes(to_plot["polarx"], "fkpolar")
        plt.rc('font', size=SMALL_SIZE)          # controls default text sizes
        plt.rc('axes', titlesize=SMALL_SIZE)     # fontsize of the axes title
        plt.rc('axes', labelsize=MEDIUM_SIZE)    # fontsize of the x and y labels
        plt.rc('xtick', labelsize=SMALL_SIZE)    # fontsize of the tick labels
        plt.rc('ytick', labelsize=SMALL_SIZE)    # fontsize of the tick labels
        plt.rc('legend', fontsize=SMALL_SIZE)    # legend fontsize
        plt.rc('figure', titlesize=BIGGER_SIZE)  # fontsize of the figure title

#        global figp, axp, cax
#        global cmap, abins, sbins

        # create figure - add polar and colorbar axes
        figp = plt.figure(figsize=(to_plot["polarx"]/my_dpi, to_plot["polary"]/my_dpi), dpi=my_dpi)
        cax = figp.add_axes([0.85, 0.2, 0.05, 0.5])
        axp = figp.add_axes([0.10, 0.1, 0.70, 0.7], polar=True)
        # set N to up
        axp.set_theta_direction(-1)
        axp.set_theta_zero_location("N")

        # set ticks
        axp.set_xticks(np.linspace(0, 2 * np.pi, 4, endpoint=False))
        axp.set_xticklabels(['N', 'E', 'S', 'W'])

        if not to_plot["usestack"]:
            hist = []

        for n in range(narrays):

            if not to_plot["usestack"]:

                # try to remove any NaNs in relpow. First find non-NaN values
                non_nan_mask = ~np.isnan(relpow[n])
                # if all are NOT true, then we have some NaNs
                if not np.all(non_nan_mask):
                    print("Replacing NaNs in relpow")
                    relpow[n] = np.nan_to_num(relpow[n], copy=True, nan=1.0)

                # choose number of fractions in plot (desirably 360 degree/N is an integer!)
                N = to_plot["nbin_baz"] #72
                N2 = to_plot["nbin_slow"] #50

                # create the azimuth and slowness bins
                abins = np.arange(N + 1) * 360. / N
                max_slow_hist = np.ceil(1.5*2* np.max(np.abs([sll_x[n], sll_y[n],\
                    slm_x[n], slm_y[n]])))/2 # 1.5x \

                try:
                    if max_slow_hist < np.max(slow): # check values are not outside this range!
                        max_slow_hist = np.ceil(np.max(slow))
                except:
                    print(max_slow_hist)
                    print("shape(slow)=", np.shape(slow))
                    print(slow)

                # max abs value in grid, rounded up to nearest 0.5
                sbins = np.linspace(0, max_slow_hist, N2 + 1)

                # get histogram, and weight by relative power (or MCCM for LSQ)
                with concurrent.futures.ProcessPoolExecutor(max_workers=get_nproc()) as executor:
                    histi, baz_edges, sl_edges = executor.submit(np.histogram2d,\
                        baz[n], slow[n], bins=[abins, sbins], weights=relpow[n]).result()

                if to_plot["norm"]:
                    histi = histi/len(data[n])

                hist.append(histi)

            sys.stdout.flush()

            # Final check for any NaNs in hist before plotting
            non_nan_mask = ~np.isnan(hist[n])
            # if all are NOT true, then we have some NaNs
            if not np.all(non_nan_mask):
                print("Replacing NaNs with 0")
                hist[n] = np.nan_to_num(hist[n], copy=True, nan=0.0)

        # transform to radian
        baz_edges = np.radians(baz_edges)

        dh = abs(sl_edges[1] - sl_edges[0])
        dw = abs(baz_edges[1] - baz_edges[0])

        # choose colourmap
        cmap_in = obspy_sequential
        if to_plot["norm"]:
            cmap = shiftedColorMap(cmap_in, 0.0, 0.15, 1.0, linear=False)
        else:
            cmap = cmap_in

        # circle through backazimuth

        for i, row in enumerate(sum(hist)):
            if not to_plot["norm"]:
                bars = axp.bar(x=(i * dw) * np.ones(N2), height=dh * np.ones(N2), width=dw,\
                bottom=dh * np.arange(N2), color=cmap(row / sum(hist).max()))
            else:
                bars = axp.bar(x=(i * dw) * np.ones(N2), height=dh * np.ones(N2), width=dw,\
                bottom=dh * np.arange(N2), color=cmap(row))

        # set slowness limits
        for n in range(narrays):
            if (to_plot["slow_ymin"][n] != 'auto') or (to_plot["slow_ymax"][n] != 'auto'):
                slow_ymin = float(to_plot["slow_ymin"][n])
                slow_ymax = float(to_plot["slow_ymax"][n])
                axp.set_ylim(slow_ymin, slow_ymax)
                print('Warning: multiple slowness axis limits defined.')
                print('Using limits for Array', n+1, 'for polar plot')
                break
            else:
                axp.set_ylim(0, max_slow_hist)

        [i.set_color('grey') for i in axp.get_yticklabels()]

        # set colorbar limits
        if not to_plot["norm"]:
            cbar = ColorbarBase(cax, cmap=cmap, norm=Normalize(vmin=sum(hist).min(),\
                vmax=sum(hist).max()))
            normstr = ''
        else:
            cbar = ColorbarBase(cax, cmap=cmap, norm=Normalize(vmin=0, vmax=1))
            normstr = 'Normalized '

        if array_resp["lsq"]:
            cbar.set_label(normstr+'Frequency (count)', rotation=270, labelpad=15)
        else:
            cbar.set_label(normstr+'Relative Power', rotation=270, labelpad=15)

        if not to_plot["usestack"]:
            # find maxima
            max_xy = []
            max_val = []
            for n in range(narrays):
                max_xy.append(np.unravel_index(np.argmax(hist[n], axis=None), hist[n].shape))
                max_val.append(np.argmax(hist[n], axis=None))

            m = max_val.index(max(max_val))

            max_baz = abins[max_xy[m][0]]
            max_slow = sbins[max_xy[m][1]]

        maxstring = 'Max: Back azimuth {}$^\circ$, slowness = {} s/km'\
        .format(str(max_baz), str(max_slow))
        maxstring2 = 'Max: Back azimuth {}$^\circ$\n slowness = {} s/km'\
        .format(str(max_baz), str(max_slow))

        #maxstring = 'Max: Back azimuth {}$^\circ$, slowness = {} s/km'\
        #.format(str(abins[max_xy[m][0]]), str(sbins[max_xy[m][1]]))
        #maxstring2 = 'Max: Back azimuth {}$^\circ$\n slowness = {} s/km'\
        #.format(str(abins[max_xy[m][0]]), str(sbins[max_xy[m][1]]))

        axp.set_title(maxstring2, y=-0.135, fontsize=SMALL_SIZE)
        plt.figtext(0.5, 0.9, my_time_label, fontsize=MEDIUM_SIZE, horizontalalignment='center')
        #fig.tight_layout()

        # add logos
        if to_plot["logos"]:
            add_logos(figp)

        # add timestamp
        if to_plot["timestamp"]:
            figp.suptitle("Plot last updated: "+UTCDateTime.now().ctime())

        ## SAVE FIGURE
        if to_plot["savefig"]:
            figname = "{}/{}-{}-{}.png".format(to_plot["figpath"], to_plot["polarfigname"],\
            st[0][0].stats.network, st[0][0].stats.starttime.strftime("%Y%m%d_%H%M%S"))
        else:
            figname = "{}/{}.png".format(to_plot["figpath"], to_plot["polarfigname"])

        print("Saving figure: ", figname)

        figp.savefig(figname)

    ### array response function #################################

    sys.stdout.flush()

    if to_plot["resp"]:

        if to_plot["first"]: ### ONLY PLOT ONCE AS DOES NOT CHANGE

            print("Plotting array response")
            # create figure - add polar and colorbar axes
            global figa, axa
            figa = plt.figure(figsize=(to_plot["arrayx"]/my_dpi,\
            to_plot["arrayy"]/my_dpi), dpi=my_dpi)

            axa = plt.axes

            # set font sizes:
            SMALL_SIZE, MEDIUM_SIZE, BIGGER_SIZE = set_font_sizes(to_plot["arrayx"], "resp")
            plt.rc('font', size=SMALL_SIZE)          # controls default text sizes
            plt.rc('axes', titlesize=SMALL_SIZE)     # fontsize of the axes title
            plt.rc('axes', labelsize=MEDIUM_SIZE)    # fontsize of the x and y labels
            plt.rc('xtick', labelsize=SMALL_SIZE)    # fontsize of the tick labels
            plt.rc('ytick', labelsize=SMALL_SIZE)    # fontsize of the tick labels
            plt.rc('legend', fontsize=SMALL_SIZE)    # legend fontsize
            plt.rc('figure', titlesize=BIGGER_SIZE)  # fontsize of the figure title

            # get response function:
            transff, kxmin, kxmax, kymin, kymax, kstep = get_array_response(st, inv, array_resp)

            # plot
            plt.pcolor(np.arange(kxmin, kxmax + kstep * 1.1, kstep) - kstep / 2.,\
            np.arange(kymin, kymax + kstep * 1.1, kstep) - kstep / 2., transff.T,\
            cmap=obspy_sequential)

            plt.colorbar()
            plt.clim(vmin=0., vmax=1.)
            plt.xlim(kxmin, kxmax)
            plt.ylim(kymin, kymax)

            fig.tight_layout()

            plt.gca().set_aspect('equal', 'datalim')

            # add logo
            if to_plot["logos"]:
                add_logos(figa)

            if to_plot["timestamp"]:
                figp.suptitle("Plot last updated: "+UTCDateTime.now().ctime())

            ## SAVE FIGURE
            if to_plot["savefig"]:
                figname = "{}/{}-{}-{}.png".format(to_plot["figpath"], to_plot["arrayfigname"],\
                st[0].stats.network, st[0].stats.starttime.strftime("%Y%m%d_%H%M%S"))
            else:
                figname = "{}/{}.png".format(to_plot["figpath"], to_plot["arrayfigname"])
            print("Saving figure: ", figname)
            figa.savefig(figname)
            sys.stdout.flush()

    ### map showing projection of back azimuth

    sys.stdout.flush()

    if to_plot["bazmap"]:

        print("Plotting map of back azimuth projection")
        sys.stdout.flush()

        #from mpl_toolkits.basemap import Basemap
        from obspy.signal.array_analysis import get_geometry
        import cartopy.crs as ccrs
        from retreat.plot.mapping import deg2num, num2deg, get_image_cluster, displace, scale_bar

        ## plot
        figm = plt.figure(figsize=(to_plot["mapx"]/my_dpi, to_plot["mapy"]/my_dpi), dpi=my_dpi)

        # create map axes
        use_proj = ccrs.Mercator()
        axm = plt.axes(projection=use_proj)

        # set font sizes:
        SMALL_SIZE, MEDIUM_SIZE, BIGGER_SIZE = set_font_sizes(to_plot["mapx"], "map")
        plt.rc('font', size=SMALL_SIZE)          # controls default text sizes
        plt.rc('axes', titlesize=SMALL_SIZE)     # fontsize of the axes title
        plt.rc('axes', labelsize=MEDIUM_SIZE)    # fontsize of the x and y labels
        plt.rc('xtick', labelsize=SMALL_SIZE)    # fontsize of the tick labels
        plt.rc('ytick', labelsize=SMALL_SIZE)    # fontsize of the tick labels
        plt.rc('legend', fontsize=SMALL_SIZE)    # legend fontsize
        plt.rc('figure', titlesize=BIGGER_SIZE)  # fontsize of the figure title

        geom = []
        array_lats = []
        array_lons = []

        for n in range(narrays):
            # use get_geometry to find centre of arrays:
            geoms = get_geometry(st[n], coordsys='lonlat', return_center=True)
            geom.append(geoms)
            array_lons.append(geoms[-1, 0]) # x-coord
            array_lats.append(geoms[-1, 1]) # y-coord

        # get midpoint (centroid) - assume locally flat and just average lat/lon for now
        array_lon = np.mean(array_lons)
        array_lat = np.mean(array_lats)

        if to_plot["map_array_centre"]: # array at centre
            print('Midpoint (centroid) of arrays at centre of map')
            sys.stdout.flush()

            # define lat/lon limits using array centre and a radius (in km)
            my_radius = to_plot["map_array_radius"] # km

            lon_min = displace(array_lon, array_lat, 270, my_radius)[1] # min lon, due W of array
            lat_min = displace(array_lon, array_lat, 180, my_radius)[0] # min lat, due S of array
            lon_max = displace(array_lon, array_lat, 90, my_radius)[1] # min lon, due E of array
            lat_max = displace(array_lon, array_lat, 0, my_radius)[0] # max lat, due N of array

            # get differences/extent of map:
            delta_lat = lat_max - lat_min
            delta_lon = lon_max - lon_min

            # check if any NON-auto values:
            if any(to_plot[key] != 'auto' for key in ['lat_min', 'lat_max', 'lon_min', 'lon_max']):
                print('Warning - you have specified array at centre with manual map extent')
                if not all(to_plot[key] != 'auto' for key in ['lat_min', 'lat_max', 'lon_min',\
                'lon_max']):
                    raise Exception('Error! You must specify ALL 4 limits')
#                else:
#                    print('OK')

                # check and use manually defined value(s)
                if to_plot["lat_min"] != 'auto':
                    lat_min = float(to_plot["lat_min"])
                if to_plot["lat_max"] != 'auto':
                    lat_max = float(to_plot["lat_max"])
                if to_plot["lon_min"] != 'auto':
                    lon_min = float(to_plot["lon_min"])
                if to_plot["lon_max"] != 'auto':
                    lon_max = float(to_plot["lon_max"])

                # get differences/extent of map:
                delta_lat = lat_max-lat_min
                delta_lon = lon_max-lon_min
                my_radius = (delta_lat/2)*111.32 # convert degrees to km
                # APPROX. This is fine for the radius calculation for the line

        else: # array NOT at centre
            print('Manually defined map extent')
            sys.stdout.flush()
#           # check if any AUTO values:
            for key in ['lat_min', 'lat_max', 'lon_min', 'lon_max']:
                if to_plot[key] == 'auto':
                    raise Exception('Error! If array NOT at the map centre, \
                    all 4 lat/lon limits MUST be specified')

                if to_plot["lat_min"] != 'auto':
                    lat_min = float(to_plot["lat_min"])
                if to_plot["lat_max"] != 'auto':
                    lat_max = float(to_plot["lat_max"])
                if to_plot["lon_min"] != 'auto':
                    lon_min = float(to_plot["lon_min"])
                if to_plot["lon_max"] != 'auto':
                    lon_max = float(to_plot["lon_max"])

            # get differences/extent of map:
            delta_lat = lat_max - lat_min
            delta_lon = lon_max - lon_min

            # convert degrees to km - very APPROX. But this is fine for the radius calculation
            # only used to get zoom level
            mean_lat = (lat_min+lat_max)/2
            delta_x = 111.11*np.cos(mean_lat*np.pi/180)*delta_lon
            delta_y = 111.11*delta_lat
            my_radius = ((delta_x/2)**2 + (delta_y/2)**2)**(1./2)

        # GET OpenTopo zoom level:
        zoom = int(round(7.12*np.exp(-0.0357*my_radius)+6.46)) #WARNING-empirically derived formula!
        #print(zoom)

        ### create image - fetch tiles from osm tileserver
        print('Fetching tiles')
        sys.stdout.flush()
        im, bbox = get_image_cluster(lat_min, lon_min, delta_lat, delta_lon, zoom, to_plot)
        print('Complete')
        sys.stdout.flush()
        # get map extent in UTM
        llcrnr, urcrnr = use_proj.transform_points(ccrs.Geodetic(),\
            np.array([bbox[0], bbox[2]]), np.array([bbox[1], bbox[3]]))

        imextent = [llcrnr[0], urcrnr[0], llcrnr[1], urcrnr[1]]

        # plot tiles:
        axm.imshow(im, origin='upper', extent=imextent, transform=use_proj)

        # coords of centre of arrays in UTM
        x, y = use_proj.transform_point(array_lon, array_lat, ccrs.Geodetic(),)

        # coords of new limits based on desired radius
        xmin, ymin = use_proj.transform_point(lon_min, lat_min, ccrs.Geodetic())
        xmax, ymax = use_proj.transform_point(lon_max, lat_max, ccrs.Geodetic())

        xa = []
        ya = []
        for n in range(narrays):
            # each array centre coords in UTM
            xxa, yya = use_proj.transform_point(array_lons[n], array_lats[n], ccrs.Geodetic(),)
            xa.append(xxa)
            ya.append(yya)

            # plot arrays
            axm.scatter(xa, ya, marker='v', alpha=0.9, c='r')

        if to_plot["first"]:
            ###### save as basemap for future cycles
            figname = "{}/{}.png".format(to_plot["figpath"], "basemap")
            print("Saving basemap: ", figname)
            im.save(figname)
            ########
        sys.stdout.flush()

        baz_err = np.array([])
        for n in range(narrays):

            # plot back azimuth line
            baz = abins[max_xy[n][0]] # this just returns the lower EDGE of the cell
            dw_deg = dw*180/np.pi
            baz = baz + dw_deg/2 # add half the step to get midpoint of cell

            # ERRORS - NB still need to come up with a satisfactory way of dealing with this
            # in a rigorous and representative way.

            if array_resp["lsq"][n]: # use mean of azimuth errors from LSQ beamforming
                baz_err = np.append(baz_err, np.mean(err_baz[n]))
                # This average across the WHOLE timeseries is likely, conservatively,
                # to be larger than the error for any well/better constrained transients
            else:
                #For now, use the following illustrative error:
                baz_err = np.append(baz_err, 2*(dw*180)/(2*np.pi))
                # i.e. n*the resolution of the angle step in histogram (in degrees).

            # calculate the length of the line (will be different for each array)
            delta_array_x = np.max(np.abs((xa[n]-xmin, xa[n]-xmax)))
            delta_array_y = np.max(np.abs((ya[n]-ymin, ya[n]-ymax)))
            line_radius = np.sqrt((delta_array_x**2 + delta_array_x**2))

            # create points to join with line- centre of array to edge point
            #xx = [x, x+line_radius*np.sin(baz*np.pi/180)]
            #yy = [y, y+line_radius*np.cos(baz*np.pi/180)]
            xx = [xa[n], xa[n]+line_radius*np.sin(baz*np.pi/180)]
            yy = [ya[n], ya[n]+line_radius*np.cos(baz*np.pi/180)]

            # define error as filled triangle:
            xerr = [xa[n], xa[n]+line_radius*np.sin((baz-baz_err[n])*np.pi/180),\
            xa[n]+line_radius*np.sin((baz+baz_err[n])*np.pi/180)]
            yerr = [ya[n], ya[n]+line_radius*np.cos((baz-baz_err[n])*np.pi/180),\
            ya[n]+line_radius*np.cos((baz+baz_err[n])*np.pi/180)]

            # plot error cone
            mycone = axm.fill(xerr, yerr, c='lightgrey', alpha=0.5)

            # plot line
            myline = axm.plot(xx, yy, 'g-')

        # crop axes to limits
        axm.set_xlim([xmin, xmax])
        axm.set_ylim([ymin, ymax])

        # scale bar
        dref = 10**np.floor(np.log10(my_radius))
        scale_bar(axm, dref, (0.5, 0.025))

        axm.set_title(maxstring, y=-0.065, fontsize=SMALL_SIZE)
        plt.figtext(0.5, 0.9, my_time_label, fontsize=MEDIUM_SIZE, horizontalalignment='center')

        # add logo
        if to_plot["logos"]:
            add_logos(figm)

        # add timestamp
        if to_plot["timestamp"]:
            figm.suptitle("Plot last updated: "+UTCDateTime.now().ctime())

        ## SAVE FIGURE
        if to_plot["savefig"]:
            figname = "{}/{}-{}-{}.png".format(to_plot["figpath"], to_plot["mapfigname"],\
            st[0][0].stats.network, st[0][0].stats.starttime.strftime("%Y%m%d_%H%M%S"))
        else:
            figname = to_plot["figpath"] + to_plot["mapfigname"] + ".png"

        print("Saving figure: ", figname)

        figm.savefig(figname)

###########################################################################
# END OF PLOTTING
###########################################################################

    plt.close('all')
    gc.collect()
    del gc.garbage[:]
    gc.collect()
    sys.stdout.flush()
    # end function
    return
