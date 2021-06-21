# hedron
A python package project for doing analysis on coordinates and clustering them.

Create Cluster objects by passing in your geolocation data in a pandas DataFrame and the Latitude and Longitude column header names. Quickly and easily identify where the clusters are in your geolocation data by using Cluster objects in your pandas workflow.

Use the make_clusters method with precision parameter set to 6 in order to create a SuperCluster object that contains all the different Cluster objects inside the same geohash. 6 digits gives you Clusters with coordinates within 150 Meters of each other.

Further clustering methods allow for more refinement like colocation with different IDs in the same Cluster and same day colocation where multiple IDs are colocated in the same Cluster on the same day.
