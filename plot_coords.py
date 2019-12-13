import folium
from cluster_center import average_geolocation

def coords_plot(coords, zoom=50):
    #Calculate center
    center = average_geolocation(coords)
    # Build map 
    coords_map = folium.Map(location=center, zoom_start=zoom, 
    tiles='cartodbpositron', width=640, height=480)
    [folium.CircleMarker(coords[i], radius=1,
            color='#0080bb', fill_color='#0080bb').add_to(coords_map) 
            for i in range(len(coords))]
    return coords_map
    