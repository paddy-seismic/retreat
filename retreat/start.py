"""start - Initialize and start main GUI window"""
def start(web):
    """Function to launch the program. Takes command line argument to determine whether to launch
    GUI or web interface"""
    #### IMPORTS ####
    import sys
    import time
    import os
    #import logging
    import traceback
    from multiprocessing import Process
    import threading
    import psutil
    # custom module to allow threads to be killed
    from retreat.tools.KThread import KThread

    # Import realtime update routines
    from retreat.realtime import realtime
    from retreat.tools.monitoring_routines import print_log_to_screen, update_image_window

    #### GET SCREEN AND WINDOW SIZES ####
    from retreat.gui.gui_sizes import get_screen_size, get_window_size
    screenx, screeny, aspect = get_screen_size()
    window_size = get_window_size(screenx, screeny, aspect)

    #### CREATE GUI LAYOUT ####
    #from retreat.gui.gui_layout import layout, sg
    from retreat.gui.gui_layout import gui_layout
    layout, sg = gui_layout(web, window_size, os.getcwd())

    #### DEFINE GLOBAL VARIABLES
    global P_LOCK, T1_LOCK, T2_LOCK, PT_LOCK, EVENT

    #### MONITOR CHILD PROCESS/THREADS ########################################
    def monitor_children(p, t1, t2, lock):
        """Monitors child processes and threads"""
        global P_LOCK, T1_LOCK, T2_LOCK, PT_LOCK, EVENT

        while p.is_alive():
            #print("p is alive")
            time.sleep(1.0)
            continue
        else:
            p.join(timeout=1.0)
            p.terminate()

            # kill threads
            t1.kill()
            t2.kill()

            ### LOCK
            lock.acquire()
            # unlock process flag
            P_LOCK = False

            # unlock thread flags
            T1_LOCK = False
            T2_LOCK = False
            PT_LOCK = False
            lock.release()
            ### UNLOCK

            if EVENT != 'Cancel':
                print('Error:  Realtime processing has died!')
                print("Please check input parameters and try again")

    ######################################################################
    #### define function to CREATE FIGURE WINDOW but don't open!- YET ####

    def create_fig_window(webfigs):
        """Creates and returns the output figure window object"""
        # change call based on figure output destination
        if webfigs:
            import PySimpleGUIWeb as sgf
        else:
            import PySimpleGUI as sgf

        image_elem = [sgf.Image(filename='', key='mytimeline'),
                      sgf.Image(filename='', key='mypolar'),
                      sgf.Image(filename='', key='myflexfig')]# NB the ORDER of the figure elements
        # is important for later - default order is assumed to be: 1) timeline, 2) polar, 3) array
        col = [[image_elem[1]], [image_elem[2]]]
        figlayout = [[image_elem[0], sgf.Column(col)]]

        figwindow = sgf.Window('Output Figures', figlayout, resizable=True)

        return figwindow, image_elem, figlayout
    ######################################################################

    ###########################################################################

    # set flags:
    # lock flags for child process and threads
    global F_LOCK, P_LOCK, T1_LOCK, T2_LOCK
    F_LOCK, P_LOCK, T1_LOCK, T2_LOCK, PT_LOCK = False, False, False, False, False
    lock = threading.Lock()

    #### CREATE AND OPEN THE GUI WINDOW ####

    if not web:
        window = sg.Window('Real-Time Tremor Analysis Tool', layout, font=("Helvetica", 11), \
        location=(400, 0), resizable=True)
    else:
        # can't use a GUI figure window with a web interface - or open a new web window - so append
        # the figure window to the existing web interface layout NOW, before window is created:
        dummy_webfigs = True
        figwindow, image_elem, figlayout = create_fig_window(dummy_webfigs) # set "webfigs flag"
        #figwindow.Finalize()
        F_LOCK = True

        layout_buffer = [[sg.Text('_'  * 150, size=(150, 1))], [sg.Text('Output Figures:',
                                                                        font=('Helvetica', 20))]]

        window = sg.Window('Real-Time Tremor Analysis Tool', layout + layout_buffer + figlayout)

    #### FINALIZE and OPEN the GUI window
    window.Finalize()

    #### RE-IMPORT
    if web:
        ## fetch default values
        from retreat.defaults.default_input_values import my_defaults
        defaults = my_defaults(os.getcwd())

        ## re-add default values (PySimpleGUIWeb doesn't seem to inherit these for some reason?!)
        for key in defaults:
            window.FindElement(key).Update(value=defaults[key])

    # find and add default image dimension values:
    from retreat.gui.gui_sizes import get_figure_dims
    mydims, quot = get_figure_dims(screenx, screeny, aspect)
    for key in ('timelinex', 'timeliney', 'polarx', 'polary', 'arrayx', 'arrayy', 'mapx', 'mapy'):
        window.FindElement(key).Update(value=mydims[key])

    #### WHILE LOOP OVER GUI EVENTS #######################################

    # begin while loop over button "EVENTS"
    while True:

        ##### READ INPUT DATA AND EVENTS FROM THE WINDOW
        EVENT, gui_input = window.Read()

        # fix InputCombo boxes in web interface mode
        if web:
            for key in ('connection', 'sds_type', 'dataformat', 'inv_type'):
                if gui_input[key] is None:
                    gui_input[key] = defaults[key][0]

        ######## START PRESSED - START REAL-TIME PROCESS ########
        if EVENT == 'Start':

            #print('P_LOCK =',P_LOCK)
            if not P_LOCK:
                try:
                    # start realtime routine as new child PROCESS using multiprocessing
                    print("Starting updates")

                    global logfile
                    logfile = gui_input["logpath"]+"/"+gui_input["logfile"]
                                    
                    # remove any existing log file:
                    os.remove(logfile)
                    os.remove(logfile+".offset")


                    mystdout = sys.stdout  # store this
                    p = Process(target=realtime, name='realtime', args=(gui_input, logfile))
                    #p.daemon = True - DISABLED since daemons cannot have children :-(
                    if 'p' not in locals() or 'p' not in globals() or not p.is_alive():
                        ptime = time.time() # capture start time for realtime process
                        p.start()
                        if p.is_alive():
                            P_LOCK = True

                    sys.stdout = mystdout # reset

                    ## start log file and figure monitoring routines as new THREADS:

                    # 1. monitor log file and print output to screen:

                    if 't1' not in locals() or 't1' not in globals():
                        t1 = KThread(target=print_log_to_screen, args=(logfile,), daemon=True)
                    if not t1.is_alive() and not T1_LOCK:
                        t1.start()
                        T1_LOCK = True

                    ## NOW CREATE AND OPEN THE FIGURE WINDOW

                    if not F_LOCK:
                        figwindow, image_elem, figlayout = create_fig_window(gui_input["webfigs"])
                        figwindow.Finalize()
                        F_LOCK = True
                        if not gui_input["webfigs"]:
                            #figwindow.Maximize()
                            figwindow.Refresh()
                            F_LOCK = True
                    if not web:
                        window.TKroot.focus_force()
                        if not gui_input["webfigs"]:
                            figwindow.Maximize()
                            figwindow.Refresh()

                    # 2. monitor figures and update:

                    if 't2' not in locals() or 't2' not in globals():
                        t2 = KThread(target=update_image_window, args=(image_elem, figwindow,\
                        gui_input["figpath"], gui_input["savefig"], gui_input["timelinefigname"],\
                        gui_input["polarfigname"], gui_input["arrayfigname"],\
                        gui_input["mapfigname"], gui_input["polar"], gui_input["resp"],\
                        gui_input["bazmap"], ptime), daemon=True)

                    if not t2.is_alive() and not T2_LOCK:
                        t2.start()
                        T2_LOCK = True

                    # 3. monitor realtime process:
                    pt = KThread(target=monitor_children, args=(p, t1, t2, lock), daemon=True)

                    if not pt.is_alive() and not PT_LOCK:
                        pt.start()
                        PT_LOCK = True

                except StopIteration:

                    print("Execution cancelled. Press Start to restart.")

                    # stop process and threads

                    # kill children of p
                    for child in psutil.Process(p.pid).children(recursive=True):
                        if child.is_running():
                            child.kill()

                    # kill any remaining children
                    for child in psutil.Process(os.getpid()).children(recursive=True):
                        if child.is_running():
                            child.kill()

                    # terminate p ... gracefully if possible
                    p.join(timeout=1.0)
                    p.terminate()

                    t1.kill()
                    t2.kill()
    #                if 'pt' in locals() or 'pt' in globals():
                    pt.kill()

                    # unlock flags
                    P_LOCK = False
                    T1_LOCK = False
                    T2_LOCK = False
                    PT_LOCK = False

                except Exception as e:

                    print('Exception occurred')

                    # stop process and threads

                    # kill children of p
                    for child in psutil.Process(p.pid).children(recursive=True):
                        if child.is_running():
                            child.kill()

                    # kill any remaining children
                    for child in psutil.Process(os.getpid()).children(recursive=True):
                        if child.is_running():
                            child.kill()
                    # terminate p ... gracefully if possible
                    p.join(timeout=0.5)
                    p.terminate()

                    # kill monitoring threads
                    if 't1' in locals() or 't1' in globals():
                        t1.kill()
                    if 't2' in locals() or 't2' in globals():
                        t2.kill()
                    if 'pt' in locals() or 'pt' in globals():
                        pt.kill()

                    # unlock flags
                    P_LOCK = False
                    T1_LOCK = False
                    T2_LOCK = False
                    PT_LOCK = False

                    print(traceback.format_exc())
                    print("Error: Please check input parameters and try again")

        ######## CANCEL PRESSED ########
        if EVENT == 'Stop':

            print('Stop button pressed')

            # Do NOTHING - OR, stop execution if already started

            # terminate any child process
            if 'p' in locals() or 'p' in globals():
                if p.is_alive():
                    print("Stopping application...")
                    # kill children of p
                    for child in psutil.Process(p.pid).children(recursive=True):
                        if child.is_running():
                            child.kill()
                            time.sleep(0.1)

                    # kill any remaining children
                    for child in psutil.Process(os.getpid()).children(recursive=True):
                        if child.is_running():
                            child.kill()
                    # terminate p ... gracefully if possible
                    p.join(timeout=3.0)
                    p.terminate()
                    P_LOCK = False

            # kill monitoring threads
            if 't1' in locals() or 't1' in globals():
                t1.kill()
                T1_LOCK = False
            if 't2' in locals() or 't2' in globals():
                t2.kill()
                T2_LOCK = False
            if 'pt' in locals() or 'pt' in globals():
                pt.kill()
                PT_LOCK = False

        ######## EXIT PRESSED ########
        if EVENT == 'Exit':

            # position and create a popup button:
            if not web:
                if quot != 1.0:
                    res = sg.PopupYesNo('Are you sure you wish to close the program?', \
                    location=(100+mydims["timelinex"]/2, mydims["timeliney"]/2))
                else:
                    res = sg.PopupYesNo('Are you sure you wish to close the program?')
            else:
                res = sg.PopupYesNo('Are you sure you wish to close the program?')

            if res == 'Yes':
                print("Exiting")

                # kill children of p
                if 'p' in locals() or 'p' in globals():
                    if p.is_alive():
                        for child in psutil.Process(p.pid).children(recursive=True):
                            if child.is_running():
                                child.kill()
                # kill any remaining children
                for child in psutil.Process(os.getpid()).children(recursive=True):
                    if child.is_running():
                        child.kill()

                # terminate p ... gracefully if possible
                if 'p' in locals() or 'p' in globals():
                    if p.is_alive():
                        p.join(timeout=2.0)
                        p.terminate()

                # kill monitoring threads
                if 't1' in locals() or 't1' in globals():
                    t1.kill()
                if 't2' in locals() or 't2' in globals():
                    t2.kill()
                if 'pt' in locals() or 'pt' in globals():
                    pt.kill()

                # close windows and exit everything
                if 'figwindow' in locals() or 'figwindow' in globals():
                    figwindow.Close()
                window.Close()
                raise SystemExit("Exit button pressed")
            else:
                print("Exit cancelled")

        ######## X (CLOSE) PRESSED ########
        # window closed by pressing X
        if EVENT is None:
            # terminate any child process
            if 'p' in locals() or 'p' in globals():
                print("Stopping application...")

                # kill children of p
                for child in psutil.Process(p.pid).children(recursive=True):
                    if child.is_running():
                        child.kill()

                # kill any remaining children
                for child in psutil.Process(os.getpid()).children(recursive=True):
                    if child.is_running():
                        child.kill()

                # terminate p ... gracefully if possible
                p.join(timeout=1.0)
                p.terminate()

            # kill monitoring threads
            if 't1' in locals() or 't1' in globals():
                t1.kill()
            if 't2' in locals() or 't2' in globals():
                t2.kill()
            if 'pt' in locals() or 'pt' in globals():
                pt.kill()
            break
