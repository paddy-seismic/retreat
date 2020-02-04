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

def update_plot(st, data, to_plot, spectro, inv, array_resp, logfile):
    """Updates output figures in the figure window based on the latest data"""

    # redirect output to log file:
    sys.stdout = open(logfile, 'a+')
    sys.stderr = sys.stdout

    # split data matrix
    time = data[:, 0]
    relpow = data[:, 1]
    abspow = data[:, 2]
    baz = data[:, 3]
    slow = data[:, 4]

    # make output human readable, adjust backazimuth to values between 0 and 360
    baz[baz < 0.0] += 360

    ### MAIN TIMELINE ######################################

    # process "to_plot" arg to get what to plot
    nsubplots = sum([value for key, value in to_plot.items() if key not in\
    ('polar', 'rmes_ovlp', 'rmes_wind', 'resp', 'timelinex', 'timeliney', 'arrayx', 'timestamp',\
    'arrayy', 'polarx', 'polary', 'slow_ymin', 'slow_ymax', 'baz_ymin', 'baz_ymax', 'usestack',\
    'rms_ymin', 'rms_ymax', 'seis_ymin', 'seis_ymax', 'savefig', 'figpath', 'webfigs',\
    'map_array_radius', 'bazmap', 'mapx', 'mapy', 'map_array_centre', 'mapfigname', 'lat_min',\
    'lat_max', 'lon_min', 'lon_max', 'nbin_baz', 'nbin_slow', 'timelinefigname', 'polarfigname',\
    'arrayfigname', 'logos', 'savedata', 'datafile', 'first')])

    print("Number of subplots selected = ", nsubplots)

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

    # initialise/reset subplot index
    aindex = 0

    pstart = st[0].stats.starttime.matplotlib_date
    pend = st[0].stats.endtime.matplotlib_date

    my_time_label = st[0].stats.starttime.strftime('%d-%b-%Y %H:%M:%S%Z') + ' to ' +\
    st[0].stats.endtime.strftime('%d-%b-%Y %H:%M:%S%Z')

    my_xlabel = 'Time [UTC] ' + st[0].stats.starttime.strftime('%d-%b-%Y')

#    fig.clf()

    if to_plot["baz"]:
        # plot backazimuths
        print("Plotting back azimuths")
        ax[aindex, 0].cla()
        ax[aindex, 0].scatter(time, baz, c=slow, alpha=0.6, edgecolors='none')
        ax[aindex, 0].set_xlim(pstart, pend)

        if (to_plot["baz_ymin"] != 'auto') or (to_plot["baz_ymax"] != 'auto'):
            baz_ymin = float(to_plot["baz_ymin"])
            baz_ymax = float(to_plot["baz_ymax"])
            ax[aindex, 0].set_ylim(baz_ymin, baz_ymax)

        ax[aindex, 0].xaxis.set_major_locator(xlocator)
        ax[aindex, 0].xaxis.set_major_formatter(mdates.AutoDateFormatter(xlocator))
        ax[aindex, 0].set_ylabel('Back Azimuth [$^\circ$]')
        if (aindex+1) == nsubplots:
            ax[aindex, 0].set_xlabel(my_xlabel)
        aindex = aindex + 1

    if to_plot["slow"]:
        # plot slowness
        print("Plotting slowness")
        ax[aindex, 0].cla()
        ax[aindex, 0].scatter(time, slow)
        ax[aindex, 0].set_xlim(pstart, pend)

        if (to_plot["slow_ymin"] != 'auto') or (to_plot["slow_ymax"] != 'auto'):
            slow_ymin = float(to_plot["slow_ymin"])
            slow_ymax = float(to_plot["slow_ymax"])
            ax[aindex, 0].set_ylim(slow_ymin, slow_ymax)
        else:
            ax[aindex, 0].set_ylim(0, 1.05*max(slow))

        ax[aindex, 0].xaxis.set_major_locator(xlocator)
        ax[aindex, 0].xaxis.set_major_formatter(mdates.AutoDateFormatter(xlocator))
        ax[aindex, 0].set_ylabel('Slowness [skm$^{-1}$]')
        if (aindex+1) == nsubplots:
            ax[aindex, 0].set_xlabel(my_xlabel)
        aindex = aindex + 1

    if to_plot["usestack"]: # calculate stack to plot
        from retreat.data.stack import stack
        # try to remove any bad traces first:
        prestack = Stream()
        for tr in st:
