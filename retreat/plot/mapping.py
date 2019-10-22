"""mapping - set of functions used in plotting of map figure"""
def deg2num(lat_deg, lon_deg, zoom):
    """Returns OSM tile coordinates based on a given lat, lon and zoom level"""
    import math
    lat_rad = math.radians(lat_deg)
    n = 2.0 ** zoom
    xtile = int((lon_deg + 180.0) / 360.0 * n)
    ytile = int((1.0 - math.log(math.tan(lat_rad) + (1 / math.cos(lat_rad))) / math.pi) / 2.0 * n)
    return (xtile, ytile)

def num2deg(xtile, ytile, zoom):
    """
    http://wiki.openstreetmap.org/wiki/Slippy_map_tilenames
    This returns the NW-corner of the square.
    Use the function with xtile+1 and/or ytile+1 to get the other corners.
    With xtile+0.5 & ytile+0.5 it will return the center of the tile.
    """
    import math
    n = 2.0 ** zoom
    lon_deg = xtile / n * 360.0 - 180.0
    lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * ytile / n)))
    lat_deg = math.degrees(lat_rad)
    return (lat_deg, lon_deg)

def get_image_cluster(lat_deg, lon_deg, delta_lat, delta_long, zoom, to_plot):
    """Returns image 'cluster' - i.e. downloads relevant tiles and creates combined image"""
    from urllib.request import urlopen
    from io import BytesIO
    from PIL import Image
    smurl = r"http://a.tile.opentopomap.org/{0}/{1}/{2}.png"
    xmin, ymax = deg2num(lat_deg, lon_deg, zoom)
    xmax, ymin = deg2num(lat_deg + delta_lat, lon_deg + delta_long, zoom)

    #bbox_ul = num2deg(xmin, ymin, zoom)
    bbox_ll = num2deg(xmin, ymax + 1, zoom)
    #print bbox_ul, bbox_ll

    bbox_ur = num2deg(xmax + 1, ymin, zoom)
    #bbox_lr = num2deg(xmax + 1, ymax +1, zoom)
    #print bbox_ur, bbox_lr

    if to_plot["first"]: # fetch/download image tiles
        cluster = Image.new('RGB', ((xmax-xmin+1)*256-1, (ymax-ymin+1)*256-1))
        for xtile in range(xmin, xmax+1):
            for ytile in range(ymin, ymax+1):
                try:
                    imgurl = smurl.format(zoom, xtile, ytile)
                    print("Opening: " + imgurl)
                    imgstr = urlopen(imgurl).read()
                    tile = Image.open(BytesIO(imgstr))
                    cluster.paste(tile, box=((xtile-xmin)*255, (ytile-ymin)*255))
                except:
                    print("Couldn't download image")
                    tile = None
    else: # reload existing locally stored image
        figname = to_plot["figpath"] + "basemap.png" # get path BUT hardcode the fileNAME for now...
        cluster = Image.open(figname)

    return cluster, [bbox_ll[1], bbox_ll[0], bbox_ur[1], bbox_ur[0]]

def displace(lon, lat, theta, distance):
    """
    Displace a Lat, Lon theta degrees counterclockwise and some
    meters in that direction.
    Notes:
        http://www.movable-type.co.uk/scripts/latlong.html
        0 DEGREES IS THE VERTICAL Y AXIS! IMPORTANT!
    Args:
        theta:    A number in degrees.
        distance: A number in meters.
    Returns:
        A new Lat, Lon.
    """
    import numpy as np
    E_RADIUS = 6371.0 # mean earth radius in km
    theta = np.float32(theta)

    delta = np.divide(np.float32(distance), np.float32(E_RADIUS))

    def to_radians(theta):
        """Converts angle in degress to radians"""
        return np.divide(np.dot(theta, np.pi), np.float32(180.0))

    def to_degrees(theta):
        """Converts angle in radians to degrees"""
        return np.divide(np.dot(theta, np.float32(180.0)), np.pi)

    theta = to_radians(theta)
    lat1 = to_radians(lat)
    lng1 = to_radians(lon)

    lat2 = np.arcsin(np.sin(lat1) * np.cos(delta) + np.cos(lat1) * np.sin(delta) * np.cos(theta))

    lng2 = lng1 + np.arctan2(np.sin(theta) * np.sin(delta) * np.cos(lat1),
                             np.cos(delta) - np.sin(lat1) * np.sin(lat2))

    lng2 = (lng2 + 3 * np.pi) % (2 * np.pi) - np.pi

    return to_degrees(lat2), to_degrees(lng2)
