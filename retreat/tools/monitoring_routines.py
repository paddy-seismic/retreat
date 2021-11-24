"""monitoring_routines"""
import sys
import os
import time
import glob
#import traceback
#from pygtail import Pygtail

def follow(thefile):
    """Approximate pythonic implementation of tail -f"""
    while True:
        line = thefile.readline()
        if not line or not line.endswith('\n'):
            time.sleep(0.2)
            continue
        yield line

def print_log_to_screen(log_file, window):
    """updates and prints output from log file to gui output window"""
    while True:
        if os.path.exists(log_file):
            logfile = open(log_file, "r")
            loglines = follow(logfile)
            for line in loglines:
                sys.stdout.write(line)
                if window is not None:
                    window.Refresh()

def print_log_to_terminal(log_file):
    """updates and prints output from log file to terminal"""
    while True:
        if os.path.exists(log_file):
            logfile = open(log_file, "r")
            loglines = follow(logfile)
            for line in loglines:
                sys.stdout.write(line)

def update_image_window(image_elem, figwindow, figpath, savefig, timelinefig, polarfig, arrayfig,\
    mapfig, polar, resp, bazmap, ptime):
    """checks for new and updated figures and updates the gui window"""
    #print('Thread t2 (images) id: {}'.format(os.getpid()))

#    # redirect output to log file:
#    sys.stdout = open(logfile, 'a+')
#    sys.stderr = sys.stdout

    figwindow.Refresh()

    # process arguments:
    fignames = [timelinefig, polarfig]

    # get list of figures we are dealing with:
    figdex = [0] # timeline - always plotted by default
    if polar:
        figdex.append(1)

    # only one of resp or bazmap (or neither) should be selected
    # (should already have thrown error if both chosen to plot)
    if resp:
        figdex.append(2)
        fignames.append(arrayfig)
    if bazmap:
        figdex.append(2)
        fignames.append(mapfig)

    # while loop to try and restart if exeception:
    while True:
        try:
            if not savefig: # using default (temporary) file names only that get overwritten

                # initialise some variables:
                ii = 0
                moddate1 = [0] * 3
                moddate2 = [0] * 3
                array_plotted = False

                while True:

                    #print('Checking figures...')
#                    print(figdex)

                    for j in figdex: # loop over indices of figures we need to process

                        image_filename = figpath + "/" + fignames[j] + ".png"

                        if os.path.exists(image_filename):
                           # print(image_filename + ' exists')
                            #print("ii = ",ii)
#                            print("moddate1 = ", moddate1)

                            # get mod time of image 1st time in loop
                            if ii < 1:
                                moddate1[j] = os.stat(image_filename)[8]
                            else:

        #                        print("j = ",j)
                                moddate2[j] = os.stat(image_filename)[8]

                                if j < 2: # i.e. figure is NOT array plot

#                                    print("moddate1[j] = ",moddate1[j])
#                                    print("moddate2[j] = ",moddate2[j])

                                    if moddate2[j] > moddate1[j] and moddate2[j] > ptime:
                                    # i.e. image has changed, AND timestamp is newer
                                    # than update process start time (NOT an old file)

#                                        print(moddate1)
#                                        print(moddate2)
                                        # image changed - reload !
                                        print('Adding ' + image_filename + ' to figure window')
                                        #print('image_elem[j]=',image_elem[j])
                                        #print(image_elem[0].__class__)
                                        #print('figwindow=',figwindow)

                                        try:
                                            image_elem[j].Update(filename=image_filename)
                                         #   print('Updated OK')
                                        except Exception as e:
                                            print('Error:', e)
                                        #image_elem[j].Update(filename=image_filename)
                                        #figwindow.Refresh()

                                        # reset mod date
                                        moddate1[j] = moddate2[j]

                                else: # either map or array response

                                    if bazmap:

#                                        print("Checking map figure")
#                                        print("moddate1[j] = ",moddate1[j])
#                                        print("moddate2[j] = ",moddate2[j])
#                                        print("ptime = ",ptime)

                                        if moddate2[j] > moddate1[j] and moddate2[j] > ptime:
                                        # i.e. image has changed, AND timestamp is newer
                                        # than update process start time (NOT an old file)

                                            #print(moddate1)
                                            #print(moddate2)
                                            # image changed - reload !
                                            #print('Adding ' + image_filename + ' to figure window')
                                            image_elem[j].Update(filename=image_filename)
                                            figwindow.Refresh()

                                            # reset mod date
                                            moddate1[j] = moddate2[j]

                                    if resp:
                                        # array plot - only updated ONCE at start -
                                        # so just compare to ptime
                                        if moddate2[j] > ptime and not array_plotted:
                                            # image changed - reload !
                                            #print('Updating image: ' + image_filename)
                                            image_elem[j].Update(filename=image_filename)
                                            figwindow.Refresh()

                                            array_plotted = True

                            # increment counter
                            ii = ii+1
                        else:

                            #print(image_filename+ " does not exist (yet)")
                            continue
                    time.sleep(2)

            ### savefig set - unique figure filenames:
            else:
                # initialise

                array_plotted = False
                moddate = [0] * 3
                myalreadyplottedfig = [0] * 3

                while True:
                    for j in figdex:
                        #print("j = ",j)
                        #print(figpath + "/" + fignames[j] + "*_"+ ("[0-9]" * 6) +".png")

                        # get list of files, sort by date and choose last
                        files = glob.glob(figpath + "/" + fignames[j] + "*_"+ ("[0-9]" * 6) +".png")
                        files.sort(key=os.path.getmtime)

                        if len(files) > 0: # i.e. at least one file exists

                            image_filename = files[-1]
                            #print("image_filename = ", image_filename)

                            # get modified time and check it is a new file (newer than ptime)
                            moddate[j] = os.stat(image_filename)[8]

                            if j < 2:  # i.e. figure is NOT array plot
                                if moddate[j] > ptime and image_filename != myalreadyplottedfig[j]:
                                    #print("Adding " + image_filename + " to figure window\n")
                                    image_elem[j].Update(filename=image_filename)
                                    myalreadyplottedfig[j] = image_filename
                                    figwindow.Refresh()
                            else:

                                if bazmap:
                                    if moddate[j] > ptime and \
                                    image_filename != myalreadyplottedfig[j]:
                                        #print("Adding " + image_filename + " to figure window\n")
                                        image_elem[j].Update(filename=image_filename)
                                        myalreadyplottedfig[j] = image_filename
                                        figwindow.Refresh()

                                if resp:

                                 # array plot - only updated ONCE at start
                                    if moddate[j] > ptime and not array_plotted:
                                        #print('Adding ' + image_filename + ' to figure window\n')
                                        image_elem[j].Update(filename=image_filename)
                                        figwindow.Refresh()
                                        array_plotted = True
                        else:
                            #print(image_filename+ " does not exist (yet)")
                            continue

                    time.sleep(1.5)

        except:
        # restart
            pass
