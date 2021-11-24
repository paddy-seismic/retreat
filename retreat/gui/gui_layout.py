import os
"""SET UP GUI WINDOW LAYOUT"""
def gui_layout(web, window_size, cwd, args):
    """Uses PySimpleGUI framework to create the layout for the GUI window. Defines and creates the
    input elements and logfile output element. Returns the complete window layout ('layout'
    variable) and the framework ('sg' variable) to the start module."""
    # Import GUI framework
    if web:
        import PySimpleGUIWeb as sg
        font_large = 20
        font_med = 18
        font_smaller = 16
        font_small = 14
        output_size = [int(window_size[0]*0.48), int(window_size[1]*0.75)]
        line_chars = 1
        nchars = int(window_size[0]/18)
    else:
        import PySimpleGUI as sg
        font_large = 14
        font_med = 12
        font_smaller = 10
        font_small = 9
        output_size = [int(window_size[0]*0.48/9.5), int(window_size[1]/22.5)] # DEFAULT conversion
        line_chars = int(window_size[0]*0.52/8.7)
        nchars = 200
        # factors from: https://pysimplegui.readthedocs.io/en/latest/#common-element-parameters
        # and adjusted slightly

    #import PySimpleGUIQt as sg

    # Import DEFAULT VALUES
    if args.defaults:
        defs=args.defaults
        # import from the path/filename supplied from command line
        from importlib.machinery import SourceFileLoader
        _, defaults_file = os.path.split(os.path.abspath(defs))
        default = SourceFileLoader(os.path.splitext(defaults_file)[0], defs).load_module()
        defaults = default.my_defaults(os.getcwd())
    else:
        # default path and name for defaults file
        from retreat.defaults.default_input_values import my_defaults
        defaults = my_defaults(os.getcwd())

    # Set GUI colour scheme and text options
    #sg.ChangeLookAndFeel('GreenTan')
    sg.ChangeLookAndFeel('BrownBlue')
    sg.SetOptions(text_justification='right')

    ######## DATA INPUT #############
    # put the first section in a separate column element to display alongside the logo:
               ### REALTIME SOURCES
    myLHcol = [[sg.Text('Connection type:', font=('Helvetica', font_smaller)),
                sg.InputCombo(defaults["connection"], default_value=defaults["connection"][0], key='connection', font=('Helvetica', font_small)),
                sg.Text('Client/Server', size=(11, 1), font=('Helvetica', font_smaller)),
                sg.Input(defaults["myclient"], key='myclient', size=(20, 1), font=('Helvetica', font_small)),
                sg.Text('S', size=(1, 1), font=('Helvetica', font_smaller)),
                sg.In(default_text=defaults["S"], size=(5, 1), key='S', font=('Helvetica', font_small)),
                sg.Text('C', size=(2, 1), font=('Helvetica', font_smaller)),
                sg.In(default_text=defaults["C"], size=(5, 1), key='C', font=('Helvetica', font_small)),
                sg.Text('N', size=(2, 1), font=('Helvetica', font_smaller)),
                sg.In(default_text=defaults["N"], size=(4, 1), key='N', font=('Helvetica', font_small)),
                sg.Text('L', size=(1, 1), font=('Helvetica', font_smaller)),
                sg.In(default_text=defaults["L"], size=(3, 1), key='L', font=('Helvetica', font_small)),
                sg.Checkbox('SCNL file', size=(8, 1), default=defaults["scnl_supply"], key='scnl_supply', font=('Helvetica', font_smaller))],
               [sg.Checkbox('Inventory file', size=(10, 1), default=defaults["inv_supply"], key='inv_supply', font=('Helvetica', font_smaller)),
                sg.Input(default_text=defaults["inv_file"], size=(16, 1), font=('Helvetica', font_small), key='inv_file'),
                sg.FileBrowse(font=('Helvetica', font_small)),
                sg.Text('File format:', font=('Helvetica', font_smaller)),
                sg.InputCombo(defaults["inv_type"], default_value=defaults["inv_type"][0], key='inv_type',
                font=('Helvetica', font_small), size=(11, 1)),
                sg.Text('| SCNL filename:', font=('Helvetica', font_smaller)),
                sg.Input(default_text=defaults["scnl_file"], size=(16, 1), font=('Helvetica', font_small), key='scnl_file'),
                sg.FileBrowse(font=('Helvetica', font_small)),
                ],
               ### FILES/REPLAY MODE
               [sg.Checkbox('Replay mode', size=(12, 1), default=defaults["replay"], key='replay', font=('Helvetica', font_smaller)),
                sg.Text('SDS directory', size=(11, 1), font=('Helvetica', font_smaller)),
                sg.Input(defaults["sds_root"], key='sds_root', size=(29, 1), font=('Helvetica', font_small)),
                sg.FolderBrowse(font=('Helvetica', font_small)),
                sg.Text('SDS type', size=(8, 1), font=('Helvetica', font_smaller)),
                sg.InputCombo(defaults["sds_type"], default_value=defaults["sds_type"][0], key='sds_type', size=(1, 1),
                font=('Helvetica', font_small)),
                sg.Text('Data format', size=(10, 1), font=('Helvetica', font_smaller)),
                sg.InputCombo(defaults["dataformat"], default_value=defaults["dataformat"][0], key='dataformat', size=(7, 1),
                font=('Helvetica', font_small))],
               [sg.Checkbox('Custom Format:', size=(15, 1), default=defaults["customfmt"], key='customfmt', font=('Helvetica', font_smaller)),
                sg.Input(defaults["myFMTSTR"], key='myFMTSTR', size=(85, 1), font=('Helvetica', font_small))]]
               ###
    # NOW start the main input element
    myinput = [[sg.Text('Input data:', font=('Helvetica', font_large))],
               [sg.Column(myLHcol),
                sg.Image(cwd+"/doc/retreat_trans96.png")],
               [sg.Text('_'  * nchars, size=(line_chars, 1))],
               ### PRE-PROCESSING ############
               [sg.Text('Pre-processing parameters:', font=('Helvetica', font_large))],
               [sg.Checkbox('Use Z components only', size=(20, 1), default=defaults["zcomps"], key='zcomps', font=('Helvetica', font_smaller)),
                sg.Checkbox('Demean', size=(8, 1), key='demean', default=defaults["demean"], font=('Helvetica', font_smaller)),
                sg.Checkbox('Linear detrend', size=(12, 1), default=defaults["detrend"], key='detrend', font=('Helvetica', font_smaller)),
                sg.Checkbox('Remove instrument response', size=(24, 1), default=defaults["removeresponse"], key='removeresponse', font=('Helvetica', font_smaller)),
                sg.Checkbox('Taper', size=(5, 1), default=defaults["taper"], key='taper', font=('Helvetica', font_smaller)),
                sg.Text('Taper fraction', size=(13, 1), font=('Helvetica', font_smaller)),
                sg.In(default_text=defaults["taper_pc"], size=(5, 1), key='taper_pc', font=('Helvetica', font_small))],
               [sg.Checkbox('Decimate:', size=(9, 1), default=defaults["decimate"], key='decimate', font=('Helvetica', font_smaller)),
                sg.Text('New sampling frequency [Hz]', size=(24, 1), font=('Helvetica', font_smaller)),
                sg.In(default_text=defaults["newfreq"], size=(7, 1), key='newfreq', font=('Helvetica', font_small)),
                sg.Checkbox('Pre-filter', size=(8, 1), default=defaults["prefilt"], key='prefilt', font=('Helvetica', font_smaller)),
                sg.Checkbox('Bandpass', size=(9, 1), default=defaults["bandpass"], key='bandpass', font=('Helvetica', font_smaller)),
                sg.Text('Fmin [Hz]', size=(9, 1), font=('Helvetica', font_smaller)),
                sg.In(default_text=defaults["Fmin"], size=(7, 1), key='Fmin', font=('Helvetica', font_small)),
                sg.Text('Fmax [Hz]', size=(9, 1), font=('Helvetica', font_smaller)),
                sg.In(default_text=defaults["Fmax"], size=(7, 1), key='Fmax', font=('Helvetica', font_small))],
               [sg.Checkbox('Check for gaps:', size=(13, 1), key='check_gaps', default=defaults["check_gaps"], font=('Helvetica', font_smaller)),
                sg.Text('Minimum number of channels', size=(25, 1), font=('Helvetica', font_smaller)),
                sg.In(default_text=defaults["min_nchan"], size=(2, 1), key='min_nchan', font=('Helvetica', font_small)),
                sg.Text('Maximum fillable gap size [s]', size=(24, 1), font=('Helvetica', font_smaller)),
                sg.In(default_text=defaults["max_gap_size"], size=(5, 1), key='max_gap_size', font=('Helvetica', font_small)),
                sg.Text('Max. gap to fill at start/end [s]', size=(24, 1), font=('Helvetica', font_smaller)),
                sg.In(default_text=defaults["max_gap_ends"], size=(5, 1), key='max_gap_ends', font=('Helvetica', font_small))],
               [sg.Text('_'  * nchars, size=(line_chars, 1))],
               ### TIMIMG ####################
               [sg.Text('Timing parameters:', font=('Helvetica', font_large))],
               [sg.Text('Start Time [UTC]', size=(14, 1), font=('Helvetica', font_smaller)),
                sg.In(default_text=defaults["tstart"], size=(25, 1), key='tstart', font=('Helvetica', font_small)),
                sg.Text('Plot Window [s]', size=(15, 1), font=('Helvetica', font_smaller)),
                sg.In(default_text=defaults["plot_window"], size=(10, 1), key='plot_window', font=('Helvetica', font_small)),
                sg.Text('Max realtime latency [s]', size=(21, 1), font=('Helvetica', font_smaller)),
                sg.In(default_text=defaults["max_realtime_latency"], size=(5, 1), key='max_realtime_latency', font=('Helvetica', font_small)),
                sg.Checkbox('Fill window on start', size=(20, 1), default=defaults["fill_on_start"], key='fill_on_start', font=('Helvetica', font_smaller))],
               [sg.Text('Window Length [s]', size=(15, 1), font=('Helvetica', font_smaller)),
                sg.In(default_text=defaults["window_length"], size=(10, 1), font=('Helvetica', font_small), key='window_length'),
                sg.Text('Update Interval [s]', size=(15, 1), font=('Helvetica', font_smaller)),
                sg.In(default_text=defaults["update_interval"], size=(7, 1), key='update_interval', font=('Helvetica', font_small)),
                sg.Text('Pre-buffer [s]', size=(11, 1), font=('Helvetica', font_smaller)),
                sg.In(default_text=defaults["prebuf"], size=(7, 1), key='prebuf', font=('Helvetica', font_small)),
                sg.Text('End Time [UTC]', size=(14, 1), font=('Helvetica', font_smaller)),
                sg.In(default_text=defaults["tstop"], size=(25, 1), key='tstop', font=('Helvetica', font_small))],
               [sg.Text('_'  * nchars, size=(line_chars, 1))],
               ### ARRAY PROCESSING #########
               [sg.Text('Array Processing parameters:', font=('Helvetica', font_large))],
               [sg.Text('Xmin, Xmax, Ymin, Ymax, Slowness step (Slowness grid)', font=('Helvetica', font_smaller), justification='left'),
                sg.Text('Fmin [Hz]', size=(8, 1), font=('Helvetica', font_smaller)),
                sg.In(default_text=defaults["frqlow"], size=(6, 1), key='frqlow', font=('Helvetica', font_small)),
                sg.Text('Fmax [Hz]', size=(8, 1), font=('Helvetica', font_smaller)),
                sg.In(default_text=defaults["frqhigh"], size=(5, 1), key='frqhigh', font=('Helvetica', font_small)),
                sg.Checkbox('Pre-whiten', size=(11, 1), key='prewhiten', default=defaults["prewhiten"], font=('Helvetica', font_smaller)),
                sg.Text('Velocity threshold', size=(14, 1), font=('Helvetica', font_smaller)),
                sg.In(default_text=defaults["vel_thresh"], size=(7, 1), key='vel_thresh', font=('Helvetica', font_small))],
               [sg.In(default_text=defaults["sll_x"], size=(5, 1), key='sll_x', font=('Helvetica', font_small)),
                sg.In(default_text=defaults["slm_x"], size=(5, 1), key='slm_x', font=('Helvetica', font_small)),
                sg.In(default_text=defaults["sll_y"], size=(5, 1), key='sll_y', font=('Helvetica', font_small)),
                sg.In(default_text=defaults["slm_y"], size=(5, 1), key='slm_y', font=('Helvetica', font_small)),
                sg.In(default_text=defaults["sl_s"], size=(5, 1), key='sl_s', font=('Helvetica', font_small)),
                sg.Text('Window length [s]', size=(14, 1), font=('Helvetica', font_smaller)),
                sg.In(default_text=defaults["win_len"], size=(6, 1), key='win_len', font=('Helvetica', font_small)),
                sg.Text('Overlap fraction', size=(13, 1), font=('Helvetica', font_smaller)),
                sg.In(default_text=defaults["win_frac"], size=(4, 1), key='win_frac', font=('Helvetica', font_small)),
                sg.Text('Semblance threshold', size=(17, 1), font=('Helvetica', font_smaller)),
                sg.In(default_text=defaults["semb_thresh"], size=(5, 1), key='semb_thresh', font=('Helvetica', font_small)),
                sg.Checkbox('LSQ Beamforming', size=(15, 1), key='lsq', default=defaults["lsq"], font=('Helvetica', font_smaller)),],
               [sg.Text('_'  * nchars, size=(line_chars, 1))],
               ### PLOTTING #################
               [sg.Text('Results to plot:', font=('Helvetica', font_large), )],
               [sg.Checkbox('Back Azimuth', size=(12, 1), default=defaults["baz"], key='baz', font=('Helvetica', font_smaller)),
                sg.Checkbox('Slowness', size=(12, 1), key='slow', default=defaults["slow"], font=('Helvetica', font_smaller)),
                sg.Checkbox('F-K Polar plot', size=(12, 1), default=defaults["polar"], key='polar', font=('Helvetica', font_smaller)),
                sg.Checkbox('Power/MCCM', size=(12, 1), default=defaults["relpow"], key='relpow', font=('Helvetica', font_smaller)),
                sg.Text('RMeS window [s]', size=(16, 1), font=('Helvetica', font_smaller)),
                sg.In(default_text=defaults["rmes_wind"], size=(8, 1), key='rmes_wind', font=('Helvetica', font_small)),
                sg.Checkbox('Save Figures', size=(12, 1), default=defaults["savefig"], key='savefig', font=('Helvetica', font_smaller))],
               [sg.Checkbox('Seismogram', size=(12, 1), default=defaults["seis"], key='seis', font=('Helvetica', font_smaller)),
                sg.Checkbox('Spectrogram', size=(12, 1), key='spec', default=defaults["spec"], font=('Helvetica', font_smaller)),
                sg.Checkbox('RMeS', size=(28, 1), default=defaults["rmes"], key='rmes', font=('Helvetica', font_smaller)),
                sg.Text('RMeS overlap fraction', size=(18, 1), font=('Helvetica', font_smaller)),
                sg.In(default_text=defaults["rmes_ovlp"], size=(6, 1), key='rmes_ovlp', font=('Helvetica', font_small)),
                sg.Checkbox('Web Figures', size=(12, 1), default=defaults["webfigs"], key='webfigs', font=('Helvetica', font_smaller))],
               [sg.Text('Timeline plot dimensions (x, y) [px]', size=(29, 1), font=('Helvetica', font_smaller)),
                sg.In(default_text=defaults["timelinex"], size=(5, 1), key='timelinex', font=('Helvetica', font_small)),
                sg.In(default_text=defaults["timeliney"], size=(5, 1), key='timeliney', font=('Helvetica', font_small)),
                sg.Text('Polar plot dimensions (x, y) [px]', size=(25, 1), font=('Helvetica', font_smaller)),
                sg.In(default_text=defaults["polarx"], size=(5, 1), key='polarx', font=('Helvetica', font_small)),
                sg.In(default_text=defaults["polary"], size=(5, 1), key='polary', font=('Helvetica', font_small)),
                sg.Checkbox('Plot logos', size=(9, 1), default=defaults["logos"], key='logos', font=('Helvetica', font_smaller))],
               [sg.Text('Slowness plot(s) axis limits (s/km) [min, max]', size=(36, 1), font=('Helvetica', font_smaller)),
                sg.In(default_text=defaults["slow_ymin"], size=(5, 1), key='slow_ymin', font=('Helvetica', font_small)),
                sg.In(default_text=defaults["slow_ymax"], size=(5, 1), key='slow_ymax', font=('Helvetica', font_small)),
                sg.Text('Back-azimuth plot axis limits (degrees) [min, max]', size=(40, 1), font=('Helvetica', font_smaller)),
                sg.In(default_text=defaults["baz_ymin"], size=(5, 1), key='baz_ymin', font=('Helvetica', font_small)),
                sg.In(default_text=defaults["baz_ymax"], size=(5, 1), key='baz_ymax', font=('Helvetica', font_small))],
               [sg.Text('RMeS limits (m/s) [min, max]', size=(23, 1), font=('Helvetica', font_smaller)),
                sg.In(default_text=defaults["rms_ymin"], size=(5, 1), key='rms_ymin', font=('Helvetica', font_small)),
                sg.In(default_text=defaults["rms_ymax"], size=(5, 1), key='rms_ymax', font=('Helvetica', font_small)),
                sg.Text('Seismogram limits (m/s) [min, max]', size=(28, 1), font=('Helvetica', font_smaller)),
                sg.In(default_text=defaults["seis_ymin"], size=(5, 1), key='seis_ymin', font=('Helvetica', font_small)),
                sg.In(default_text=defaults["seis_ymax"], size=(5, 1), key='seis_ymax', font=('Helvetica', font_small)),
                sg.Text('Power/MCCM limits [min, max]', size=(25, 1), font=('Helvetica', font_smaller)),
                sg.In(default_text=defaults["relpow_ymin"], size=(5, 1), key='relpow_ymin', font=('Helvetica', font_small)),
                sg.In(default_text=defaults["relpow_ymax"], size=(5, 1), key='relpow_ymax', font=('Helvetica', font_small))],
               [sg.Text('Number of azimuth bins', font=('Helvetica', font_smaller)),
                sg.In(default_text=defaults["nbin_baz"], size=(4, 1), key='nbin_baz', font=('Helvetica', font_small)),
                sg.Text('Number of slowness bins', font=('Helvetica', font_smaller)),
                sg.In(default_text=defaults["nbin_slow"], size=(4, 1), key='nbin_slow', font=('Helvetica', font_small)),
                sg.Checkbox('Plot timestamp', size=(12, 1), default=defaults["timestamp"], key='timestamp', font=('Helvetica', font_smaller)),
                sg.Checkbox('Use stack for plots', size=(15, 1), default=defaults["usestack"], key='usestack', font=('Helvetica', font_smaller)),
                sg.Checkbox('Normalized histogram', size=(18, 1), default=defaults["norm"], key='norm', font=('Helvetica', font_smaller))],
               #### break
               [sg.Text('_'  * nchars, size=(line_chars, 1))],
               #### break
               [sg.Checkbox('Array response function', size=(20, 1), default=defaults["resp"], key='resp', font=('Helvetica', font_smaller)),
                sg.Checkbox('Elevation in [m]', size=(13, 1), default=defaults["elev_in_m"], key='elev_in_m', font=('Helvetica', font_smaller)),
                sg.Text('wavenumber limit', size=(14, 1), font=('Helvetica', font_smaller)),
                sg.In(default_text=defaults["klim"], size=(5, 1), key='klim', font=('Helvetica', font_small)),
                sg.Text('wavenumber step', size=(14, 1), font=('Helvetica', font_smaller)),
                sg.In(default_text=defaults["kstep"], size=(5, 1), key='kstep', font=('Helvetica', font_small)),
                sg.Text('Plot dimensions (x, y) [px]', size=(21, 1), font=('Helvetica', font_smaller)),
                sg.In(default_text=defaults["arrayx"], size=(4, 1), key='arrayx', font=('Helvetica', font_small)),
                sg.In(default_text=defaults["arrayy"], size=(4, 1), key='arrayy', font=('Helvetica', font_small))],
               #### break
               [sg.Text('_'  * nchars, size=(line_chars, 1))],
               #### break
               [sg.Checkbox('Map display', size=(11, 1), default=defaults["bazmap"], key='bazmap', font=('Helvetica', font_smaller)),
                sg.Checkbox('Array at centre?', size=(14, 1), default=defaults["map_array_centre"], key='map_array_centre', font=('Helvetica', font_smaller)),
                sg.Text('Radius from array [km]', size=(20, 1), font=('Helvetica', font_smaller)),
                sg.In(default_text=defaults["map_array_radius"], size=(7, 1), key='map_array_radius', font=('Helvetica', font_small))],
               [sg.Text('Plot dimensions (x, y) [px]', size=(21, 1), font=('Helvetica', font_smaller)),
                sg.In(default_text=defaults["mapx"], size=(5, 1), key='mapx', font=('Helvetica', font_small)),
                sg.In(default_text=defaults["mapy"], size=(5, 1), key='mapy', font=('Helvetica', font_small)),
                sg.Text('Latitude limits (deg) [min, max]', size=(25, 1), font=('Helvetica', font_smaller)),
                sg.In(default_text=defaults["lat_min"], size=(5, 1), key='lat_min', font=('Helvetica', font_small)),
                sg.In(default_text=defaults["lat_max"], size=(5, 1), key='lat_max', font=('Helvetica', font_small)),
                sg.Text('Longitude limits (deg) [min, max]', size=(26, 1), font=('Helvetica', font_smaller)),
                sg.In(default_text=defaults["lon_min"], size=(5, 1), key='lon_min', font=('Helvetica', font_small)),
                sg.In(default_text=defaults["lon_max"], size=(5, 1), key='lon_max', font=('Helvetica', font_small)),],
               [sg.Text('_'  * nchars, size=(line_chars, 1))],
               ### SPECTROGRAM ############
               [sg.Text('Spectrogram parameters:', font=('Helvetica', font_med))],
               [sg.Text('Fmin [Hz]', size=(9, 1), font=('Helvetica', font_smaller)),
                sg.In(default_text=defaults["fmin"], size=(6, 1), key='fmin', font=('Helvetica', font_small)),
                sg.Text('Fmax [Hz]', size=(9, 1), font=('Helvetica', font_smaller)),
                sg.In(default_text=defaults["fmax"], size=(6, 1), key='fmax', font=('Helvetica', font_small)),
                sg.Text('Window Length [s]', size=(15, 1), font=('Helvetica', font_smaller)),
                sg.In(default_text=defaults["wlen"], size=(10, 1), key='wlen', font=('Helvetica', font_small))],
               [sg.Text('Overlap fraction', size=(17, 1), font=('Helvetica', font_smaller)),
                sg.In(default_text=defaults["per_lap"], size=(5, 1), key='per_lap', font=('Helvetica', font_small)),
                sg.Text('Colormap limits:', size=(17, 1), font=('Helvetica', font_smaller)),
                sg.In(default_text=defaults["clim1"], size=(5, 1), key='clim1', font=('Helvetica', font_small)),
                sg.In(default_text=defaults["clim2"], size=(5, 1), key='clim2', font=('Helvetica', font_small)),
                sg.Text('Colormap', size=(8, 1), font=('Helvetica', font_smaller)),
                sg.In(default_text=defaults["cmap"], size=(10, 1), key='cmap', font=('Helvetica', font_small))],
               [sg.Text('_'  * nchars, size=(line_chars, 1))],
               #### OUTPUT ###############
               [sg.Text('Output parameters:', font=('Helvetica', font_large))],
               [sg.Text('Figure output path', size=(15, 1), font=('Helvetica', font_smaller)),
                sg.In(default_text=defaults["figpath"], size=(49, 1), key='figpath', font=('Helvetica', font_small)),
                sg.Text('filenames:', size=(8, 1), font=('Helvetica', font_smaller)),
                sg.In(default_text=defaults["timelinefigname"], size=(11, 1), key='timelinefigname', font=('Helvetica', font_small)),
                sg.In(default_text=defaults["polarfigname"], size=(11, 1), key='polarfigname', font=('Helvetica', font_small)),
                sg.In(default_text=defaults["arrayfigname"], size=(11, 1), key='arrayfigname', font=('Helvetica', font_small)),
                sg.In(default_text=defaults["mapfigname"], size=(6, 1), key='mapfigname', font=('Helvetica', font_small))],
               [sg.Text('Log file path', size=(10, 1), font=('Helvetica', font_smaller)),
                sg.In(default_text=defaults["logpath"], size=(45, 1), key='logpath', font=('Helvetica', font_small)),
                sg.Text('Log file name', size=(12, 1), font=('Helvetica', font_smaller)),
                sg.In(default_text=defaults["logfile"], size=(15, 1), key='logfile', font=('Helvetica', font_small)),
                sg.Checkbox('Save data?', size=(11,1), default=defaults["savedata"], key='savedata', font=('Helvetica', font_smaller)),
                sg.Text('filename:', size=(9, 1), font=('Helvetica', font_smaller)),
                sg.In(default_text=defaults["datafile"], size=(11, 1), key='datafile', font=('Helvetica', font_small)),
                ]
              ]# close myinput

    ######## SUBMIT BUTTON ############
    mybuttons = [sg.Submit('Start', tooltip='Press to start real-time monitoring updates', font=('Helvetica', font_large)),
                 sg.Cancel('Stop', tooltip='Press to Stop or Cancel the execution', font=('Helvetica', font_large)),
                 sg.Exit(tooltip='Exit the program', font=('Helvetica', font_large))
                ]

    ######## OUTPUT ###################
    myout = [[sg.Text('_'  * nchars, size=(line_chars, 1))],
             mybuttons,
             [sg.Text('_'  * nchars, size=(line_chars, 1))],
             [sg.Text('Program output:', font=('Helvetica', font_large))],
             [sg.Output(size=(output_size[0], output_size[1]), key='outputwindow')]
            ]

    ######## CREATE LAYOUT ############

    if not web:
        layout = [[sg.Column(myinput, scrollable=True, vertical_scroll_only=True, size=(window_size[0]*0.52, window_size[1])),
                   sg.VerticalSeparator(pad=None), sg.Column(myout, size=(window_size[0]*0.48, window_size[1]))]]
    else:
        layout = myinput + myout

    # RETURN the layout and framework variable
    return layout, sg
