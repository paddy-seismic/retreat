import os
"""SET UP GUI WINDOW LAYOUT"""
def gui_layout(web, window_size, cwd, args):
    """Uses PySimpleGUI framework to create the layout for the GUI window. Defines and creates the
    input elements and logfile output element. Returns the complete window layout ('layout'
    variable) and the framework ('sg' variable) to the start module."""
    # Import GUI framework
    if args.web:
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
        # import from the path/filename supplied from command line
        from importlib.machinery import SourceFileLoader
        _, defaults_file = os.path.split(os.path.abspath(args.defaults))
        default = SourceFileLoader(os.path.splitext(defaults_file)[0], args.defaults).load_module()
        defaults = default.my_defaults(os.getcwd(), int(args.narrays))
    else:
        # default path and name for defaults file
        from retreat.defaults.default_input_values import my_defaults
        defaults = my_defaults(os.getcwd(), int(args.narrays))

    # Set GUI colour scheme and text options
    #sg.ChangeLookAndFeel('Default')
    #sg.ChangeLookAndFeel('GreenTan')
    sg.theme('GreenTan')
    #sg.ChangeLookAndFeel('LightTeal')
    #sg.ChangeLookAndFeel('BrownBlue')
    sg.SetOptions(text_justification='right')

    #print(type(defaults), len(defaults), defaults)

    mytitle = [[sg.Text('RETREAT for TWO arrays - Input data:', font=('Helvetica', font_large))]]

    ######## DATA INPUT #############
