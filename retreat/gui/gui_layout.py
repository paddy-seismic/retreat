"""SET UP GUI WINDOW LAYOUT"""
def gui_layout(web,CWD):
    """Uses PySimpleGUI framework to create the layout for the GUI window. Defines and creates the
    input elements and logfile output element. Returns the complete window layout ('layout' variable)
    and the framework ('sg' variable) to the gui_start module."""
    # Import GUI framework
    if web:
        import PySimpleGUIWeb as sg
    else:
        import PySimpleGUI as sg
    #import PySimpleGUIQt as sg

    # Import DEFAULT VALUES
    from retreat.defaults.default_input_values import my_defaults
    defaults = my_defaults(CWD)

    # Set GUI colour scheme and text options
    #sg.ChangeLookAndFeel('GreenTan')
    sg.ChangeLookAndFeel('BrownBlue')
    sg.SetOptions(text_justification='right')

    ######## DATA INPUT #############
    myinput = [[sg.Text('Input data:', font=('Helvetica', 14))],
               ### REALTIME SOURCES
               [sg.Text('Connection type:'),
                sg.InputCombo(['FDSN', 'seedlink'], key='connection', font=('Helvetica', 9)),
                sg.Text('Client/Server', size=(11, 1)),
                sg.Input(defaults["myclient"], key='myclient', size=(28, 1), font=('Helvetica', 9)),
                sg.Text('S', size=(1, 1)),
                sg.In(default_text=defaults["S"], size=(5, 1), key='S', font=('Helvetica', 9)),
                sg.Text('C', size=(2, 1)),
                sg.In(default_text=defaults["C"], size=(5, 1), key='C', font=('Helvetica', 9)),
                sg.Text('N', size=(2, 1)),
                sg.In(default_text=defaults["N"], size=(4, 1), key='N', font=('Helvetica', 9)),
                sg.Text('L', size=(1, 1)),
                sg.In(default_text=defaults["L"], size=(3, 1), key='L', font=('Helvetica', 9))],
               [sg.Checkbox('Inventory file', size=(20, 1), default=defaults["inv_supply"], key='inv_supply'),
                sg.Text('Inventory filename'),
                sg.Input(default_text=defaults["inv_file"], size=(12, 1), font=('Helvetica', 9), key='inv_file'),
                sg.FileBrowse(font=('Helvetica', 9)),
                sg.Text('File format:'),
                sg.InputCombo(['STATIONXML', 'SEED', 'XSEED', 'RESP'], key='inv_type', font=('Helvetica', 9), size=(11, 1))],
               ### FILES/REPLAY MODE
               [sg.Checkbox('Replay mode', size=(11, 1), default=defaults["replay"], key='replay'),
                sg.Text('SDS directory', size=(11, 1)),
                sg.Input(defaults["sds_root"], key='sds_root', size=(35, 1), font=('Helvetica', 9)),
                sg.Text('SDS type', size=(8, 1)),
                sg.InputCombo(['', '*', 'D', 'R'], key='sds_type', size=(1, 1), font=('Helvetica', 9)),
                sg.Text('Data format', size=(10, 1)),
                sg.InputCombo(['MSEED', 'SAC', 'GCF', 'SEISAN'], key='dataformat', size=(7, 1), font=('Helvetica', 9))],
               [sg.Checkbox('Custom Format:', size=(13, 1), default=defaults["customfmt"], key='customfmt'),
                sg.Input(defaults["myFMTSTR"], key='myFMTSTR', size=(85, 1), font=('Helvetica', 9))],
               [sg.Text('_'  * 200, size=(114, 1))],
               ### PRE-PROCESSING ############
               [sg.Text('Pre-processing parameters:', font=('Helvetica', 14))],
               [sg.Checkbox('Use Z components only', size=(20, 1), default=defaults["zcomps"], key='zcomps'),
                sg.Checkbox('Demean', size=(8, 1), key='demean', default=defaults["demean"]),
                sg.Checkbox('Linear detrend', size=(13, 1), default=defaults["detrend"], key='detrend'),
                sg.Checkbox('Remove instrument response', size=(27, 1), default=defaults["removeresponse"], key='removeresponse')],
               [sg.Checkbox('Taper', size=(5, 1), default=defaults["taper"], key='taper'),
                sg.Text('Taper fraction', size=(14, 1)),
                sg.In(default_text=defaults["taper_pc"], size=(5, 1), key='taper_pc', font=('Helvetica', 9)),
                sg.Checkbox('Decimate', size=(9, 1), default=defaults["decimate"], key='decimate'),
                sg.Text('New sampling frequency [Hz]', size=(24, 1)),
                sg.In(default_text=defaults["newfreq"], size=(7, 1), key='newfreq', font=('Helvetica', 9))],
               [sg.Checkbox('Pre-filter', size=(9, 1), default=defaults["prefilt"], key='prefilt'),
                sg.Checkbox('Bandpass', size=(10, 1), default=defaults["bandpass"], key='bandpass'),
                sg.Text('Fmin [Hz]', size=(10, 1)),
                sg.In(default_text=defaults["Fmin"], size=(7, 1), key='Fmin', font=('Helvetica', 9)),
                sg.Text('Fmax [Hz]', size=(10, 1)),
                sg.In(default_text=defaults["Fmax"], size=(7, 1), key='Fmax', font=('Helvetica', 9))],
               [sg.Text('_'  * 200, size=(114, 1))],
               ### TIMIMG ####################
               [sg.Text('Timing parameters:', font=('Helvetica', 14))],
               [sg.Text('Start Time [UTC]', size=(14, 1)),
                sg.In(default_text=defaults["tstart"], size=(25, 1), key='tstart', font=('Helvetica', 9)),
                sg.Text('Plot Window [s]', size=(15, 1)),
                sg.In(default_text=defaults["plot_window"], size=(10, 1), key='plot_window', font=('Helvetica', 9))],
               [sg.Text('Window Length [s]', size=(15, 1)),
                sg.In(default_text=defaults["window_length"], size=(10, 1), font=('Helvetica', 9), key='window_length'),
                sg.Text('Update Interval [s]', size=(15, 1)),
                sg.In(default_text=defaults["update_interval"], size=(7, 1), key='update_interval', font=('Helvetica', 9)),
                sg.Text('Pre-buffer [s]', size=(11, 1)),
                sg.In(default_text=defaults["prebuf"], size=(7, 1), key='prebuf', font=('Helvetica', 9)),
                sg.Text('Fill window on start', size=(16, 1)),
                sg.Checkbox('', size=(1, 1), default=defaults["fill_on_start"], key='fill_on_start', font=('Helvetica', 9))],
               [sg.Text('_'  * 200, size=(114, 1))],
               ### ARRAY PROCESSiNG #########
               [sg.Text('Array Processing parameters:', font=('Helvetica', 14))],
               [sg.Text('Xmin, Xmax, Ymin, Ymax, Slowness step (Slowness grid)', font=('Helvetica', 9), justification='left'),
                sg.Text('Fmin [Hz]', size=(8, 1), font=('Helvetica', 10)),
                sg.In(default_text=defaults["frqlow"], size=(6, 1), key='frqlow', font=('Helvetica', 9)),
                sg.Text('Fmax [Hz]', size=(8, 1), font=('Helvetica', 10)),
                sg.In(default_text=defaults["frqhigh"], size=(5, 1), key='frqhigh', font=('Helvetica', 9)),
                sg.Checkbox('Pre-whiten', size=(9, 1), key='prewhiten', default=defaults["prewhiten"], font=('Helvetica', 9)),
                sg.Text('Velocity threshold', size=(14, 1), font=('Helvetica', 10)),
                sg.In(default_text=defaults["vel_thresh"], size=(7, 1), key='vel_thresh', font=('Helvetica', 9))],
               [sg.In(default_text=defaults["sll_x"], size=(6, 1), key='sll_x', font=('Helvetica', 9)),
                sg.In(default_text=defaults["slm_x"], size=(6, 1), key='slm_x', font=('Helvetica', 9)),
                sg.In(default_text=defaults["sll_y"], size=(6, 1), key='sll_y', font=('Helvetica', 9)),
                sg.In(default_text=defaults["slm_y"], size=(6, 1), key='slm_y', font=('Helvetica', 9)),
                sg.In(default_text=defaults["sl_s"], size=(6, 1), key='sl_s', font=('Helvetica', 9)),
                sg.Text('Window length [s]', size=(14, 1), font=('Helvetica', 10)),
                sg.In(default_text=defaults["win_len"], size=(6, 1), key='win_len', font=('Helvetica', 9)),
                sg.Text('Overlap fraction', size=(13, 1), font=('Helvetica', 10)),
                sg.In(default_text=defaults["win_frac"], size=(5, 1), key='win_frac', font=('Helvetica', 9)),
                sg.Text('Semblance threshold', size=(17, 1), font=('Helvetica', 10)),
                sg.In(default_text=defaults["semb_thresh"], size=(7, 1), key='semb_thresh', font=('Helvetica', 9))],
               [sg.Text('_'  * 200, size=(114, 1))],
               ### PLOTTING #################
               [sg.Text('Results to plot:', font=('Helvetica', 14), )],
               [sg.Checkbox('Back Azimuth', size=(16, 1), default=defaults["baz"], key='baz'),
                sg.Checkbox('Slowness', size=(16, 1), key='slow', default=defaults["slow"]),
                sg.Checkbox('F-K Polar plot', size=(16, 1), default=defaults["polar"], key='polar'),
                sg.Text('RMeS window [s]', size=(16, 1)),
                sg.In(default_text=defaults["rmes_wind"], size=(8, 1), key='rmes_wind', font=('Helvetica', 9)),
                sg.Checkbox('Save Figures', size=(12, 1), default=defaults["savefig"], key='savefig')],
               [sg.Checkbox('Seismogram', size=(16, 1), default=defaults["seis"], key='seis'),
                sg.Checkbox('Spectrogram', size=(16, 1), key='spec', default=defaults["spec"]),
                sg.Checkbox('RMeS', size=(16, 1), default=defaults["rmes"], key='rmes'),
                sg.Text('RMeS overlap fraction', size=(18, 1)),
                sg.In(default_text=defaults["rmes_ovlp"], size=(6, 1), key='rmes_ovlp', font=('Helvetica', 9)),
                sg.Checkbox('Web Figures', size=(12, 1), default=defaults["webfigs"], key='webfigs')],
               [sg.Text('Timeline plot dimensions (x, y) [px]', size=(29, 1)),
                sg.In(default_text=defaults["timelinex"], size=(5, 1), key='timelinex', font=('Helvetica', 9)),
                sg.In(default_text=defaults["timeliney"], size=(5, 1), key='timeliney', font=('Helvetica', 9)),
                sg.Text('Polar plot dimensions (x, y) [px]', size=(25, 1)),
                sg.In(default_text=defaults["polarx"], size=(5, 1), key='polarx', font=('Helvetica', 9)),
                sg.In(default_text=defaults["polary"], size=(5, 1), key='polary', font=('Helvetica', 9))],
               [sg.Text('Slowness plot axis limits (s/km) [min, max]', size=(35, 1)),
                sg.In(default_text=defaults["slow_ymin"], size=(5, 1), key='slow_ymin', font=('Helvetica', 9)),
                sg.In(default_text=defaults["slow_ymax"], size=(5, 1), key='slow_ymax', font=('Helvetica', 9)),
                sg.Text('Back-azimuth plot axis limits (degrees) [min, max]', size=(40, 1)),
                sg.In(default_text=defaults["baz_ymin"], size=(5, 1), key='baz_ymin', font=('Helvetica', 9)),
                sg.In(default_text=defaults["baz_ymax"], size=(5, 1), key='baz_ymax', font=('Helvetica', 9))],
               [sg.Text('Number of azimuth bins'),
                sg.In(default_text=defaults["nbin_baz"], size=(5, 1), key='nbin_baz', font=('Helvetica', 9)),
                sg.Text('Number of slowness bins'),
                sg.In(default_text=defaults["nbin_slow"], size=(5, 1), key='nbin_slow', font=('Helvetica', 9)),
                sg.Checkbox('Plot timestamp', size=(15, 1), default=defaults["timestamp"], key='timestamp'),
                sg.Checkbox('Use stack for plots', size=(15, 1), default=defaults["usestack"], key='usestack')],
               [sg.Text('RMS/RMeS limits (m/s) [min, max]', size=(29, 1)),
                sg.In(default_text=defaults["rms_ymin"], size=(5, 1), key='rms_ymin', font=('Helvetica', 9)),
                sg.In(default_text=defaults["rms_ymax"], size=(5, 1), key='rms_ymax', font=('Helvetica', 9)),
                sg.Text('Seismogram ampltiude limits (m/s) [min, max]', size=(36, 1)),
                sg.In(default_text=defaults["seis_ymin"], size=(5, 1), key='seis_ymin', font=('Helvetica', 9)),
                sg.In(default_text=defaults["seis_ymax"], size=(5, 1), key='seis_ymax', font=('Helvetica', 9))],
               #### break
               [sg.Text('_'  * 200, size=(114, 1))],
               #### break
               [sg.Checkbox('Array response function', size=(20, 1), default=defaults["resp"], key='resp'),
                sg.Text('Coordinates [\'xy\' or \'lonlat\']'),
                sg.In(default_text=defaults["coordsys"], size=(5, 1), key='coordsys', font=('Helvetica', 9)),
                sg.Checkbox('Elevation in [m]', size=(20, 1), default=defaults["elev_in_m"], key='elev_in_m')],
               [sg.Text('wavenumber limit', size=(15, 1)),
                sg.In(default_text=defaults["klim"], size=(6, 1), key='klim', font=('Helvetica', 9)),
                sg.Text('wavenumber step', size=(18, 1)),
                sg.In(default_text=defaults["kstep"], size=(6, 1), key='kstep', font=('Helvetica', 9)),
                sg.Text('Plot dimensions (x, y) [px]', size=(23, 1)),
                sg.In(default_text=defaults["arrayx"], size=(5, 1), key='arrayx', font=('Helvetica', 9)),
                sg.In(default_text=defaults["arrayy"], size=(5, 1), key='arrayy', font=('Helvetica', 9))],
               #### break
               [sg.Text('_'  * 200, size=(114, 1))],
               #### break
               [sg.Checkbox('Map display', size=(10, 1), default=defaults["bazmap"], key='bazmap'),
                sg.Checkbox('Array at centre?', size=(13, 1), default=defaults["map_array_centre"], key='map_array_centre'),
                sg.Text('Radius from array [km]', size=(1, 1), font=('Helvetica', 10)),
                sg.In(default_text=defaults["map_array_radius"], size=(7, 1), key='map_array_radius', font=('Helvetica', 9))],
               [sg.Text('Plot dimensions (x, y) [px]', size=(21, 1)),
                sg.In(default_text=defaults["mapx"], size=(5, 1), key='mapx', font=('Helvetica', 9)),
                sg.In(default_text=defaults["mapy"], size=(5, 1), key='mapy', font=('Helvetica', 9)),
                sg.Text('Latitude limits (deg) [min, max]', size=(25, 1)),
                sg.In(default_text=defaults["lat_min"], size=(5, 1), key='lat_min', font=('Helvetica', 9)),
                sg.In(default_text=defaults["lat_max"], size=(5, 1), key='lat_max', font=('Helvetica', 9)),
                sg.Text('Longitude limits (deg) [min, max]', size=(26, 1)),
                sg.In(default_text=defaults["lon_min"], size=(5, 1), key='lon_min', font=('Helvetica', 9)),
                sg.In(default_text=defaults["lon_max"], size=(5, 1), key='lon_max', font=('Helvetica', 9)),],
               [sg.Text('_'  * 200, size=(114, 1))],
               ### SPECTROGRAM ############
               [sg.Text('Spectrogram parameters:', font=('Helvetica', 12))],
               [sg.Text('Fmin [Hz]', size=(9, 1)),
                sg.In(default_text=defaults["fmin"], size=(6, 1), key='fmin', font=('Helvetica', 9)),
                sg.Text('Fmax [Hz]', size=(9, 1)),
                sg.In(default_text=defaults["fmax"], size=(6, 1), key='fmax', font=('Helvetica', 9)),
                sg.Text('Window Length [s]', size=(15, 1)),
                sg.In(default_text=defaults["wlen"], size=(10, 1), key='wlen', font=('Helvetica', 9))],
               [sg.Text('Overlap fraction', size=(17, 1)),
                sg.In(default_text=defaults["per_lap"], size=(5, 1), key='per_lap', font=('Helvetica', 9)),
                sg.Text('Colormap limits:', size=(17, 1)),
                sg.In(default_text=defaults["clim1"], size=(5, 1), key='clim1', font=('Helvetica', 9)),
                sg.In(default_text=defaults["clim2"], size=(5, 1), key='clim2', font=('Helvetica', 9)),
                sg.Text('Colormap', size=(8, 1)),
                sg.In(default_text=defaults["cmap"], size=(10, 1), key='cmap', font=('Helvetica', 9))],
               [sg.Text('_'  * 200, size=(114, 1))],
               #### OUTPUT ###############
               [sg.Text('Output parameters:', font=('Helvetica', 14))],
               [sg.Text('Figure output path', size=(15, 1)),
                sg.In(default_text=defaults["figpath"], size=(45, 1), key='figpath', font=('Helvetica', 9)),
                sg.Text('filenames:', size=(10, 1)),
                sg.In(default_text=defaults["timelinefigname"], size=(11, 1), key='timelinefigname', font=('Helvetica', 9)),
                sg.In(default_text=defaults["polarfigname"], size=(11, 1), key='polarfigname', font=('Helvetica', 9)),
                sg.In(default_text=defaults["arrayfigname"], size=(11, 1), key='arrayfigname', font=('Helvetica', 9)),
                sg.In(default_text=defaults["mapfigname"], size=(6, 1), key='mapfigname', font=('Helvetica', 9))],
               [sg.Text('Log file path', size=(10, 1)),
                sg.In(default_text=defaults["logpath"], size=(40, 1), key='logpath', font=('Helvetica', 9)),
                sg.Text('Log file name', size=(12, 1)),
                sg.In(default_text=defaults["logfile"], size=(18, 1), key='logfile', font=('Helvetica', 9))]
              ]# close myinput

    ######## SUBMIT BUTTON ############
    mybuttons = [sg.Submit('Start', tooltip='Press to start realt-time monitoring updates'),
                 sg.Cancel('Stop', tooltip='Press to Stop or Cancel the execution'),
                 sg.Exit(tooltip='Exit the program')
                ]

    ######## OUTPUT ###################
    myout = [mybuttons,
             [sg.Text('Program output:', font=('Helvetica', 14))],
             [sg.Output(size=(125, 60), key='outputwindow')]
            ]

    ######## CREATE LAYOUT ############
    layout = [[sg.Column(myinput, scrollable=True, vertical_scroll_only=True),
               sg.VerticalSeparator(pad=None), sg.Column(myout)]]

    # RETURN the layout and framework variable
    return layout, sg
