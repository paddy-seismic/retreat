"""set_font_sizes.py"""
import numpy as np

def set_font_sizes(xdim, plot_type):
    """Sets the font sizes based on the figure dimensions.
    Formulas based on sigmoid functions, with different versions
    for MainTimeline and array/map/polar plots"""

    ##### MainTimeline #####
    if plot_type == "timeline":

        # small font size
        fss = 13 - 4./(1 + (xdim/1375)**12)
        fssr = np.round(2.0*fss)/2.0 # round to nearest 0.5

        # med font size
        fsm = 15 - 5./(1 + (xdim/1375)**12)
        fsmr = np.round(2.0*fsm)/2.0 # round to nearest 0.5

        # large font size
        fsl = 18 - 4.5/(1 + (xdim/1450)**20)
        fslr = np.round(2.0*fsl)/2.0 # round to nearest 0.5

    ##### f-k polar/array resp/map #####
    elif plot_type in ('fkpolar', 'resp', 'map'):

        # small font size
        fss = 13 - 5./(1 + (xdim/560)**15)
        fssr = np.round(2.0*fss)/2.0 # round to nearest 0.5

        # med font size
        fsm = 15 - 5./(1 + (xdim/540)**12)
        fsmr = np.round(2.0*fsm)/2.0 # round to nearest 0.5

        # large font size
        fsl = 18.5 - 6.5/(1 + (xdim/550)**10)
        fslr = np.round(2.0*fsl)/2.0 # round to nearest 0.5

    return (fssr, fsmr, fslr)
