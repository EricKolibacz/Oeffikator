"""Main visualization module containing a dash app."""
import requests
from dash import Dash, Input, Output, ctx, dcc, exceptions, html, no_update

from visualization import settings
from visualization.map import get_folium_map

INPUT_ID = "input-id"
NEW_POINTS_BUTTON_ID = "new-points-button-id"
MAP_ID = "map-id"
STORED_VALUE_ID = "stored-valued-id"
INTERVAL_ID = "interval-id"
NUMBER_OF_NEW_TRIPS = 32

app = Dash(__name__)
server = app.server
BASE_URL = f"http://{settings.app_container_name}:8000"

print("This is the base url %s,", BASE_URL)
INITIAL_LOCATION_DESCRIPTION = "Friedrichstr. 50"

app.layout = html.Div(
    children=[
        html.H1(children="Oeffikator"),
        html.Div(
            [
                "Location Description: ",
                dcc.Input(
                    id=INPUT_ID,
                    value=INITIAL_LOCATION_DESCRIPTION,
                    type="text",
                    debounce=True,
                ),  # dcc.Store stores the intermediate value
                dcc.Store(
                    id=STORED_VALUE_ID,
                    data=requests.get(f"{BASE_URL}/location/{INITIAL_LOCATION_DESCRIPTION}", timeout=5).json(),
                ),
            ]
        ),
        html.Br(),
        html.Button("New Points", id=NEW_POINTS_BUTTON_ID, n_clicks=0),
        html.Br(),
        html.Br(),
        html.Div("Number of Points:", id="number-of-points"),
        html.Br(),
        html.Iframe(id=MAP_ID, width=1000, height=500),
        dcc.Interval(id=INTERVAL_ID, interval=10 * 1000, n_intervals=3),
    ]
)


@app.callback(
    Output(MAP_ID, "srcDoc"),
    Input(INTERVAL_ID, "n_intervals"),
    Input(STORED_VALUE_ID, "data"),
)
def update_figure(n_intervals: int, location: dict) -> str:
    """Periodically update the figure

    Args:
        n_intervals (int): number of updates done already
        location (dict): current display location

    Returns:
        str: docstring of the iFrame
    """
    if n_intervals < 3:
        response_trip = requests.get(f"{BASE_URL}/all_trips/{location['id']}", timeout=5).json()
        if response_trip != []:
            docsrc = get_folium_map(response_trip)
            return docsrc
    return no_update


@app.callback(
    Output("number-of-points", "children"),
    Output(STORED_VALUE_ID, "data"),
    Output(INTERVAL_ID, "n_intervals"),
    Input(INPUT_ID, "value"),
    Input(NEW_POINTS_BUTTON_ID, "n_clicks"),
    Input(STORED_VALUE_ID, "data"),
)
def get_location(location_description: str, _, location) -> list[str, int]:
    """Updates the figure whenever a new location is entered or the "New points" button is clicked

    Args:
        location_description (str): _description_
        _ (int): ignored parameter from button

    Raises:
        exceptions.PreventUpdate: if the location is not given, the update function should not be called

    Returns:
        list[str, int]: the intrated frame (html string) as string and the number of trips known for the given location
    """
    if location_description is None:
        # PreventUpdate prevents ALL outputs updating
        raise exceptions.PreventUpdate
    if ctx.triggered_id == NEW_POINTS_BUTTON_ID:
        requests.put(
            f"{BASE_URL}/trips/{location_description}", params={"number_of_trips": NUMBER_OF_NEW_TRIPS}, timeout=180
        )
    elif ctx.triggered_id == INPUT_ID:
        location = requests.get(f"{BASE_URL}/location/{location_description}", timeout=5).json()
        print("Using %s", location)

    response_trip = requests.get(f"{BASE_URL}/all_trips/{location['id']}", timeout=5).json()
    if response_trip == []:
        requests.put(f"{BASE_URL}/trips/{location_description}", params={"number_of_trips": 9}, timeout=180).json()
        requests.put(
            f"{BASE_URL}/trips/{location_description}", params={"number_of_trips": NUMBER_OF_NEW_TRIPS}, timeout=180
        ).json()

    return f"Number of Points: {len(response_trip)}", location, 0


if __name__ == "__main__":
    # For Development only, otherwise use uvicorn launch, e.g.
    # uvicorn visualization.main:app --host 0.0.0.0 --port 8080
    app.run_server(host="0.0.0.0", port=8082, debug=True)
