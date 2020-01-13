"""add_logos"""
def add_logos(fig, offset=0):
    """Adds RETREAT and EUROVOLC logos to a given figure"""

    # import tools
    import os
    import matplotlib.cbook as cbook
    import matplotlib.image as image

    cwd = os.getcwd()
    ## define and load the logo images
    # RETREAT
    retreat_logo_file = cbook.get_sample_data(cwd+"/doc/retreat_trans48.png", asfileobj=False)
    im_ret = image.imread(retreat_logo_file)
    # EUROVOLC
    eurovolc_logo_file = cbook.get_sample_data(cwd+"/doc/EUROVOLC-logo-32.png", asfileobj=False)
    im_euro = image.imread(eurovolc_logo_file)
    eurologo_width = 116 #px

    ## Now add logos to the figure:

    # RETREAT - Lower left
    fig.figimage(im_ret, 1, 0, zorder=10)

    # EUROVOLC - Lower right
    fig.figimage(im_euro, fig.bbox.xmax-(eurologo_width+offset), 0, zorder=10)
