"""get_param"""
from obspy.core import UTCDateTime
import numpy as np

def get_param(gui_input):
    """Reads and returns input parameters from the GUI window"""

    #### timing options
    # need to define some dependent variables outside dictionary
    window_length = float(gui_input["window_length"])
    prebuf = float(gui_input["prebuf"])

    ###################### REAL TIME ###########################
#    tstart = UTCDateTime()

    ### SPECIFIC date/time for TESTING #####
#    tstart = UTCDateTime("2019-06-24T03:50:00")

    #####  FROM GUI
    # first check the start time
    if not gui_input["tstart"] or gui_input["tstart"].casefold() == "now":
        print('NOW or no start time specified. Using current time')
        tstart = UTCDateTime() # use current time
    else:
        try:
            tstart = UTCDateTime(gui_input["tstart"])
        except Exception as e:
            print(e)
            print('Invalid Start time format. Using current time.')
            tstart = UTCDateTime()
    # now check the end time
    if gui_input["tstop"]:
        try:
            tstop = UTCDateTime(gui_input["tstop"])
            if tstop <= tstart:
                raise Exception('Error. End time must be later than start time')
        except Exception as e:
            raise Exception('Invalid End time format:',e) from e

    if type(tstart).__name__ != 'UTCDateTime':
        print('Invalid Start time format. Using current time.')
        tstart = UTCDateTime()

    ##### # TIMING
    timing = dict(
        # OVERALL length of time window to display on plots
        plot_window=float(gui_input["plot_window"]), # in seconds
        ### round down to nearest n minutes for tidiness
        # nmin = mins_to_round_to,
        tstart=tstart,
        tstop=gui_input["tstop"],
        # length of time window to grab and process each update
        window_length=window_length, # in SECONDS
        ##### ASSUME FOR NOW THIS IS THE SAME AS THE WINDOW LENGTH
        # update interval
        update_interval=float(gui_input["update_interval"]), #in SECONDS
        fill_on_start=gui_input["fill_on_start"], # backfill entire plot window on startup
        prebuf=prebuf,
        # maximum real-time latency
        max_realtime_latency=float(gui_input["max_realtime_latency"]), # in seconds
    )

    #####  waveform data

    mydata = dict(
        t=tstart - (window_length + prebuf),
        # SCNL
        scnl=dict(S=gui_input["S"], C=gui_input["C"], N=gui_input["N"], L=gui_input["L"]),
        scnl_supply=gui_input["scnl_supply"],
        scnl_file=gui_input["scnl_file"],
        ## realtime source
        myclient=gui_input["myclient"],
        connection=gui_input["connection"],
        ## replay source
        replay=gui_input["replay"],
        sds_root=gui_input["sds_root"],
        sds_type=gui_input["sds_type"],
        dataformat=gui_input["dataformat"],
        customfmt=gui_input["customfmt"],
        myFMTSTR=gui_input["myFMTSTR"],
        ## metadata
        inv_supply=gui_input["inv_supply"],
        inv_file=gui_input["inv_file"],
        inv_type=gui_input["inv_type"],
    )

    #####  pre-processing parameters

    preproc = dict(
        # gaps
        check_gaps=gui_input["check_gaps"],
        min_nchan=int(gui_input["min_nchan"]),
        max_gap_size=float(gui_input["max_gap_size"]),
        max_gap_ends=float(gui_input["max_gap_ends"]),
        # detrending options
        zcomps=gui_input["zcomps"],
        demean=gui_input["demean"],
        linear=gui_input["detrend"],
        # taper
        taper=gui_input["taper"],
        taper_pc=float(gui_input["taper_pc"]),
        # prefiltering
        prefilt=gui_input["prefilt"],
        Fmin=float(gui_input["Fmin"]),
        Fmax=float(gui_input["Fmax"]),
        # decimation
        decimate=gui_input["decimate"],
        newfreq=float(gui_input["newfreq"]),
        # response
        removeresponse=gui_input["removeresponse"],
        # filtering
        bandpass=gui_input["bandpass"],
    )

    #####  array processing parameters

    kwargs = dict(
        # slowness grid: X min, X max, Y min, Y max, Slow Step
        sll_x=float(gui_input["sll_x"]), slm_x=float(gui_input["slm_x"]),\
        sll_y=float(gui_input["sll_x"]), slm_y=float(gui_input["slm_y"]),\
        sl_s=float(gui_input["sl_s"]),
        # sliding window properties
        win_len=float(gui_input["win_len"]),
        win_frac=1.0-float(gui_input["win_frac"]), #NB obspy array_processing uses..
        # ..fraction for STEP not overlap
        # frequency properties
        frqlow=float(gui_input["frqlow"]), frqhigh=float(gui_input["frqhigh"]),\
        prewhiten=int(gui_input["prewhiten"]),
        # restrict output
        semb_thres=float(gui_input["semb_thresh"]), vel_thres=float(gui_input["vel_thresh"]),
        stime=None,
        etime=None,
        store=None,
        verbose=False,
        method=0, # 0 = beamforming, 1 = capon (for f-k)
    )

    #####  plotting parameters
    to_plot = dict(
        baz=gui_input["baz"],
        slow=gui_input["slow"],
        relpow=gui_input["relpow"],
        seis=gui_input["seis"],
        spec=gui_input["spec"],
        rmes=gui_input["rmes"],
        rmes_wind=float(gui_input["rmes_wind"]),
        rmes_ovlp=float(gui_input["rmes_ovlp"]),
        polar=gui_input["polar"],
        resp=gui_input["resp"],
        bazmap=gui_input["bazmap"],
        timelinex=int(gui_input["timelinex"]),
        timeliney=int(gui_input["timeliney"]),
        slow_ymin=gui_input["slow_ymin"],
        slow_ymax=gui_input["slow_ymax"],
        baz_ymin=gui_input["baz_ymin"],
        baz_ymax=gui_input["baz_ymax"],
        rms_ymin=gui_input["rms_ymin"],
        rms_ymax=gui_input["rms_ymax"],
        seis_ymin=gui_input["seis_ymin"],
        seis_ymax=gui_input["seis_ymax"],
        relpow_ymin=gui_input["relpow_ymin"],
        relpow_ymax=gui_input["relpow_ymax"],
        norm=gui_input["norm"],
        polarx=int(gui_input["polarx"]),
        polary=int(gui_input["polary"]),
        arrayx=int(gui_input["arrayx"]),
        arrayy=int(gui_input["arrayy"]),
        mapx=int(gui_input["mapx"]),
        mapy=int(gui_input["mapy"]),
        map_array_radius=float(gui_input["map_array_radius"]),
        map_array_centre=gui_input["map_array_centre"],
        lat_min=gui_input["lat_min"],
        lat_max=gui_input["lat_max"],
        lon_min=gui_input["lon_min"],
        lon_max=gui_input["lon_max"],
        nbin_baz=int(gui_input["nbin_baz"]),
        nbin_slow=int(gui_input["nbin_slow"]),
        timestamp=gui_input["timestamp"],
        usestack=gui_input["usestack"],
        savefig=gui_input["savefig"],
        webfigs=gui_input["webfigs"],
        logos=gui_input["logos"],
        figpath=gui_input["figpath"],
        timelinefigname=gui_input["timelinefigname"],
        polarfigname=gui_input["polarfigname"],
        arrayfigname=gui_input["arrayfigname"],
        mapfigname=gui_input["mapfigname"],
        savedata=gui_input["savedata"],
        datafile=gui_input["datafile"],
        first=True, # do NOT adjust this!
    )

    spectro = dict(
        fmin=float(gui_input["fmin"]),
        fmax=float(gui_input["fmax"]),
        axes=None,
        wlen=float(gui_input["wlen"]),
        per_lap=float(gui_input["per_lap"]),
        show=True,
        cmap=gui_input["cmap"],
        clip=[float(gui_input["clim1"]), float(gui_input["clim2"])],
        dbscale=True,
    )

    array_resp = dict(
        coordsys='lonlat',
        klim=float(gui_input["klim"]),
        kstep_factor=1./(float(gui_input["kstep"])),
        elev_in_m=gui_input["elev_in_m"],
        scnl=mydata["scnl"],
        myclient=mydata["myclient"],
        lsq=gui_input["lsq"], # Use Least-Squares inversion/beamforming instead of f-k
    )

    #### SANITY CHECKS:

    if to_plot["resp"] and to_plot["bazmap"]:
        raise Exception("Error: Too many figures selected. \
            Please choose either array response OR map view to plot")

    if to_plot["bazmap"] and not to_plot["polar"]:
        raise Exception("Error: polar plot is required for map in order to\
            calculate histogram to determine peak back azimuth")

    if not mydata["replay"]:

        # window length
        if window_length > timing["plot_window"]:
            raise Exception('Error: window_length should be LESS than plot_window')

        # prebuffer
        if prebuf > window_length:
            raise Exception('Error: prebuffer should be LESS than window_length')

    if not to_plot["map_array_centre"]: # array NOT at centre
        for key in ['lat_min', 'lat_max', 'lon_min', 'lon_max']:
            if to_plot[key] == 'auto':
                raise Exception('Error! If array NOT at the map centre, all 4 lat/lon \
                    limits MUST be specified')

    return timing, mydata, preproc, kwargs, to_plot, spectro, array_resp

