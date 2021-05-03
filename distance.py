from geopy.distance import great_circle

def distance(lat1, lon1, lat2, lon2, measurement='miles'):
    p1 = (lat1, lon1)
    p2 = (lat2, lon2)
    m = measurement.lower()
    if m == 'miles':
        return great_circle(p1, p2).miles
    elif m == 'km':
        return great_circle(p1, p2).km
    elif m == 'nm':
        return great_circle(p1, p2).nm
    elif m == 'meters':
        return great_circle(p1, p2).meters