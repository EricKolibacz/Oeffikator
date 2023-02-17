"""Module to create the duration heatmap."""
import io

import matplotlib as plt
import matplotlib.colors as mcolors  # noqa
import matplotlib.pyplot as plt  # noqa
import numpy as np
import pandas as pd
from shapely import from_wkt

COLOR_DICT = {
    "red": ((0.0, 0.0, 0.0), (0.5, 0.0, 0.0), (1.0, 1.0, 1.0)),
    "blue": ((0.0, 0.0, 0.0), (1.0, 0.0, 0.0)),
    "green": ((0.0, 0.0, 1.0), (0.5, 0.0, 0.0), (1.0, 0.0, 0.0)),
}
CMAP = mcolors.LinearSegmentedColormap("my_colormap", COLOR_DICT, 100)


def get_heatmap(trip_response: dict) -> list[io.BytesIO, list[float, float], list[float, float]]:
    """Create the heatmap for given trips

    Args:
        trip_response (dict): a list of trips in .json format

    Returns:
        list[io.BytesIO, list[float, float], list[float, float]]: the overlay image and information on xlim and ylim
    """
    trips = pd.DataFrame.from_dict(
        {
            "lon": [from_wkt(trip["destination"]["geom"]).x for trip in trip_response],
            "lat": [from_wkt(trip["destination"]["geom"]).y for trip in trip_response],
            "duration": [trip["duration"] for trip in trip_response],
        }
    )

    fig, axis = plt.subplots(figsize=(18, 13))
    fig.subplots_adjust(0, 0, 1, 1)
    # ax.set_xlim(bounding_box_map[0], bounding_box_map[1])
    # ax.set_ylim(bounding_box_map[2], bounding_box_map[3])
    axis.set_facecolor((1, 1, 1, 0))

    # define the amount of color levels should be there
    levels = np.linspace(np.min(trips["duration"]), np.max(trips["duration"]), 60)
    axis.tricontourf(
        trips["lon"],
        trips["lat"],
        trips["duration"],
        levels=levels,
        alpha=0.5,
        cmap=CMAP,
        antialiased=True,
        zorder=-2,
    )
    # fig.colorbar(tcf, shrink=0.67, label="Travel Time in minutes", format="{x:.0f} min")

    # Displaying destination locations
    # ax.scatter(df["lon"], df["lat"], alpha=0.9, color="black", label="Journey Stops", zorder=-2)

    # ax.legend(fontsize="xx-large")
    plt.gca().set_axis_off()
    plt.subplots_adjust(top=1, bottom=0, right=1, left=0, hspace=0, wspace=0)
    plt.margins(0, 0)
    # fig.canvas.draw()
    # plt.savefig("test.png", bbox_inches="tight", pad_inches=0, transparent=True)
    # plt.close()
    buf = io.BytesIO()
    fig.savefig(buf)
    buf.seek(0)
    return buf, axis.get_xlim(), axis.get_ylim()


# get_image()
