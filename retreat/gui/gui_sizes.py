"""gui_sizes - collection of functions to return screen, window and figure dimensions"""
def get_screen_size():
    """Uses tkinter to calculate and return screen dimensions and aspect ratio"""
    # use tkinter (assume python3)
    from tkinter import Tk
    root = Tk()
    screenx = root.winfo_screenwidth()
    screeny = root.winfo_screenheight()
    root.destroy()
    # get aspect ratio
    myratio = screenx/screeny

    return screenx, screeny, myratio

def get_quotient(myratio):
    """Returns quotient based on aspect ratio. Used for detecting multiple screens. NB assumes
    monitor is most likely to be 16:9 or 4:3 aspect ratio"""
    if (myratio % (16.0/9.0)) < 0.01:
        #myaspect = '16:9'
        quot, rem = divmod(myratio, (16.0/9.0))
    elif (myratio % (4.0/3.0)) < 0.01:
        #myaspect = '4:3'
        quot, rem = divmod(myratio, (4.0/3.0))
    else:
        #myaspect = 'other'
        quot = 1.0
    return quot

def get_window_size(screenx, screeny, myratio):
    """Determines and returns size of main GUI window based on screen dimensions"""
    # process aspect ratio:
    quot = get_quotient(myratio)
    # correct x-dimension if necessary:
    if quot != 1.0:
        screenx = screenx/quot
    window_size = [screenx, screeny]

    return window_size

def get_figure_dims(x, y, myratio):
    """Determines and returns size of figure window based on screen dimensions"""
    # process aspect ratio:
    quot = get_quotient(myratio)

    # correct x-dimension if necessary:
    if quot != 1.0:
        x = x/quot

    # remove edge buffer
    nbuf = 50 # px
    x = x - (2*nbuf)
    y = y - (2*nbuf)

    # set dims:
    dims = dict()
    # Fig1 - timeline
    dims["timelinex"] = int(x-(y/2.))
    dims["timeliney"] = int(y)
    # Fig2 - polar
    dims["polarx"] = int(y/2.)
    dims["polary"] = int(y/2.)
    # Fig3 - array resp
    dims["arrayx"] = int(y/2.)
    dims["arrayy"] = int(y/2.)
    # Fig4 - map
    dims["mapx"] = int(y/2.)
    dims["mapy"] = int(y/2.)

    return dims, quot
