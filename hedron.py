import pandas as pd

class Cluster(pd.DataFrame):
    """Holds a pandas DataFrame with coordinate data"""
    def __init__(self, df, lat_header, lon_header, date_time_header, id_header=''):
        pd.DataFrame.__init__(self, df)
        self.lat_header = lat_header
        self.lon_header = lon_header
        self.id_header = id_header
        self.date_time_header = date_time_header
        # Add day column
        df['day'] = df[date_time_header].dt.date


    def make_clusters(self, digits):
        return SuperCluster(cluster_coords(self, self.lat_header, self.lon_header, digits))


class SuperCluster(dict):
    """Holds multiple Cluster Objects"""
    def __init__(self, data):
        dict.__init__(self, data)

    def clusters(self):
        return self.values()

    def names(self):
        return self.keys()



def main():
    # Load data into DataFrame
    df = pd.read_csv('test_coords.csv')
    # Check for headers
    if not {'Registration ID', 'Date Formatted', 'Latitude', 'Longitude'}.issubset(df.columns):
        return 'Headers Missing'
    # Remove duplicates
    df.drop_duplicates(['Registration ID', 'Date Formatted', 'Latitude', 'Longitude'], inplace=True)

    # Fix dates
    df = fix_df_dates(df, 'Date Formatted')

    c = Cluster(df, 'Latitude', 'Longitude', 'Date Formatted', 'Registration ID')

    # Make coordinate clusters
    clusters = c.make_clusters(3)
    print(len(clusters))

    # Filter clusters to colocation clusters
    #colocations = f

    #day_co = f



def day_colocations_clusters(clusters, day_header, id_header):
    """Check each cluster for ids on same day"""
    # future summary function output {key:day, ids counts}
    # this function output all the metadata for each day colocation point
    out = dict()
    for key,df in clusters.items():
        day_co = day_colocations(df, day_header, id_header)
        if len(day_co) > 0:
            out[key] = day_co
    return out


def day_colocations(cluster, day_header, id_header):
    cluster = cluster.copy()
    day_clusters = cluster.groupby(day_header)
    colocated = {key:df for key, df in day_clusters if len(df[id_header].unique())>1}
    if len(colocated) == 0:
        return pd.DataFrame()
    # Add back date to each df
    for key, df in colocated.items():
        df[day_header] = [key for _ in range(len(df))]
    # Combine DataFrames
    return pd.concat(colocated.values(), axis=0)


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


def fix_df_dates(df, date_header):
    df = df.copy()
    df[date_header] = df[date_header].apply(fix_date)
    df[date_header] = pd.to_datetime(df[date_header])
    return df


def fix_date(date):
    return date.split('(')[0]


if __name__ == '__main__':
    main()