#################################################################
##### TWO ARRAYS CASE ###########################################
#################################################################

def get_param2(gui_input,narrays,cmd):
    """Reads and returns input parameters from the GUI window for
    two array case"""
    from retreat.defaults.rearrange_defaults import rearrange_gui

    if not cmd:
        # rerrange input from gui_input
        gui_input = rearrange_gui(gui_input)

    ### timing options
    # need to define some dependent variables outside dictionary
    window_length = float(gui_input["window_length"])
    prebuf = float(gui_input["prebuf"])

    ###################### REAL TIME ###########################

    #####  FROM GUI
    # first check the start time
    if not gui_input["tstart"] or gui_input["tstart"].casefold() == "now":
        print('NOW or no start time specified. Using current time')
        tstart = UTCDateTime() # use current time
    else:
        try:
            tstart = UTCDateTime(gui_input["tstart"])
        except Exception as e:
            print(e)
            print('Invalid Start time format. Using current time.')
            tstart = UTCDateTime()
    # now check the end time
    if gui_input["tstop"]:
        try:
            tstop = UTCDateTime(gui_input["tstop"])
            if tstop <= tstart:
                raise Exception('Error. End time must be later than start time')
        except Exception as e:
            raise Exception('Invalid End time format:',e) from e

    if type(tstart).__name__ != 'UTCDateTime':
        print('Invalid Start time format. Using current time.')
        tstart = UTCDateTime()

    ##### # TIMING
    timing = dict(
        # OVERALL length of time window to display on plots
        plot_window=float(gui_input["plot_window"]), # in seconds
        ### round down to nearest n minutes for tidiness
        # nmin = mins_to_round_to,
        tstart=tstart,
        tstop=gui_input["tstop"],
        # length of time window to grab and process each update
        window_length=window_length, # in SECONDS
        ##### ASSUME FOR NOW THIS IS THE SAME AS THE WINDOW LENGTH
        # update interval
        update_interval=float(gui_input["update_interval"]), #in SECONDS
        fill_on_start=gui_input["fill_on_start"], # backfill entire plot window on startup
        prebuf=prebuf,
        # maximum real-time latency
        max_realtime_latency=float(gui_input["max_realtime_latency"]), # in seconds
    )

    #####  waveform data

    # process SCNLs
    scnls=[]
    for n in range(narrays):
        scnls.append(dict(S=gui_input["S"][n], C=gui_input["C"][n], \
            N=gui_input["N"][n], L=gui_input["L"][n]))
    #scnl1=dict(S=gui_input["S"], C=gui_input["C"], N=gui_input["N"], L=gui_input["L"])
    #scnl2=dict(S=gui_input["S2"], C=gui_input["C2"], N=gui_input["N2"], L=gui_input["L2"])

    mydata = dict(
        t=tstart - (window_length + prebuf),
        # SCNL
        #scnl=[scnl1,scnl2],
        #scnl_supply=[gui_input["scnl_supply"],gui_input["scnl_supply2"]],
        #scnl_file=[gui_input["scnl_file"],gui_input["scnl_file2"]],
        scnl=scnls,
        scnl_supply=gui_input["scnl_supply"],
        scnl_file=gui_input["scnl_file"],
        ## realtime source
        myclient=gui_input["myclient"],
        connection=gui_input["connection"],
        ## replay source
        replay=gui_input["replay"],
        sds_root=gui_input["sds_root"],
        sds_type=gui_input["sds_type"],
        dataformat=gui_input["dataformat"],
        customfmt=gui_input["customfmt"],
        myFMTSTR=gui_input["myFMTSTR"],
        ## metadata
        inv_supply=gui_input["inv_supply"],
        inv_file=gui_input["inv_file"],
        inv_type=gui_input["inv_type"],
    )

    #####  pre-processing parameters

    preproc = dict(
        # gaps
        check_gaps=gui_input["check_gaps"],
        min_nchan=[*map(int, gui_input["min_nchan"])],
        max_gap_size=[*map(float, gui_input["max_gap_size"])],
        max_gap_ends=[*map(float, gui_input["max_gap_ends"])],
        # detrending options
        zcomps=gui_input["zcomps"],
        demean=gui_input["demean"],
        linear=gui_input["detrend"],
        # taper
        taper=gui_input["taper"],
        taper_pc=[*map(float,gui_input["taper_pc"])],
        # prefiltering
        prefilt=gui_input["prefilt"],
        Fmin=[*map(float,gui_input["Fmin"])],
        Fmax=[*map(float,gui_input["Fmax"])],
        # decimation
        decimate=gui_input["decimate"],
        newfreq=[*map(float,gui_input["newfreq"])],
        # response
        removeresponse=gui_input["removeresponse"],
        # filtering
        bandpass=gui_input["bandpass"],
    )

    #####  array processing parameters

    kwargs = dict(
        # slowness grid: X min, X max, Y min, Y max, Slow Step
        sll_x=[*map(float,gui_input["sll_x"])],
        slm_x=[*map(float,gui_input["slm_x"])],
        sll_y=[*map(float,gui_input["sll_x"])],
        slm_y=[*map(float,gui_input["slm_y"])],
        sl_s=[*map(float,gui_input["sl_s"])],
        # sliding window properties
        win_len=[*map(float,gui_input["win_len"])],
        #win_frac=1.0-[*map(float,gui_input["win_frac"])],
        win_frac=[1.0-wf for wf in [*map(float,gui_input["win_frac"])]],#NB obspy\
        #array_processing uses fraction for STEP not overlap
        # frequency properties
        frqlow=[*map(float,gui_input["frqlow"])],
        frqhigh=[*map(float,gui_input["frqhigh"])],
        prewhiten=[*map(int,gui_input["prewhiten"])],
        # restrict output
        semb_thres=[*map(float,gui_input["semb_thresh"])],
        vel_thres=[*map(float,gui_input["vel_thresh"])],
        stime=None,
        etime=None,
        store=None,
        verbose=False,
        method=0, # 0 = beamforming, 1 = capon (for f-k)
    )

    #####  plotting parameters
    to_plot = dict(
        baz=gui_input["baz"],
        slow=gui_input["slow"],
        relpow=gui_input["relpow"],
        seis=gui_input["seis"],
        spec=gui_input["spec"],
        arraysep=gui_input["arraysep"],
        rmes=gui_input["rmes"],
        rmes_wind=float(gui_input["rmes_wind"]),
        rmes_ovlp=float(gui_input["rmes_ovlp"]),
        polar=gui_input["polar"],
        resp=gui_input["resp"],
        bazmap=gui_input["bazmap"],
        timelinex=int(gui_input["timelinex"]),
        timeliney=int(gui_input["timeliney"]),
        slow_ymin=gui_input["slow_ymin"],
        slow_ymax=gui_input["slow_ymax"],
        baz_ymin=gui_input["baz_ymin"],
        baz_ymax=gui_input["baz_ymax"],
        rms_ymin=gui_input["rms_ymin"],
        rms_ymax=gui_input["rms_ymax"],
        seis_ymin=gui_input["seis_ymin"],
        seis_ymax=gui_input["seis_ymax"],
        relpow_ymin=gui_input["relpow_ymin"],
        relpow_ymax=gui_input["relpow_ymax"],
        norm=gui_input["norm"],
        polarx=int(gui_input["polarx"]),
        polary=int(gui_input["polary"]),
        arrayx=int(gui_input["arrayx"]),
        arrayy=int(gui_input["arrayy"]),
        mapx=int(gui_input["mapx"]),
        mapy=int(gui_input["mapy"]),
        map_array_radius=float(gui_input["map_array_radius"]),
        map_array_centre=gui_input["map_array_centre"],
        lat_min=gui_input["lat_min"],
        lat_max=gui_input["lat_max"],
        lon_min=gui_input["lon_min"],
        lon_max=gui_input["lon_max"],
        nbin_baz=int(gui_input["nbin_baz"]),
        nbin_slow=int(gui_input["nbin_slow"]),
        timestamp=gui_input["timestamp"],
        usestack=gui_input["usestack"],
        savefig=gui_input["savefig"],
        webfigs=gui_input["webfigs"],
        logos=gui_input["logos"],
        figpath=gui_input["figpath"],
        timelinefigname=gui_input["timelinefigname"],
        polarfigname=gui_input["polarfigname"],
        arrayfigname=gui_input["arrayfigname"],
        mapfigname=gui_input["mapfigname"],
        savedata=gui_input["savedata"],
        datafile=gui_input["datafile"],
        first=True, # do NOT adjust this!
    )

    spectro = dict(
        fmin=[*map(float,gui_input["fmin"])],
        fmax=[*map(float,gui_input["fmax"])],
        axes=None,
        wlen=[*map(float,gui_input["wlen"])],
        per_lap=[*map(float,gui_input["per_lap"])],
        show=True,
        cmap=gui_input["cmap"],
        #clip=[[*map(float,gui_input["clim1"])],\
        #    [*map(float,gui_input["clim2"])]],
        clip = np.array([[*map(float,gui_input["clim_min"])],\
            [*map(float,gui_input["clim_max"])]]).squeeze()\
                .transpose().tolist(),
        dbscale=True,
    )

    array_resp = dict(
        coordsys='lonlat',
        klim=float(gui_input["klim"]),
        kstep_factor=1./(float(gui_input["kstep"])),
        elev_in_m=gui_input["elev_in_m"],
        scnl=mydata["scnl"],
        myclient=mydata["myclient"],
        lsq=gui_input["lsq"], # Use Least-Squares inversion/beamforming instead of f-k
    )

    #### SANITY CHECKS:

    if to_plot["resp"] and to_plot["bazmap"]:
        raise Exception("Error: Too many figures selected. \
            Please choose either array response OR map view to plot")

    if to_plot["bazmap"] and not to_plot["polar"]:
        raise Exception("Error: polar plot is required for map\
in order to calculate histogram to determine peak back azimuth")

    if not mydata["replay"]:

        # window length
        if window_length > timing["plot_window"]:
            raise Exception('Error: window_length should be LESS than plot_window')

        # prebuffer
        if prebuf > window_length:
            raise Exception('Error: prebuffer should be LESS than window_length')

    if not to_plot["map_array_centre"]: # array NOT at centre
        for key in ['lat_min', 'lat_max', 'lon_min', 'lon_max']:
            if to_plot[key] == 'auto':
                raise Exception('Error! If array NOT at the map centre, all 4 lat/lon \
                    limits MUST be specified')

    return timing, mydata, preproc, kwargs, to_plot, spectro, array_resp