#            print(tr.stats.station, tr.stats.starttime,'-',tr.stats.endtime)
            if not np.any(np.isnan(tr.data)):
                prestack.append(tr)
        # use simple linear stack for now
        try:
        # allow 30 seconds difference in trace length (realtime lag)
            mystack = stack(prestack, npts_tol=30*prestack[0].stats.sampling_rate, time_tol=1.0)
            # check for bad data/NaN:
            if np.any(np.isnan(mystack[0].data)):
                print('Warning, bad data in stack - reverting to first station in array')
                mystack[0] = st[0]
#            print('stack', mystack[0].stats.starttime,'-',tr.stats.endtime)
        except ValueError:
            to_plot["usestack"] = False

    if to_plot["rmes"]:
        # plot RMeS / envelope
        print("Plotting RMeS")
        ax[aindex, 0].cla()

        if to_plot["usestack"]:
            with concurrent.futures.ProcessPoolExecutor(max_workers=get_nproc()) as executor:
                rmes, rtimes = executor.submit(window_rmes, mystack[0], to_plot["rmes_wind"],\
                to_plot["rmes_ovlp"], logfile).result()
        else:
            with concurrent.futures.ProcessPoolExecutor(max_workers=get_nproc()) as executor:
                rmes, rtimes = executor.submit(window_rmes, st[0], to_plot["rmes_wind"],\
                to_plot["rmes_ovlp"], logfile).result()

        ax[aindex, 0].plot(rtimes, rmes)
        ax[aindex, 0].set_xlim(pstart, pend)

        if (to_plot["rms_ymin"] != 'auto') or (to_plot["rms_ymax"] != 'auto'):
            rms_ymin = float(to_plot["rms_ymin"])
            rms_ymax = float(to_plot["rms_ymax"])
            ax[aindex, 0].set_ylim(rms_ymin, rms_ymax)

        ax[aindex, 0].xaxis.set_major_locator(xlocator)
        ax[aindex, 0].xaxis.set_major_formatter(mdates.AutoDateFormatter(xlocator))
        ax[aindex, 0].set_ylabel('RMeS Velocity [ms$^{-1}$]')
        #ax[aindex,0].ticklabel_format(axis='y', style='sci')
        ax[aindex, 0].yaxis.set_major_formatter(mtick.FormatStrFormatter('%.1e'))
        if (aindex+1) == nsubplots:
            ax[aindex, 0].set_xlabel(my_xlabel)
        aindex = aindex + 1

    if to_plot["seis"]:
        # plot seismogram
        print("Plotting waveform")
        ax[aindex, 0].cla()

        if to_plot["usestack"]:
            ax[aindex, 0].plot(mystack[0].times(type="matplotlib"), mystack[0].data, 'k')
        else:
            ax[aindex, 0].plot(st[0].times(type="matplotlib"), st[0].data, 'k')

        ax[aindex, 0].set_xlim(pstart, pend)

        if (to_plot["seis_ymin"] != 'auto') or (to_plot["seis_ymax"] != 'auto'):
            seis_ymin = float(to_plot["seis_ymin"])
            seis_ymax = float(to_plot["seis_ymax"])
            ax[aindex, 0].set_ylim(seis_ymin, seis_ymax)

        ax[aindex, 0].xaxis.set_major_locator(xlocator)
        ax[aindex, 0].xaxis.set_major_formatter(mdates.AutoDateFormatter(xlocator))
        ax[aindex, 0].set_ylabel('Velocity [ms$^{-1}$]')

        ax[aindex, 0].yaxis.set_major_formatter(mtick.FormatStrFormatter('%.1e'))
        #
        if (aindex+1) == nsubplots:
            ax[aindex, 0].set_xlabel(my_xlabel)

        aindex = aindex + 1

    if to_plot["spec"]:
        # plot spectrogram
        print("Plotting spectrogram")
        global sfmin, sfmax, vmax
        if to_plot["first"]:
            sfmin = spectro["fmin"]
            sfmax = spectro["fmax"]

            del spectro["fmin"]
            del spectro["fmax"]

        ax[aindex, 0].cla()
        spectro["axes"] = ax[aindex, 0]

        # CALCULATE SPECTROGRAM
        if to_plot["usestack"]:
            mystack[0].spectrogram(**spectro)
        else:
            st[0].spectrogram(**spectro)
        # Grab image for manipulation
        im = ax[aindex, 0].images[0]

        # convert x-axis to absolute time:
        ext = list(im.get_extent())
        for ll in range(2):
            ext[ll] = ext[ll]/(60.*60*24) + pstart
        tuple(ext)
        im.set_extent(ext)

        # set colorscale limits
        clip = spectro["clip"]
        _range = float(im.get_array().max() - im.get_array().min())
        vmin = im.get_array().min() + clip[0] * _range
        vmax = im.get_array().min() + clip[1] * _range
        im.set_clim(vmin=vmin, vmax=vmax)

        # axis limts
        ax[aindex, 0].set_ylim(sfmin, sfmax)
        ax[aindex, 0].set_xlim(pstart, pend)

        ax[aindex, 0].xaxis.set_major_locator(xlocator)
        ax[aindex, 0].xaxis.set_major_formatter(mdates.AutoDateFormatter(xlocator))
        ax[aindex, 0].set_ylabel('Frequency [Hz]')

        if (aindex+1) == nsubplots:
            ax[aindex, 0].set_xlabel(my_xlabel)

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
        st[0].stats.network, st[0].stats.starttime.strftime("%Y%m%d_%H%M%S"))
    else:
        figname = to_plot["figpath"] + to_plot["timelinefigname"] + ".png"
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

        # choose number of fractions in plot (desirably 360 degree/N is an integer!)
        N = to_plot["nbin_baz"] #72
        N2 = to_plot["nbin_slow"] #50

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

        # create the azimuth and slowness bins
        abins = np.arange(N + 1) * 360. / N
        sbins = np.linspace(0, 3, N2 + 1)

        with concurrent.futures.ProcessPoolExecutor(max_workers=get_nproc()) as executor:
            hist, baz_edges, sl_edges = executor.submit(np.histogram2d,\
            baz, slow, bins=[abins, sbins], weights=relpow).result()

        # transform to radian
        baz_edges = np.radians(baz_edges)

        dh = abs(sl_edges[1] - sl_edges[0])
        dw = abs(baz_edges[1] - baz_edges[0])

        # choose colourmap
        cmap = obspy_sequential

        # circle through backazimuth
        #axp.cla()

        for i, row in enumerate(hist):
            bars = axp.bar(x=(i * dw) * np.ones(N2), height=dh * np.ones(N2), width=dw,\
            bottom=dh * np.arange(N2), color=cmap(row / hist.max()))

        # set slowness limits
        axp.set_ylim(0, 1)
        [i.set_color('grey') for i in axp.get_yticklabels()]

        # set colorbar limits
        cbar = ColorbarBase(cax, cmap=cmap, norm=Normalize(vmin=hist.min(), vmax=hist.max()))
        cbar.set_label('Relative Power', rotation=270, labelpad=15)

        # find maximum
        max_xy = np.unravel_index(np.argmax(hist, axis=None), hist.shape)
        maxstring = 'Max: Back azimuth {}$^\circ$, slowness = {} s/km'\
        .format(str(abins[max_xy[0]]), str(sbins[max_xy[1]]))
        maxstring2 = 'Max: Back azimuth {}$^\circ$\n slowness = {} s/km'\
        .format(str(abins[max_xy[0]]), str(sbins[max_xy[1]]))
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
            st[0].stats.network, st[0].stats.starttime.strftime("%Y%m%d_%H%M%S"))
        else:
            figname = to_plot["figpath"] + to_plot["polarfigname"] + ".png"

        print("Saving figure: ", figname)

        figp.savefig(figname)

    ### array response function #################################

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
                figname = to_plot["figpath"] + to_plot["arrayfigname"] + ".png"

            print("Saving figure: ", figname)
            figa.savefig(figname)

    ### map showing projection of back azimuth

    if to_plot["bazmap"]:

        print("Plotting map of back azimuth projection")

        from retreat.plot.mapping import deg2num, num2deg, get_image_cluster, displace
        from mpl_toolkits.basemap import Basemap
        from obspy.signal.array_analysis import get_geometry

        #global figm, axm
        figm = plt.figure(figsize=(to_plot["mapx"]/my_dpi, to_plot["mapy"]/my_dpi), dpi=my_dpi)
        axm = plt.axes()

        # set font sizes:
        SMALL_SIZE, MEDIUM_SIZE, BIGGER_SIZE = set_font_sizes(to_plot["mapx"], "map")
        plt.rc('font', size=SMALL_SIZE)          # controls default text sizes
        plt.rc('axes', titlesize=SMALL_SIZE)     # fontsize of the axes title
        plt.rc('axes', labelsize=MEDIUM_SIZE)    # fontsize of the x and y labels
        plt.rc('xtick', labelsize=SMALL_SIZE)    # fontsize of the tick labels
        plt.rc('ytick', labelsize=SMALL_SIZE)    # fontsize of the tick labels
        plt.rc('legend', fontsize=SMALL_SIZE)    # legend fontsize
        plt.rc('figure', titlesize=BIGGER_SIZE)  # fontsize of the figure title

        # use get_geometry to find centre of array:
        geom = get_geometry(st, coordsys='lonlat', return_center=True)

        array_lon = geom[-1, 0] # x-coord
        array_lat = geom[-1, 1] # y-coord

        if to_plot["map_array_centre"]: # array at centre
            print('Array at centre')
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
                    print('Error! You must specify ALL 4 limits')
                    raise Exception
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
            print('Manually defined extent')
