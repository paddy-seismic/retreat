"""get_nth"""
def get_nth(thedict, n):
    """
    Returns nth values from lists in dictionary of
    parameters for the nth array
    """
    newdict = dict()
    for key, value in thedict.items():
        if isinstance(value, list):
            newdict[key] = value[n]
        else:
            newdict[key] = value

    return newdict
