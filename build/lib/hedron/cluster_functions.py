import pandas as pd
from pygeodesy import geohash


geohash_data = {}

def calculate_geohashes(lats, lons, precision):
    hashes = []
    for lat, lon in zip(lats, lons):
        if (lat, lon, precision) in geohash_data:
            h = geohash_data[(lat, lon, precision)]
        else:
            h = geohash.encode(lat, lon, precision)
            geohash_data[(lat, lon, precision)] = h
        hashes.append(h)
    return hashes


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


def cluster_coords(df, lat_header, lon_header, precision):
    df = df.copy()
    # Make lat,lon hash column
    df['hash'] = calculate_geohashes(df[lat_header], df[lon_header], precision)
    # Make dict with hash:cluster, clusters need more than 1 point to count as a cluster
    return {key:cluster_df for key, cluster_df in df.groupby('hash') if len(cluster_df) > 1}


def colocation_clusters(clusters, id_header):
    """Return only clusters with more than one id"""
    return {key:df for key, df in clusters.items() if len(df[id_header].unique()) > 1}


def colocation_cluster_coords(df, lat_header, lon_header, id_header, precision):
    df = df.copy()
    # Make lat,lon hash column
    df['hash'] = calculate_geohashes(df[lat_header], df[lon_header], precision)
    # Make dict with hash:colocation cluster, clusters need more than 1 id to be a colocation cluster
    return {key:cluster_df for key, cluster_df in df.groupby('hash') if len(cluster_df[id_header].unique()) > 1}