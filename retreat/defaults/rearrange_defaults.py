"""rearrange_defaults"""
def rearrange_defaults(defaults, narrays):
    
    # First check if correct number of arrays defined
    if (len(defaults)-1) != narrays:
        raise SystemExit('Error. Please specify parameters for EACH array in the defaults file')

    master_defaults = defaults[0] # the common set of parameters
    
    defaults_arrays = dict()
    
    # loop over remaining keys
    for key in defaults[1]: # (assume keys in both array sets are identical)
        key_array = []
        # loop over arrays
        for n in range(narrays):
            #print(defaults[n+1][key])
            key_array.append(defaults[n+1][key])
        
        defaults_arrays.update({key:key_array})
        
    # append
    master_defaults.update(defaults_arrays)
    
    return master_defaults

def rearrange_gui(gui_input):
    
    #print(gui_input)
    ## get common set of parameters
    
    common_keys = ('plot_window', 'window_length', 'update_interval', 'max_realtime_latency',\
        'tstart', 'tstop', 'prebuf', 'fill_on_start', 'baz', 'slow', 'polar', 'rmes', 'relpow', \
        'arraysep', 'norm', 'rmes_wind', 'rmes_ovlp', 'seis', 'spec', 'resp', 'bazmap', \
        'elev_in_m', 'klim', 'kstep', 'timestamp', 'usestack', 'savefig', 'webfigs', 'logos',\
        'nbin_baz', 'nbin_slow', 'map_array_centre', 'map_array_radius', 'lon_min', 'lon_max', \
        'lat_min', 'lat_max', 'timelinex', 'timeliney', 'polarx', 'polary', 'arrayx', 'arrayy', \
        'mapx', 'mapy', 'logpath', 'logfile', 'figpath', 'timelinefigname', 'polarfigname', \
        'arrayfigname', 'mapfigname', 'savedata', 'datafile')
    
    gui_common = dict((k, gui_input[k]) for k in common_keys)
    
    gui_input_out = gui_common
    
    ## get both arrays
    
    array_keys = ('myclient', 'connection', 'replay', 'customfmt', 'sds_root', 'sds_type', \
        'myFMTSTR', 'dataformat', 'S', 'C', 'N', 'L', 'scnl_supply', 'scnl_file', 'inv_type', \
        'inv_supply', 'inv_file', 'check_gaps', 'min_nchan', 'max_gap_size', 'max_gap_ends', \
        'decimate', 'newfreq', 'demean', 'detrend', 'bandpass', 'Fmin', 'Fmax', 'prefilt', \
        'removeresponse', 'taper', 'taper_pc', 'zcomps', 'sll_x', 'sll_y', 'slm_x', 'slm_y',\
        'sl_s', 'win_len', 'win_frac', 'prewhiten', 'frqlow', 'frqhigh', 'semb_thresh', \
        'vel_thresh', 'lsq', 'slow_ymin', 'slow_ymax', 'baz_ymin', 'baz_ymax', 'rms_ymin',\
        'rms_ymax', 'seis_ymin', 'seis_ymax', 'relpow_ymin', 'relpow_ymax', 'fmin', 'fmax',\
        'wlen', 'per_lap', 'clim_min', 'clim_max', 'cmap')
    
    # we know this is only for 2 array case
    gui_arrays=[]
    for n in range(2): 
        narray_keys=[]
        for s in array_keys:
            s += str(n+1)
            narray_keys.append(s)
        
        gui_arrays.append(dict((k, gui_input[k]) for k in narray_keys))
        
    # rearrange into pairs
    new_gui_arrays = dict()
    
    for key in array_keys: # (assume keys in both array sets are identical)
        key_array = []
        # loop over arrays
        for n in range(2):
            #print(gui_arrays[n][key+str(n+1)])
            key_array.append(gui_arrays[n][key+str(n+1)])
        
            new_gui_arrays.update({key:key_array})  
    
    # append to common params
    gui_input_out.update(new_gui_arrays)
  
    return gui_input_out
