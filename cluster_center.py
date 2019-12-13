from math import cos, sin, sqrt, atan2

def average_geolocation(coords):
    '''Calculate the center/average of multiple Geolocation coordinates
       Expects list of tuples (latitude, longitude)
       Returns a tuple for the center'''

    PI = 3.14159265358979
    x = 0.0
    y = 0.0
    z = 0.0
    lat_most = 0.0
    lon_most = 0.0

    if len(coords) == 1:
        return coords[0]

    # Calculate most digites after decimal
    for coord in coords:
        coord_lat = coord[0]
        coord_lon = coord[1]
        most = digits(coord_lat)
        if lat_most < most:
            lat_most = most

        most = digits(coord_lon)
        if lon_most < most:
            lon_most = most

        latitude = coord_lat * PI / 180
        longitude = coord_lon * PI / 180

        x = x + cos(latitude) * cos(longitude)
        y = y + cos(latitude) * sin(longitude)
        z = z + sin(latitude)

    total = len(coords)

    x = x / total
    y = y / total
    z = z / total

    central_longitude = atan2(y, x)
    central_squareRoot = sqrt(x * x + y * y)
    central_latitude = atan2(z, central_squareRoot)

    latitude = cut_decimal(central_latitude * 180 / PI, lat_most)
    longitude = cut_decimal(central_longitude * 180 / PI, lon_most)
    return (latitude, longitude)


def cut_decimal(f, i):
    num = str(f)
    period = num.find(".") + 1
    if period == 0:
        return float(num & "." + (i * "0"))

    decimals = len(num) - period
    if decimals < i:
        return float(num + ((i - decimals) * "0"))
    return float(num[0:period + i])


def digits(d):
    '''Count how many digits are to the right of the decimal'''
    return len(str(d).split('.')[-1])