import pandas as pd
import cluster_functions as cl

class Cluster(pd.DataFrame):
    """Holds a pandas DataFrame with coordinate data"""
    def __init__(self, df, lat_header, lon_header, date_time_header, id_header):
        pd.DataFrame.__init__(self, df)
        self.lat_header = lat_header
        self.lon_header = lon_header
        self.id_header = id_header
        self.date_time_header = date_time_header
        self.day_header = 'day'
        if len(df) == 0: return

        # Try to convert columns to correct data types
        self[lat_header] = self[lat_header].astype(float)
        self[lon_header] = self[lon_header].astype(float)
        self[date_time_header] = pd.to_datetime(df[date_time_header])
        self[id_header] = self[id_header].astype(str)
        # Add day column
        df[self.day_header] = df[date_time_header].dt.date

    def make_clusters(self, digits):
        if len(self)==0: return SuperCluster(dict())
        return convert_dict_to_super(self, cl.cluster_coords(self, self.lat_header, self.lon_header, digits))

    def colocation_clusters(self, digits):
        if len(self)==0: return SuperCluster(dict())
        return convert_dict_to_super(self, cl.colocation_cluster_coords(self, self.lat_header, self.lon_header, self.id_header, digits))

    def day_colocation_cluster(self):
        if len(self)==0: return self
        return Cluster(cl.day_colocations(self, self.day_header, self.id_header), self.lat_header, self.lon_header, self.date_time_header, self.id_header)

    def day_colocation_clusters(self):
        if len(self)==0: return SuperCluster(dict())
        return convert_dict_to_super(self, cl.day_colocations(self, self.day_header, self.id_header, merge=False))


class SuperCluster(dict):
    """Holds multiple Cluster Objects"""
    def __init__(self, data):
        """data if a dictionary of Cluster objects"""
        dict.__init__(self, data)

    def clusters(self):
        return self.values()

    def names(self):
        return self.keys()

    def colocation_clusters(self):
        if len(self)==0: return self
        return SuperCluster({key:cluster for key, cluster in self.items() if len(cluster[cluster.id_header].unique())>1})

    def merge(self):
        # TODO: Combine each cluster into one cluster
        pass

    def day_colocation_clusters(self):
        if len(self)==0: return self
        day_clusters = dict()
        for key, cluster in self.items():
            c = cluster.day_colocation_cluster()
            if len(c) > 0:
                day_clusters[key] = c
        return SuperCluster(day_clusters)


    # TODO: to_xlsx method, stores each cluster in a tab. saves in xlsx file

def convert_dict_to_super(cluster, d):
    if len(d)==0: return SuperCluster(dict())
    return SuperCluster({key:Cluster(df, cluster.lat_header, cluster.lon_header, cluster.date_time_header, cluster.id_header) for key, df in d.items()})


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
    colocations = clusters.colocation_clusters()
    print(len(colocations))

    day_co = colocations.day_colocation_clusters()
    print(len(day_co))


def fix_df_dates(df, date_header):
    df = df.copy()
    df[date_header] = df[date_header].apply(fix_date)
    df[date_header] = pd.to_datetime(df[date_header])
    return df


def fix_date(date):
    return date.split('(')[0]


if __name__ == '__main__':
    main()
