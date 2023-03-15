"""Module to create the map with overlaying image."""
import imageio.v3 as iio
from folium import Map, Marker, raster_layers
from shapely import from_wkt

from visualization.heatmap import get_heatmap

from . import settings


def get_folium_map(trip_response: dict) -> str:
    """Create the map with overlaying image

    Args:
        trip_response (dict): a list of trips in .json format

    Returns:
        str: html file as string
    """
    buf, xlim, ylim = get_heatmap(trip_response)
    img = iio.imread(buf)

    origin = trip_response[0]["origin"]
    origin_geom = from_wkt(origin["geom"])
    origin_coordinates = [origin_geom.y, origin_geom.x]

    # Create a map using Stamen Terrain, centered on study area with set zoom level
    map_object = Map(
        location=[from_wkt(trip_response[0]["origin"]["geom"]).y, from_wkt(trip_response[0]["origin"]["geom"]).x],
        min_lon=settings.max_west,
        max_lon=settings.max_east,
        min_lat=settings.max_south,
        max_lat=settings.max_north,
        max_bounds=True,
        tiles="Stamen Terrain",
        zoom_start=13,
        min_zoom=13,
    )

    map_bounds = [[ylim[0], xlim[0]], [ylim[1], xlim[1]]]
    # Overlay raster called img using add_child() function (opacity and bounding box set)
    map_object.add_child(raster_layers.ImageOverlay(img, opacity=0.8, bounds=map_bounds))
    Marker(origin_coordinates, popup=origin["address"], tooltip="Click me").add_to(map_object)
    return map_object.get_root().render()
