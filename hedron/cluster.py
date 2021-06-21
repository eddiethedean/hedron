import pandas as pd
from hedron import cluster_functions as cl
from .maps import plot_cluster, plot_super_cluster, plot_heat_map


class Cluster(pd.DataFrame):
    """Holds a pandas DataFrame with coordinate data"""
    def __init__(self,
                 df,
                 lat_header,
                 lon_header,
                 date_time_header,
                 id_header,
                 colors=None):
        pd.DataFrame.__init__(self, df)
        self.lat_header = lat_header
        self.lon_header = lon_header
        self.id_header = id_header
        self.date_time_header = date_time_header
        self.day_header = 'day'
        self.colors = colors
        if len(df) == 0: return

        # Try to convert columns to correct data types
        self[lat_header] = self[lat_header].astype(float)
        self[lon_header] = self[lon_header].astype(float)
        self[date_time_header] = pd.to_datetime(df[date_time_header])
        self[id_header] = self[id_header].astype(str)
        # Add day column
        df[self.day_header] = df[date_time_header].dt.date

    @property
    def lats(self):
        return self[self.lat_header]

    @property
    def lons(self):
        return self[self.lon_header]

    @property
    def ids(self):
        return self[self.id_header]

    @property
    def dates(self):
        return self[self.date_time_header]

    @property
    def days(self):
        return self[self.day_header]

    def plot(self, size=(800, 500)):
        return plot_cluster(self, size=size)

    def make_clusters(self, digits):
        if len(self)==0: return SuperCluster(dict())
        return convert_dict_to_super(self,
                                     cl.cluster_coords(self,
                                                       self.lat_header,
                                                       self.lon_header,
                                                       digits),
                                    colors=self.colors)

    def colocation_clusters(self, digits):
        if len(self)==0: return SuperCluster(dict())
        return convert_dict_to_super(self,
                                     cl.colocation_cluster_coords(self,
                                                                  self.lat_header,
                                                                  self.lon_header,
                                                                  self.id_header,
                                                                  digits),
                                    colors=self.colors)

    def day_colocation_cluster(self):
        if len(self)==0: return self
        return Cluster(cl.day_colocations(self,
                                          self.day_header,
                                          self.id_header),
                       self.lat_header,
                       self.lon_header,
                       self.date_time_header,
                       self.id_header,
                       colors=self.colors)

    def day_colocation_clusters(self):
        if len(self)==0: return SuperCluster(dict())
        return convert_dict_to_super(self,
                                     cl.day_colocations(self,
                                                        self.day_header,
                                                        self.id_header,
                                                        merge=False),
                                     colors=self.colors)


class SuperCluster(dict):
    """Holds multiple Cluster Objects"""

    def __init__(self, iterable, colors=None):
        dict.__init__(self, iterable)
        self.colors = colors

    def plot(self):
        return plot_super_cluster(self)

    def plot_heat(self, p):
        return plot_heat_map(self, p)

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

    @property
    def ids(self):
        out = []
        for c in self.values():
            out.extend(list(c.ids))
        return out

    @property
    def lats(self):
        out = []
        for c in self.values():
            out.extend(list(c.lats))
        return out

    @property
    def lons(self):
        out = []
        for c in self.values():
            out.extend(list(c.lons))
        return out

    # TODO: to_xlsx method, stores each cluster in a tab. saves in xlsx file

def convert_dict_to_super(cluster, d, colors=None):
    if len(d)==0: return SuperCluster(dict())
    return SuperCluster({key:Cluster(df,
                                     cluster.lat_header,
                                     cluster.lon_header,
                                     cluster.date_time_header,
                                     cluster.id_header) for key, df in d.items()})