#################################################################
### COMMMAND LINE
#################################################################

def get_param_cmd(cmd_input, narrays):
    """Reads default input values and returns cmd_input for command-line mode"""

    # fix drop-down menus (assume first item in list)
    for key in ('connection', 'inv_type', 'sds_type', 'dataformat'):
        if narrays:
            for n in range(narrays):
                if type(cmd_input[key][n]) is list and len(cmd_input[key][n])>1:
                    print('Warning:',key,'is a list, for Array',n+1,'. First item selected')
                    cmd_input[key][n] = cmd_input[key][n][0]
        else:
            if type(cmd_input[key]) is list and len(cmd_input[key])>1:
                print('Warning:',key,'is a list. First item selected')
                cmd_input[key] = cmd_input[key][0]

    # check for "auto" sized figures and set to default size:
    counter=0
    for key in ('timelinex', 'timeliney', 'polarx', 'polary', 'arrayx', 'arrayy', 'mapx', 'mapy'):
        if cmd_input[key] == 'auto':
            if counter < 1:
                from retreat.gui.gui_sizes import default_cmd_figure_dims
                fig_dims = default_cmd_figure_dims()
                print('Warning: figure size cannot be set to "auto" in command line mode')
                print('Setting to default size. Change in defaults file if other size is desired')
            #  set new value
            cmd_input[key] = fig_dims[key]
            counter = counter + 1

    # warn if overwriting figures
    if not cmd_input['savefig']:
        print('Warning: output figures will be overwritten (and NOT displayed in the GUI)')
        print('Please set "savefig" to "True" in defaults file to change this')

    # grab full path to logfile:
    logfile = cmd_input["logpath"]+"/"+cmd_input["logfile"]

    return cmd_input, logfile