################## ARRAY 1 PARAMETERS ###########################
    myArray1 = [[sg.Text('_'  * nchars, size=(line_chars, 1))],
               [sg.Text('***************** Array 1 parameters *******************', font=('Helvetica', font_large))],
               ### REALTIME SOURCES
               [sg.Text('Connection type:', font=('Helvetica', font_smaller)),
                sg.InputCombo(defaults["connection"][0], default_value=defaults["connection"][0][0], key='connection1', font=('Helvetica', font_small)),
                sg.Text('Client/Server', size=(11, 1), font=('Helvetica', font_smaller)),
                sg.Input(defaults["myclient"][0], key='myclient1', size=(20, 1), font=('Helvetica', font_small)),
                sg.Checkbox('Inventory file', size=(10, 1), default=defaults["inv_supply"][0], key='inv_supply1', font=('Helvetica', font_smaller)),
                sg.Input(default_text=defaults["inv_file"][0], size=(16, 1), font=('Helvetica', font_small), key='inv_file1'),
                sg.FileBrowse(font=('Helvetica', font_small)),
                sg.Text('File format:', font=('Helvetica', font_smaller)),
                sg.InputCombo(defaults["inv_type"][0], default_value=defaults["inv_type"][0][0], key='inv_type1',
                font=('Helvetica', font_small), size=(11, 1)),],
               [sg.Text('S', size=(1, 1), font=('Helvetica', font_smaller)),
                sg.In(default_text=defaults["S"][0], size=(5, 1), key='S1', font=('Helvetica', font_small)),
                sg.Text('C', size=(2, 1), font=('Helvetica', font_smaller)),
                sg.In(default_text=defaults["C"][0], size=(5, 1), key='C1', font=('Helvetica', font_small)),
                sg.Text('N', size=(2, 1), font=('Helvetica', font_smaller)),
                sg.In(default_text=defaults["N"][0], size=(4, 1), key='N1', font=('Helvetica', font_small)),
                sg.Text('L', size=(1, 1), font=('Helvetica', font_smaller)),
                sg.In(default_text=defaults["L"][0], size=(3, 1), key='L1', font=('Helvetica', font_small)),
                sg.Checkbox('SCNL file', size=(8, 1), default=defaults["scnl_supply"][0], key='scnl_supply1', font=('Helvetica', font_smaller)),
                sg.Text('| SCNL filename:', font=('Helvetica', font_smaller)),
                sg.Input(default_text=defaults["scnl_file"][0], size=(16, 1), font=('Helvetica', font_small), key='scnl_file1'),
                sg.FileBrowse(font=('Helvetica', font_small)),],
               ### FILES/REPLAY MODE
               [sg.Checkbox('Replay mode', size=(12, 1), default=defaults["replay"][0], key='replay1', font=('Helvetica', font_smaller)),
                sg.Text('SDS directory', size=(11, 1), font=('Helvetica', font_smaller)),
                sg.Input(defaults["sds_root"][0], key='sds_root1', size=(29, 1), font=('Helvetica', font_small)),
                sg.FolderBrowse(font=('Helvetica', font_small)),
                sg.Text('SDS type', size=(8, 1), font=('Helvetica', font_smaller)),
                sg.InputCombo(defaults["sds_type"][0], default_value=defaults["sds_type"][0][0], key='sds_type1', size=(1, 1),
                font=('Helvetica', font_small)),
                sg.Text('Data format', size=(10, 1), font=('Helvetica', font_smaller)),
                sg.InputCombo(defaults["dataformat"][0], default_value=defaults["dataformat"][0][0], key='dataformat1', size=(7, 1),
                font=('Helvetica', font_small))],
               [sg.Checkbox('Custom Format:', size=(15, 1), default=defaults["customfmt"][0], key='customfmt1', font=('Helvetica', font_smaller)),
                sg.Input(defaults["myFMTSTR"][0], key='myFMTSTR1', size=(85, 1), font=('Helvetica', font_small))],
               [sg.Text('_'  * nchars, size=(line_chars, 1))],
               ### PRE-PROCESSING ############
               [sg.Text('Pre-processing parameters:', font=('Helvetica', font_large))],
               [sg.Checkbox('Use Z components only', size=(20, 1), default=defaults["zcomps"][0], key='zcomps1', font=('Helvetica', font_smaller)),
                sg.Checkbox('Demean', size=(8, 1), key='demean1', default=defaults["demean"][0], font=('Helvetica', font_smaller)),
                sg.Checkbox('Linear detrend', size=(12, 1), default=defaults["detrend"][0], key='detrend1', font=('Helvetica', font_smaller)),
                sg.Checkbox('Remove instrument response', size=(24, 1), default=defaults["removeresponse"][0], key='removeresponse1', font=('Helvetica', font_smaller)),
                sg.Checkbox('Taper', size=(5, 1), default=defaults["taper"][0], key='taper1', font=('Helvetica', font_smaller)),
                sg.Text('Taper fraction', size=(13, 1), font=('Helvetica', font_smaller)),
                sg.In(default_text=defaults["taper_pc"][0], size=(5, 1), key='taper_pc1', font=('Helvetica', font_small))],
               [sg.Checkbox('Decimate:', size=(9, 1), default=defaults["decimate"][0], key='decimate1', font=('Helvetica', font_smaller)),
                sg.Text('New sampling frequency [Hz]', size=(24, 1), font=('Helvetica', font_smaller)),
                sg.In(default_text=defaults["newfreq"][0], size=(7, 1), key='newfreq1', font=('Helvetica', font_small)),
                sg.Checkbox('Pre-filter', size=(8, 1), default=defaults["prefilt"][0], key='prefilt1', font=('Helvetica', font_smaller)),
                sg.Checkbox('Bandpass', size=(9, 1), default=defaults["bandpass"][0], key='bandpass1', font=('Helvetica', font_smaller)),
                sg.Text('Fmin [Hz]', size=(9, 1), font=('Helvetica', font_smaller)),
                sg.In(default_text=defaults["Fmin"][0], size=(7, 1), key='Fmin1', font=('Helvetica', font_small)),
                sg.Text('Fmax [Hz]', size=(9, 1), font=('Helvetica', font_smaller)),
                sg.In(default_text=defaults["Fmax"][0], size=(7, 1), key='Fmax1', font=('Helvetica', font_small))],
               [sg.Checkbox('Check for gaps:', size=(13, 1), key='check_gaps1', default=defaults["check_gaps"][0], font=('Helvetica', font_smaller)),
                sg.Text('Minimum number of channels', size=(25, 1), font=('Helvetica', font_smaller)),
                sg.In(default_text=defaults["min_nchan"][0], size=(2, 1), key='min_nchan1', font=('Helvetica', font_small)),
                sg.Text('Maximum fillable gap size [s]', size=(24, 1), font=('Helvetica', font_smaller)),
                sg.In(default_text=defaults["max_gap_size"][0], size=(5, 1), key='max_gap_size1', font=('Helvetica', font_small)),
                sg.Text('Max. gap to fill at start/end [s]', size=(24, 1), font=('Helvetica', font_smaller)),
                sg.In(default_text=defaults["max_gap_ends"][0], size=(5, 1), key='max_gap_ends1', font=('Helvetica', font_small))],
               [sg.Text('_'  * nchars, size=(line_chars, 1))],
                ### ARRAY PROCESSING #########
               [sg.Text('Array Processing parameters:', font=('Helvetica', font_large))],
               [sg.Text('Xmin, Xmax, Ymin, Ymax, Slowness step (Slowness grid)', font=('Helvetica', font_smaller), justification='left'),
                sg.Text('Fmin [Hz]', size=(8, 1), font=('Helvetica', font_smaller)),
                sg.In(default_text=defaults["frqlow"][0], size=(6, 1), key='frqlow1', font=('Helvetica', font_small)),
                sg.Text('Fmax [Hz]', size=(8, 1), font=('Helvetica', font_smaller)),
                sg.In(default_text=defaults["frqhigh"][0], size=(5, 1), key='frqhigh1', font=('Helvetica', font_small)),
                sg.Checkbox('Pre-whiten', size=(11, 1), key='prewhiten1', default=defaults["prewhiten"][0], font=('Helvetica', font_smaller)),
                sg.Text('Velocity threshold', size=(14, 1), font=('Helvetica', font_smaller)),
                sg.In(default_text=defaults["vel_thresh"][0], size=(7, 1), key='vel_thresh1', font=('Helvetica', font_small))],
               [sg.In(default_text=defaults["sll_x"][0], size=(5, 1), key='sll_x1', font=('Helvetica', font_small)),
                sg.In(default_text=defaults["slm_x"][0], size=(5, 1), key='slm_x1', font=('Helvetica', font_small)),
                sg.In(default_text=defaults["sll_y"][0], size=(5, 1), key='sll_y1', font=('Helvetica', font_small)),
                sg.In(default_text=defaults["slm_y"][0], size=(5, 1), key='slm_y1', font=('Helvetica', font_small)),
                sg.In(default_text=defaults["sl_s"][0], size=(5, 1), key='sl_s1', font=('Helvetica', font_small)),
                sg.Text('Window length [s]', size=(14, 1), font=('Helvetica', font_smaller)),
                sg.In(default_text=defaults["win_len"][0], size=(6, 1), key='win_len1', font=('Helvetica', font_small)),
                sg.Text('Overlap fraction', size=(13, 1), font=('Helvetica', font_smaller)),
                sg.In(default_text=defaults["win_frac"][0], size=(4, 1), key='win_frac1', font=('Helvetica', font_small)),
                sg.Text('Semblance threshold', size=(17, 1), font=('Helvetica', font_smaller)),
                sg.In(default_text=defaults["semb_thresh"][0], size=(5, 1), key='semb_thresh1', font=('Helvetica', font_small)),
                sg.Checkbox('LSQ Beamforming', size=(15, 1), key='lsq1', default=defaults["lsq"][0], font=('Helvetica', font_smaller)),],
               [sg.Text('_'  * nchars, size=(line_chars, 1))],
                ### SPECTROGRAM ############
               [sg.Text('Spectrogram parameters:', font=('Helvetica', font_med))],
               [sg.Text('Fmin [Hz]', size=(9, 1), font=('Helvetica', font_smaller)),
                sg.In(default_text=defaults["fmin"][0], size=(6, 1), key='fmin1', font=('Helvetica', font_small)),
                sg.Text('Fmax [Hz]', size=(9, 1), font=('Helvetica', font_smaller)),
                sg.In(default_text=defaults["fmax"][0], size=(6, 1), key='fmax1', font=('Helvetica', font_small)),
                sg.Text('Window Length [s]', size=(15, 1), font=('Helvetica', font_smaller)),
                sg.In(default_text=defaults["wlen"][0], size=(10, 1), key='wlen1', font=('Helvetica', font_small))],
               [sg.Text('Overlap fraction', size=(17, 1), font=('Helvetica', font_smaller)),
                sg.In(default_text=defaults["per_lap"][0], size=(5, 1), key='per_lap1', font=('Helvetica', font_small)),
                sg.Text('Colormap limits:', size=(17, 1), font=('Helvetica', font_smaller)),
                sg.In(default_text=defaults["clim_min"][0], size=(5, 1), key='clim_min1', font=('Helvetica', font_small)),
                sg.In(default_text=defaults["clim_max"][0], size=(5, 1), key='clim_max1', font=('Helvetica', font_small)),
                sg.Text('Colormap', size=(8, 1), font=('Helvetica', font_smaller)),
                sg.In(default_text=defaults["cmap"][0], size=(10, 1), key='cmap1', font=('Helvetica', font_small))],
               [sg.Text('_'  * nchars, size=(line_chars, 1))],
               ### AXIS LIMITS #########
               [sg.Text('Axis limits:', font=('Helvetica', font_large))],
               [sg.Text('RMeS limits (m/s) [min, max]', size=(23, 1), font=('Helvetica', font_smaller)),
                sg.In(default_text=defaults["rms_ymin"][0], size=(5, 1), key='rms_ymin1', font=('Helvetica', font_small)),
                sg.In(default_text=defaults["rms_ymax"][0], size=(5, 1), key='rms_ymax1', font=('Helvetica', font_small)),
                sg.Text('Seismogram limits (m/s) [min, max]', size=(28, 1), font=('Helvetica', font_smaller)),
                sg.In(default_text=defaults["seis_ymin"][0], size=(5, 1), key='seis_ymin1', font=('Helvetica', font_small)),
                sg.In(default_text=defaults["seis_ymax"][0], size=(5, 1), key='seis_ymax1', font=('Helvetica', font_small)),
                sg.Text('Power/MCCM limits [min, max]', size=(25, 1), font=('Helvetica', font_smaller)),
                sg.In(default_text=defaults["relpow_ymin"][0], size=(5, 1), key='relpow_ymin1', font=('Helvetica', font_small)),
                sg.In(default_text=defaults["relpow_ymax"][0], size=(5, 1), key='relpow_ymax1', font=('Helvetica', font_small))],
                [sg.Text('Slowness plot(s) axis limits (s/km) [min, max]', size=(36, 1), font=('Helvetica', font_smaller)),
                sg.In(default_text=defaults["slow_ymin"][0], size=(5, 1), key='slow_ymin1', font=('Helvetica', font_small)),
                sg.In(default_text=defaults["slow_ymax"][0], size=(5, 1), key='slow_ymax1', font=('Helvetica', font_small)),
                sg.Text('Back-azimuth plot axis limits (degrees) [min, max]', size=(40, 1), font=('Helvetica', font_smaller)),
                sg.In(default_text=defaults["baz_ymin"][0], size=(5, 1), key='baz_ymin1', font=('Helvetica', font_small)),
                sg.In(default_text=defaults["baz_ymax"][0], size=(5, 1), key='baz_ymax1', font=('Helvetica', font_small))],
               [sg.Text('_'  * nchars, size=(line_chars, 1))]
               ] # end Array 1 element