#           # check if any AUTO values:
            for key in ['lat_min', 'lat_max', 'lon_min', 'lon_max']:
                if to_plot[key] == 'auto':
                    print('Error! If array NOT at the map centre, \
                    all 4 lat/lon limits MUST be specified')
                    raise Exception

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
        im, bbox = get_image_cluster(lat_min, lon_min, delta_lat, delta_lon, zoom, to_plot)

        ## plot
        #axm = plt.subplot(111)
        m = Basemap(
            llcrnrlon=bbox[0], llcrnrlat=bbox[1],
            urcrnrlon=bbox[2], urcrnrlat=bbox[3],
            projection='merc',
            ax=axm
        )
        m.imshow(im, interpolation='lanczos', origin='upper')
        x, y = m(array_lon, array_lat)

        xmin, ymin = m(lon_min, lat_min)
        xmax, ymax = m(lon_max, lat_max)

        # plot array centre
        axm.scatter(x, y, marker='v', alpha=0.9, c='r')

        if to_plot["first"]:
            ###### save as basemap for future cycles
            figname = to_plot["figpath"] + "basemap.png"
            print("Saving basemap: ", figname)
            im.save(figname)
            ########

        # plot back azimuth line
        baz = abins[max_xy[0]]
        baz_err = 3.0 # e.g.

        # calculate the length of the line
        if to_plot["map_array_centre"]: # array at centre
            line_radius = (xmax-xmin)/np.sqrt(2) # as we already know it's a square in Cartesian..

        else: # array NOT at centre
            # Now radius depends on position of array AND shape of map:
            delta_array_x = np.max(np.abs((x-xmin, x-xmax)))
            delta_array_y = np.max(np.abs((y-ymin, y-ymax)))
            line_radius = (delta_array_x**2 + delta_array_x**2)**(1./2)

        # create points to join with line- centre of array to edge point
        xx = [x, x+line_radius*np.sin(baz*np.pi/180)]
        yy = [y, y+line_radius*np.cos(baz*np.pi/180)]

        # define error as filled triangle:
        xerr = [x, x+line_radius*np.sin((baz-baz_err)*np.pi/180),\
        x+line_radius*np.sin((baz+baz_err)*np.pi/180)]
        yerr = [y, y+line_radius*np.cos((baz-baz_err)*np.pi/180),\
        y+line_radius*np.cos((baz+baz_err)*np.pi/180)]

        # plot error cone
        mycone = axm.fill(xerr, yerr, c='white', alpha=0.5)

        # plot line
        myline = axm.plot(xx, yy, 'g-')

        # scale bar
        dref = 10**np.floor(np.log10(my_radius))
        distance = dref/np.cos(array_lat*np.pi/180)
        scale = m.drawmapscale(displace(array_lon, array_lat, 215, my_radius)[1],\
        displace(array_lon, array_lat, 215, my_radius)[0], array_lon, array_lat, distance,\
        barstyle='fancy', units='km')
        scale[12].set_text(dref/2)
        scale[13].set_text(dref)

        # crop axes to limits
        axm.set_xlim([xmin, xmax])
        axm.set_ylim([ymin, ymax])

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
            st[0].stats.network, st[0].stats.starttime.strftime("%Y%m%d_%H%M%S"))
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
    # end function
    return
