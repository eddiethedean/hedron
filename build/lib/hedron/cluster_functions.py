import pandas as pd


def main():
    # Load data into DataFrame
    ids = ['a','b','c','d','e','f']
    dates = pd.to_datetime(['Dec 6, 2019 2:27:45 PM', 'Dec 6, 2019 2:27:45 PM', 'Dec 8, 2019 2:27:45 PM', 'Dec 8, 2019 2:27:45 PM', 'Dec 10, 2019 2:27:45 PM', 'Dec 11, 2019 2:27:45 PM'])
    lats = [29.4259671, 29.42525, 29.4237056, 29.423606, 29.4239835, 29.4239835]
    lons = [-98.4861419, -98.4860167, -98.4868973, -98.4860462, -98.4851705, -98.4851705]
    df = pd.DataFrame({'ID':ids, 'Date':dates, 'Latitude':lats, 'Longitude':lons})
    # Check for headers
    if not {'ID', 'Date', 'Latitude', 'Longitude'}.issubset(df.columns):
        return print('Headers Missing')

    # Add day column
    df['day']  = pd.to_datetime(df['Date']).dt.date

    # Make coordinate clusters
    clusters = cluster_coords(df, 'Latitude', 'Longitude', 3)

    # Filter clusters to colocation clusters
    colocations = colocation_clusters(clusters, 'ID')

    # Make colocation clusters from DataFrame
    all_at_once_colocations = colocation_cluster_coords(df, 'Latitude', 'Longitude', 'ID', 3)

    print(len(clusters))
    print(len(colocations))
    print(len(all_at_once_colocations))

    day_co = day_colocations_clusters(colocations, 'day', 'ID')

    print(len(day_co))


def day_colocations_clusters(clusters, day_header, id_header):
    """Check each cluster for ids on same day"""
    out = dict()
    for key,df in clusters.items():
        day_co = day_colocations(df, day_header, id_header)
        if len(day_co) > 0:
            out[key] = day_co
    return out


def day_colocations(cluster, day_header, id_header, merge=True):
    cluster = cluster.copy()
    day_clusters = cluster.groupby(day_header)
    colocated = {key:df for key, df in day_clusters if len(df[id_header].unique())>1}
    if len(colocated) == 0:
        return pd.DataFrame()
    # Add back date to each df
    for key, df in colocated.items():
        df[day_header] = [key for _ in range(len(df))]
    if merge == True:
        # Combine DataFrames
        return pd.concat(colocated.values(), axis=0)
    else:
        return colocated


def cluster_coords(df, lat_header, lon_header, digits):
    df = df.copy()
    # Make lat,lon hash column
    df['hash'] = [hash_latlon(lat, lon, digits) for lat, lon in zip(df[lat_header], df[lon_header])]
    # Make dict with hash:cluster, clusters need more than 1 point to count as a cluster
    return {key:cluster_df for key, cluster_df in df.groupby('hash') if len(cluster_df) > 1}


def colocation_clusters(clusters, id_header):
    """Return only clusters with more than one id"""
    return {key:df for key, df in clusters.items() if len(df[id_header].unique()) > 1}


def colocation_cluster_coords(df, lat_header, lon_header, id_header, digits):
    df = df.copy()
    # Make lat,lon hash column
    df['hash'] = [hash_latlon(lat, lon, digits) for lat, lon in zip(df[lat_header], df[lon_header])]
    # Make dict with hash:colocation cluster, clusters need more than 1 id to be a colocation cluster
    return {key:cluster_df for key, cluster_df in df.groupby('hash') if len(cluster_df[id_header].unique()) > 1}


def hash_latlon(lat, lon, i):
    """Get hash from lat/lon | 14.60775948, -90.65505981, 3 --> '14.607,-90.655"""
    return cut_decimal(lat, i) + ',' + cut_decimal(lon, i)


def cut_decimal(f, i):
    """Converts float f to a string with i digits after decimal place"""
    num = str(f)
    period = num.find(".") + 1
    if period == 0:
        return num & "." + (i * "0")
    decimals = len(num) - period
    if decimals < i:
        return num + ((i - decimals) * "0")
    return num[0:period + i]


if __name__ == '__main__':
    main()