################## ARRAY 2 PARAMETERS ###########################
    myArray2 = [[sg.Text('_'  * nchars, size=(line_chars, 1))],
               [sg.Text('***************** Array 2 parameters *******************', font=('Helvetica', font_large))],
               ### REALTIME SOURCES
               [sg.Text('Connection type:', font=('Helvetica', font_smaller)),
                sg.InputCombo(defaults["connection"][1], default_value=defaults["connection"][1][0], key='connection2', font=('Helvetica', font_small)),
                sg.Text('Client/Server', size=(11, 1), font=('Helvetica', font_smaller)),
                sg.Input(defaults["myclient"][1], key='myclient2', size=(20, 1), font=('Helvetica', font_small)),
                sg.Checkbox('Inventory file', size=(10, 1), default=defaults["inv_supply"][1], key='inv_supply2', font=('Helvetica', font_smaller)),
                sg.Input(default_text=defaults["inv_file"][1], size=(16, 1), font=('Helvetica', font_small), key='inv_file2'),
                sg.FileBrowse(font=('Helvetica', font_small)),
                sg.Text('File format:', font=('Helvetica', font_smaller)),
                sg.InputCombo(defaults["inv_type"][1], default_value=defaults["inv_type"][1][0], key='inv_type2',
                font=('Helvetica', font_small), size=(11, 1)),],
               [sg.Text('S', size=(1, 1), font=('Helvetica', font_smaller)),
                sg.In(default_text=defaults["S"][1], size=(5, 1), key='S2', font=('Helvetica', font_small)),
                sg.Text('C', size=(2, 1), font=('Helvetica', font_smaller)),
                sg.In(default_text=defaults["C"][1], size=(5, 1), key='C2', font=('Helvetica', font_small)),
                sg.Text('N', size=(2, 1), font=('Helvetica', font_smaller)),
                sg.In(default_text=defaults["N"][1], size=(4, 1), key='N2', font=('Helvetica', font_small)),
                sg.Text('L', size=(1, 1), font=('Helvetica', font_smaller)),
                sg.In(default_text=defaults["L"][1], size=(3, 1), key='L2', font=('Helvetica', font_small)),
                sg.Checkbox('SCNL file', size=(8, 1), default=defaults["scnl_supply"][1], key='scnl_supply2', font=('Helvetica', font_smaller)),
                sg.Text('| SCNL filename:', font=('Helvetica', font_smaller)),
                sg.Input(default_text=defaults["scnl_file"][1], size=(16, 1), font=('Helvetica', font_small), key='scnl_file2'),
                sg.FileBrowse(font=('Helvetica', font_small)),],
               ### FILES/REPLAY MODE
               [sg.Checkbox('Replay mode', size=(12, 1), default=defaults["replay"][1], key='replay2', font=('Helvetica', font_smaller)),
                sg.Text('SDS directory', size=(11, 1), font=('Helvetica', font_smaller)),
                sg.Input(defaults["sds_root"][1], key='sds_root2', size=(29, 1), font=('Helvetica', font_small)),
                sg.FolderBrowse(font=('Helvetica', font_small)),
                sg.Text('SDS type', size=(8, 1), font=('Helvetica', font_smaller)),
                sg.InputCombo(defaults["sds_type"][1], default_value=defaults["sds_type"][1][0], key='sds_type2', size=(1, 1),
                font=('Helvetica', font_small)),
                sg.Text('Data format', size=(10, 1), font=('Helvetica', font_smaller)),
                sg.InputCombo(defaults["dataformat"][1], default_value=defaults["dataformat"][1][0], key='dataformat2', size=(7, 1),
                font=('Helvetica', font_small))],
               [sg.Checkbox('Custom Format:', size=(15, 1), default=defaults["customfmt"][1], key='customfmt2', font=('Helvetica', font_smaller)),
                sg.Input(defaults["myFMTSTR"][1], key='myFMTSTR2', size=(85, 1), font=('Helvetica', font_small))],
               [sg.Text('_'  * nchars, size=(line_chars, 1))],
               ### PRE-PROCESSING ############
               [sg.Text('Pre-processing parameters:', font=('Helvetica', font_large))],
               [sg.Checkbox('Use Z components only', size=(20, 1), default=defaults["zcomps"][1], key='zcomps2', font=('Helvetica', font_smaller)),
                sg.Checkbox('Demean', size=(8, 1), key='demean2', default=defaults["demean"][1], font=('Helvetica', font_smaller)),
                sg.Checkbox('Linear detrend', size=(12, 1), default=defaults["detrend"][1], key='detrend2', font=('Helvetica', font_smaller)),
                sg.Checkbox('Remove instrument response', size=(24, 1), default=defaults["removeresponse"][1], key='removeresponse2', font=('Helvetica', font_smaller)),
                sg.Checkbox('Taper', size=(5, 1), default=defaults["taper"][1], key='taper2', font=('Helvetica', font_smaller)),
                sg.Text('Taper fraction', size=(13, 1), font=('Helvetica', font_smaller)),
                sg.In(default_text=defaults["taper_pc"][1], size=(5, 1), key='taper_pc2', font=('Helvetica', font_small))],
               [sg.Checkbox('Decimate:', size=(9, 1), default=defaults["decimate"][1], key='decimate2', font=('Helvetica', font_smaller)),
                sg.Text('New sampling frequency [Hz]', size=(24, 1), font=('Helvetica', font_smaller)),
                sg.In(default_text=defaults["newfreq"][1], size=(7, 1), key='newfreq2', font=('Helvetica', font_small)),
                sg.Checkbox('Pre-filter', size=(8, 1), default=defaults["prefilt"][1], key='prefilt2', font=('Helvetica', font_smaller)),
                sg.Checkbox('Bandpass', size=(9, 1), default=defaults["bandpass"][1], key='bandpass2', font=('Helvetica', font_smaller)),
                sg.Text('Fmin [Hz]', size=(9, 1), font=('Helvetica', font_smaller)),
                sg.In(default_text=defaults["Fmin"][1], size=(7, 1), key='Fmin2', font=('Helvetica', font_small)),
                sg.Text('Fmax [Hz]', size=(9, 1), font=('Helvetica', font_smaller)),
                sg.In(default_text=defaults["Fmax"][1], size=(7, 1), key='Fmax2', font=('Helvetica', font_small))],
               [sg.Checkbox('Check for gaps:', size=(13, 1), key='check_gaps2', default=defaults["check_gaps"][1], font=('Helvetica', font_smaller)),
                sg.Text('Minimum number of channels', size=(25, 1), font=('Helvetica', font_smaller)),
                sg.In(default_text=defaults["min_nchan"][1], size=(2, 1), key='min_nchan2', font=('Helvetica', font_small)),
                sg.Text('Maximum fillable gap size [s]', size=(24, 1), font=('Helvetica', font_smaller)),
                sg.In(default_text=defaults["max_gap_size"][1], size=(5, 1), key='max_gap_size2', font=('Helvetica', font_small)),
                sg.Text('Max. gap to fill at start/end [s]', size=(24, 1), font=('Helvetica', font_smaller)),
                sg.In(default_text=defaults["max_gap_ends"][1], size=(5, 1), key='max_gap_ends2', font=('Helvetica', font_small))],
               [sg.Text('_'  * nchars, size=(line_chars, 1))],
                ### ARRAY PROCESSING #########
               [sg.Text('Array Processing parameters:', font=('Helvetica', font_large))],
               [sg.Text('Xmin, Xmax, Ymin, Ymax, Slowness step (Slowness grid)', font=('Helvetica', font_smaller), justification='left'),
                sg.Text('Fmin [Hz]', size=(8, 1), font=('Helvetica', font_smaller)),
                sg.In(default_text=defaults["frqlow"][1], size=(6, 1), key='frqlow2', font=('Helvetica', font_small)),
                sg.Text('Fmax [Hz]', size=(8, 1), font=('Helvetica', font_smaller)),
                sg.In(default_text=defaults["frqhigh"][1], size=(5, 1), key='frqhigh2', font=('Helvetica', font_small)),
                sg.Checkbox('Pre-whiten', size=(11, 1), key='prewhiten2', default=defaults["prewhiten"][1], font=('Helvetica', font_smaller)),
                sg.Text('Velocity threshold', size=(14, 1), font=('Helvetica', font_smaller)),
                sg.In(default_text=defaults["vel_thresh"][1], size=(7, 1), key='vel_thresh2', font=('Helvetica', font_small))],
               [sg.In(default_text=defaults["sll_x"][1], size=(5, 1), key='sll_x2', font=('Helvetica', font_small)),
                sg.In(default_text=defaults["slm_x"][1], size=(5, 1), key='slm_x2', font=('Helvetica', font_small)),
                sg.In(default_text=defaults["sll_y"][1], size=(5, 1), key='sll_y2', font=('Helvetica', font_small)),
                sg.In(default_text=defaults["slm_y"][1], size=(5, 1), key='slm_y2', font=('Helvetica', font_small)),
                sg.In(default_text=defaults["sl_s"][1], size=(5, 1), key='sl_s2', font=('Helvetica', font_small)),
                sg.Text('Window length [s]', size=(14, 1), font=('Helvetica', font_smaller)),
                sg.In(default_text=defaults["win_len"][1], size=(6, 1), key='win_len2', font=('Helvetica', font_small)),
                sg.Text('Overlap fraction', size=(13, 1), font=('Helvetica', font_smaller)),
                sg.In(default_text=defaults["win_frac"][1], size=(4, 1), key='win_frac2', font=('Helvetica', font_small)),
                sg.Text('Semblance threshold', size=(17, 1), font=('Helvetica', font_smaller)),
                sg.In(default_text=defaults["semb_thresh"][1], size=(5, 1), key='semb_thresh2', font=('Helvetica', font_small)),
                sg.Checkbox('LSQ Beamforming', size=(15, 1), key='lsq2', default=defaults["lsq"][1], font=('Helvetica', font_smaller)),],
               [sg.Text('_'  * nchars, size=(line_chars, 1))],
                ### SPECTROGRAM ############
               [sg.Text('Spectrogram parameters:', font=('Helvetica', font_med))],
               [sg.Text('Fmin [Hz]', size=(9, 1), font=('Helvetica', font_smaller)),
                sg.In(default_text=defaults["fmin"][1], size=(6, 1), key='fmin2', font=('Helvetica', font_small)),
                sg.Text('Fmax [Hz]', size=(9, 1), font=('Helvetica', font_smaller)),
                sg.In(default_text=defaults["fmax"][1], size=(6, 1), key='fmax2', font=('Helvetica', font_small)),
                sg.Text('Window Length [s]', size=(15, 1), font=('Helvetica', font_smaller)),
                sg.In(default_text=defaults["wlen"][1], size=(10, 1), key='wlen2', font=('Helvetica', font_small))],
               [sg.Text('Overlap fraction', size=(17, 1), font=('Helvetica', font_smaller)),
                sg.In(default_text=defaults["per_lap"][1], size=(5, 1), key='per_lap2', font=('Helvetica', font_small)),
                sg.Text('Colormap limits:', size=(17, 1), font=('Helvetica', font_smaller)),
                sg.In(default_text=defaults["clim_min"][1], size=(5, 1), key='clim_min2', font=('Helvetica', font_small)),
                sg.In(default_text=defaults["clim_max"][1], size=(5, 1), key='clim_max2', font=('Helvetica', font_small)),
                sg.Text('Colormap', size=(8, 1), font=('Helvetica', font_smaller)),
                sg.In(default_text=defaults["cmap"][1], size=(10, 1), key='cmap2', font=('Helvetica', font_small))],
               [sg.Text('_'  * nchars, size=(line_chars, 1))],
               ### AXIS LIMITS #########
               [sg.Text('Axis limits:', font=('Helvetica', font_large))],
               [sg.Text('RMeS limits (m/s) [min, max]', size=(23, 1), font=('Helvetica', font_smaller)),
                sg.In(default_text=defaults["rms_ymin"][1], size=(5, 1), key='rms_ymin2', font=('Helvetica', font_small)),
                sg.In(default_text=defaults["rms_ymax"][1], size=(5, 1), key='rms_ymax2', font=('Helvetica', font_small)),
                sg.Text('Seismogram limits (m/s) [min, max]', size=(28, 1), font=('Helvetica', font_smaller)),
                sg.In(default_text=defaults["seis_ymin"][1], size=(5, 1), key='seis_ymin2', font=('Helvetica', font_small)),
                sg.In(default_text=defaults["seis_ymax"][1], size=(5, 1), key='seis_ymax2', font=('Helvetica', font_small)),
                sg.Text('Power/MCCM limits [min, max]', size=(25, 1), font=('Helvetica', font_smaller)),
                sg.In(default_text=defaults["relpow_ymin"][1], size=(5, 1), key='relpow_ymin2', font=('Helvetica', font_small)),
                sg.In(default_text=defaults["relpow_ymax"][1], size=(5, 1), key='relpow_ymax2', font=('Helvetica', font_small))],
                [sg.Text('Slowness plot(s) axis limits (s/km) [min, max]', size=(36, 1), font=('Helvetica', font_smaller)),
                sg.In(default_text=defaults["slow_ymin"][1], size=(5, 1), key='slow_ymin2', font=('Helvetica', font_small)),
                sg.In(default_text=defaults["slow_ymax"][1], size=(5, 1), key='slow_ymax2', font=('Helvetica', font_small)),
                sg.Text('Back-azimuth plot axis limits (degrees) [min, max]', size=(40, 1), font=('Helvetica', font_smaller)),
                sg.In(default_text=defaults["baz_ymin"][1], size=(5, 1), key='baz_ymin2', font=('Helvetica', font_small)),
                sg.In(default_text=defaults["baz_ymax"][1], size=(5, 1), key='baz_ymax2', font=('Helvetica', font_small))],
               [sg.Text('_'  * nchars, size=(line_chars, 1))]
               ] # end Array 1 element

               ### NOW start the main input element
               # add ARRAY 1 with logo
               #[sg.Column(myArray1),
                #sg.Image(cwd+"/doc/retreat_trans96.png")],
                #myArray1,
