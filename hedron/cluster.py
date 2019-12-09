import pandas as pd
from . import cluster_functions as cl


class Cluster:
    """Holds a pandas DataFrame with coordinate data"""
    def __init__(self, data, lat_header, lon_header, date_time_header='', id_header=''):
        self.data = pd.DataFrame(data)
        self.lat_header = lat_header
        self.lon_header = lon_header
        self.id_header = id_header
        self.date_time_header = date_time_header
        self.day_header = 'day'
        if len(self.data) == 0: return

        # Try to convert columns to correct data types
        self.data[lat_header] = self.data[lat_header].astype(float)
        self.data[lon_header] = self.data[lon_header].astype(float)

        if date_time_header != '':
            self.data[date_time_header] = pd.to_datetime(self.data[date_time_header])
            # Add day column
            self.data[self.day_header] = self.data[date_time_header].dt.date

        if id_header != '':
            self.data[id_header] = self.data[id_header].astype(str)

    def __len__(self):
        return len(self.data)

    def __str__(self):
        return self.data.__str__()

    def __repr__(self):
        return self.data.__repr__()

    def __getitem__(self, key):
        return self.data[key]

    def __setitem__(self, key, value):
        self[key] = value

    def __copy__(self):
        return Cluster(self.data, self.lat_header, self.lon_header, self.date_time_header, self.id_header)

    def copy(self):
        return self.__copy__()

    def groupby(self, *args):
        return self.data.groupby(*args)

    def make_clusters(self, digits):
        """Groups all the coordinates based on the beginning digits of the latitude and longitude
           Each coordinate is "hashed" - if digits is 3, 29.423706, -98.486897 --> '29.423,-98.486'
           3 digit hashes result in coordinates within 110 Meters of each other
           Returns a SuperCluster object that is a dict that holds Cluster objects"""
        if len(self)==0: return SuperCluster(dict())
        return convert_dict_to_super(self, cl.cluster_coords(self.data, self.lat_header, self.lon_header, digits))

    def colocation_clusters(self, digits):
        """Groups all the coordinates based on the beginning digits of the latitude and longitude
           Each coordinate is "hashed" - if digits is 3, 29.423706, -98.486897 --> '29.423,-98.486'
           3 digit hashes result in coordinates within 110 Meters of each other
           Only keeps clusters that have more than one unuique id that are considered colocation
           Returns a SuperCluster object that is a dict that holds Cluster objects"""
        if self.id_header == '':
            raise Exception('colocation_clusters requires an id Series with an id_header')
        if len(self)==0: return SuperCluster(dict())
        return convert_dict_to_super(self, cl.colocation_cluster_coords(self, self.lat_header, self.lon_header, self.id_header, digits))

    def day_colocation_cluster(self, inplace=False):
        """Filters out events in the Cluster that did not happen on the same day as another id
           Returns a Cluster containing all the same day colocation events"""
        if self.date_time_header == '':
            raise Exception('day_colocation_cluster requires a date/time Series with a date_time_header')
        if self.id_header == '':
            raise Exception('day_colocation_cluster requires an id Series with an id_header')

        if len(self)==0:
            if inplace == False:
                return self
            else:
                return

        out = Cluster(cl.day_colocations(self, self.day_header, self.id_header), self.lat_header, self.lon_header, self.date_time_header, self.id_header)

        if inplace:
            self.data = out.data
        else:
            return out

    def day_colocation_clusters(self):
        """Groups all the coordinates based on the beginning digits of the latitude and longitude
           Each coordinate is "hashed" - if digits is 3, 29.423706, -98.486897 --> '29.423,-98.486'
           3 digit hashes result in coordinates within 110 Meters of each other
           Only keeps clusters that have more than one unuique id that are considered colocation
           colocation Clusters only contain events that happen on the same day
           Returns a SuperCluster object that is a dict that holds Cluster objects"""
        if self.date_time_header == '':
            raise Exception('day_colocation_clusters requires a date/time Series with a date_time_header')
        if self.id_header == '':
            raise Exception('day_colocation_clusters requires an id Series with an id_header')
        if len(self)==0: return SuperCluster(dict())
        return convert_dict_to_super(self, cl.day_colocations(self, self.day_header, self.id_header, merge=False))

    def merge(self, c):
        """Combine two clusters"""
        pass # TODO:


class SuperCluster(dict):
    """Holds multiple Cluster Objects"""
    def clusters(self):
        return self.values()

    def names(self):
        return self.keys()

    def colocation_clusters(self, inplace=False):
        """Filters out clusters that don't have more than one id"""
        if len(self)==0:
            if inplace:
                return
            else:
                return self
        out = SuperCluster({key:cluster for key, cluster in self.items() if len(cluster[cluster.id_header].unique())>1})
        if inplace:
            self = out
        else:
            return SuperCluster({key:cluster for key, cluster in self.items() if len(cluster[cluster.id_header].unique())>1})

    def merge(self):
        """Combine all clusters into one cluster"""
        pass # TODO:

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
    ids = ['a','b','c','d','e','f']
    dates = pd.to_datetime(['Dec 6, 2019 2:27:45 PM', 'Dec 6, 2019 2:27:45 PM', 'Dec 8, 2019 2:27:45 PM', 'Dec 8, 2019 2:27:45 PM', 'Dec 10, 2019 2:27:45 PM', 'Dec 11, 2019 2:27:45 PM'])
    lats = [29.4259671, 29.42525, 29.4237056, 29.423606, 29.4239835, 29.4239835]
    lons = [-98.4861419, -98.4860167, -98.4868973, -98.4860462, -98.4851705, -98.4851705]
    df = pd.DataFrame({'ID':ids, 'Date':dates, 'Latitude':lats, 'Longitude':lons})
    # Check for headers
    if not {'ID', 'Date', 'Latitude', 'Longitude'}.issubset(df.columns):
        return print('Headers Missing')

    c = Cluster(df, lat_header='Latitude', lon_header='Longitude', date_time_header='Date', id_header='ID')

    # Make coordinate clusters
    clusters = c.make_clusters(3)
    print(len(clusters))

    # Filter clusters to colocation clusters
    colocations = clusters.colocation_clusters()
    print(len(colocations))

    day_co = colocations.day_colocation_clusters()
    print(len(day_co))


if __name__ == '__main__':
    main()
