"""default_input_values"""
def my_defaults(cwd, narrays):
    """Dictionary containing Default Input Values"""
    from obspy.core import UTCDateTime
    from retreat.defaults.rearrange_defaults import rearrange_defaults

    # default parameter values
    #############################
    ### Start with values/parameters common to all arrays
    defaults_common = dict(
        #########################
        # TIMING
        plot_window=1800,
        window_length=900,
        update_interval=900,
        max_realtime_latency=10,
        tstart=UTCDateTime('2019-07-19-18:00').isoformat(),
        tstop=UTCDateTime('2019-07-19-23:00').isoformat(),
        prebuf=5,
        fill_on_start=True,
        # PLOTTING
        baz=True,
        slow=True,
        polar=True,
        rmes=True,
        relpow=False,
        arraysep=False,
        norm=False,
        rmes_wind=120.0,
        rmes_ovlp=0.90,
        seis=True,
        spec=True,
        resp=False,
        bazmap=True,
        elev_in_m=True,
        klim=10.0,
        kstep=0.01,
        timestamp=False,
        usestack=False,
        savefig=False,
        webfigs=False,
        logos=True,
        # ARRAY
        # polar plot histogram
        nbin_baz=72, # 360/72=5 deg bins
        nbin_slow=50,
        # MAP
        map_array_centre=True,
        map_array_radius=2.5, # km
        lon_min="auto",
        lon_max="auto",
        lat_min="auto",
        lat_max="auto",
        # PLOT DIMENSIONS
        timelinex=1600,
        timeliney=1200,
        polarx=800,
        polary=600,
        arrayx=650,
        arrayy=600,
        mapx=650,
        mapy=650,
        # OUTPUT
        logpath=cwd+"/retreat/output/",
        logfile="retreat.log",
        figpath=cwd+"/retreat/output/",
        timelinefigname="MainTimeline",
        polarfigname="fkpolar",
        arrayfigname="arrayresp",
        mapfigname="map",
        savedata=False,
        datafile="array_output",
        ########################
        )
    ##############################
    ### Now add separate parameters section for each array

    ## ARRAY 1
    defaults_array_one = dict(
        #########################
        # DATA SOURCES - REALTIME
        myclient="IRIS",
        connection=['FDSN', 'seedlink','earthworm'],
        # DATA SOURCES - REPLAY
        replay=True,
        customfmt=True,
        sds_root=cwd+"/retreat/example_data/ETNA/",
        sds_type=['', '*', 'D', 'R'],
        myFMTSTR="{network}.{station}.{location}.{channel}.{year}.{doy:03d}",
        dataformat=['MSEED', 'SAC', 'GCF', 'SEISAN'],
        # SCNLs
        S="ENCR",
        C="*",
        N="XZ",
        L="*",
        scnl_supply=False,
        scnl_file=cwd+"/retreat/example_data/ETNA/ETNA.scnl",
        # METADATA
        inv_type=['STATIONXML', 'XSEED', 'ASCII'],
        inv_supply=True,
        inv_file=cwd+"/retreat/example_data/ETNA/XZ.xml",
        # PRE-PROCESSING
        check_gaps=False,
        min_nchan=3,
        max_gap_size=10,
        max_gap_ends=60,
        decimate=True,
        newfreq=30.0,
        demean=True,
        detrend=False,
        bandpass=False,
        Fmin=0.1,
        Fmax=10.0,
        prefilt=False,
        removeresponse=False,
        taper=True,
        taper_pc=0.005,
        zcomps=False,
        # ARRAY PROCESSING
        sll_x=-3.1,
        sll_y=-3.1,
        slm_x=3.1,
        slm_y=3.1,
        sl_s=0.155,
        win_len=60.0,
        win_frac=0.6,
        prewhiten=False,
        frqlow=0.5,
        frqhigh=10.0,
        semb_thresh='-1e9',
        vel_thresh='-1e9',
        lsq=False,
        # AXIS LIMITS
        slow_ymin="2.0",
        slow_ymax="4.0",
        baz_ymin="45",
        baz_ymax="260",
        rms_ymin="auto",
        rms_ymax="auto",
        seis_ymin="-1E5",
        seis_ymax="1E5",
        relpow_ymin="auto",
        relpow_ymax="auto",
        # SPECTROGRAM
        fmin=0.1,
        fmax=10.0,
        wlen=25.0,
        per_lap=0.95,
        clim_min=0.75,
        clim_max=1.0,
        cmap="jet",
    )

    ## ARRAY 2
    defaults_array_two = dict(
        #########################
        # DATA SOURCES - REALTIME
        myclient="IRIS",
        connection=['FDSN', 'seedlink','earthworm'],
        # DATA SOURCES - REPLAY
        replay=True,
        customfmt=True,
        sds_root=cwd+"/retreat/example_data/ETNA/",
        sds_type=['', '*', 'D', 'R'],
        myFMTSTR="{network}.{station}.{location}.{channel}.{year}.{doy:03d}",
        dataformat=['MSEED', 'SAC', 'GCF', 'SEISAN'],
        # SCNLs
        S="ENEA",
        C="*",
        N="XZ",
        L="*",
        scnl_supply=False,
        scnl_file=cwd+"/retreat/example_data/ETNA/ETNA.scnl",
        # METADATA
        inv_type=['STATIONXML', 'XSEED', 'ASCII'],
        inv_supply=True,
        inv_file=cwd+"/retreat/example_data/ETNA/XZ.xml",
        # PRE-PROCESSING
        check_gaps=False,
        min_nchan=3,
        max_gap_size=10,
        max_gap_ends=60,
        decimate=True,
        newfreq=30.0,
        demean=True,
        detrend=False,
        bandpass=False,
        Fmin=0.1,
        Fmax=10.0,
        prefilt=False,
        removeresponse=False,
        taper=True,
        taper_pc=0.005,
        zcomps=False,
        # ARRAY PROCESSING
        sll_x=-3.1,
        sll_y=-3.1,
        slm_x=3.1,
        slm_y=3.1,
        sl_s=0.155,
        win_len=60.0,
        win_frac=0.6,
        prewhiten=False,
        frqlow=0.5,
        frqhigh=10.0,
        semb_thresh='-1e9',
        vel_thresh='-1e9',
        lsq=False,
        # AXIS LIMITS
        slow_ymin="2.0",
        slow_ymax="4.0",
        baz_ymin="45",
        baz_ymax="260",
        rms_ymin="auto",
        rms_ymax="auto",
        seis_ymin="-1E5",
        seis_ymax="1E5",
        relpow_ymin="auto",
        relpow_ymax="auto",
        # SPECTROGRAM
        fmin=0.1,
        fmax=10.0,
        wlen=25.0,
        per_lap=0.95,
        clim_min=0.75,
        clim_max=1.0,
        cmap="jet",
    )
    ## NB to add another array, create another section/dictionary as above, and append to list below:
    
    ### Combine into single list
    defaults = [defaults_common, defaults_array_one, defaults_array_two ] # append additonal array parameters here, 
    # e.g. [ ..., defaults_array_three ] etc.

    ### process and turn into single dictionary:
    defaults = rearrange_defaults(defaults,narrays)

    return defaults