################## COMMON PARAMETERS ###########################
    mycommon = [
               ### TIMIMG ####################
               [sg.Text('***************** Common parameters *******************', font=('Helvetica', font_large))],
               [sg.Text('_'  * nchars, size=(line_chars, 1))],
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
                sg.Checkbox('RMeS', size=(6, 1), default=defaults["rmes"], key='rmes', font=('Helvetica', font_smaller)),
                sg.Checkbox('Separate timeline plots?', size=(20, 1), default=defaults["arraysep"], key='arraysep', font=('Helvetica', font_smaller)),
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
              ]# close mycommon

    myinput = mytitle + myArray1 + myArray2 + mycommon

    ######## SUBMIT BUTTON ############
    mybuttons = [[sg.Submit('Start', tooltip='Press to start real-time monitoring updates', font=('Helvetica', font_large)),
                 sg.Cancel('Stop', tooltip='Press to Stop or Cancel the execution', font=('Helvetica', font_large)),
                 sg.Exit(tooltip='Exit the program', font=('Helvetica', font_large))
                ]]

    ######## OUTPUT ###################
    # put buttons in a separate column element to display alongside the logo:
    myout = [[sg.Text('_'  * nchars, size=(line_chars, 1))],
             #mybuttons,
             [sg.Column(mybuttons),
              sg.Image(cwd+"/doc/retreat_trans96.png", pad=((window_size[0]*0.25, 0),(0,0)))],
             #sg.Column(mybuttons),#, sg.Image(cwd+"/doc/retreat_trans96.png"),
             [sg.Text('_'  * nchars, size=(line_chars, 1))],
             [sg.Text('Program output:', font=('Helvetica', font_large))],
             [sg.Output(size=(output_size[0], 1.15*output_size[1]), key='outputwindow')]
            ]

    ######## CREATE LAYOUT ############

    if not args.web:
        layout = [[sg.Column(myinput, scrollable=True, vertical_scroll_only=False, size=(window_size[0]*0.52, window_size[1])),
                   sg.VerticalSeparator(pad=None), sg.Column(myout, size=(window_size[0]*0.48, window_size[1]))]]
    else:
        layout = myinput + myout

    # RETURN the layout and framework variable
    return layout, sg
