"""Main visualization module containing a dash app."""
import time

import requests
from dash import Dash, Input, Output, ctx, dcc, html, no_update
from PIL import Image

from visualization import settings
from visualization.map import get_folium_map

INPUT_ID = "input-id"
POINTS_BUTTON_ID = "points-button-id"
MAP_ID = "map-id"
ADDRESS_ID = "address-id"
LOADING_ID = "loading-id"
SLIDER_DIV_ID = "slider-div-id"
SLIDER_ID = "silder-id"
INITIAL_SLIDER_VALUE = 0.75
CONFIRM_ID = "confirm-id"
CONFIRM_SUBMITTED_CLICKS_ID = "confirm_submitted_clicks_id"
SUBMITTED_ADDRESSES = 0
STORED_VALUE_ID = "stored-valued-id"
NUMBER_OF_NEW_TRIPS = 32


app = Dash(__name__, meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}])
server = app.server
BASE_URL = f"http://{settings.app_container_name}:8000"

print("This is the base url %s,", BASE_URL)
INITIAL_LOCATION_DESCRIPTION = "Friedrichstr. 50"

app.layout = html.Div(
    children=[
        html.Div(
            children=[
                html.H1(
                    children="Oeffikator",
                    style={
                        "textAlign": "center",
                        "display": "inline-block",
                        "verticalAlign": "middle",
                    },
                ),
                html.A(
                    children=html.Img(src=Image.open("visualization/images/github-mark.png"), height=24),
                    href="https://github.com/EricKolibacz/Oeffikator",
                    target="_blank",
                ),
            ],
            style={"textAlign": "center"},
        ),
        html.Div(
            [
                dcc.Input(
                    id=INPUT_ID,
                    placeholder="Friedrichstr. 50",
                    type="text",
                    debounce=True,
                    style={"width": 300},
                ),  # dcc.Store stores the intermediate value
                dcc.Store(
                    id=STORED_VALUE_ID,
                    data=requests.get(f"{BASE_URL}/location/{INITIAL_LOCATION_DESCRIPTION}", timeout=5).json(),
                ),
            ],
            style={"textAlign": "center"},
        ),
        dcc.ConfirmDialog(id=CONFIRM_ID),  # dcc.Store stores the intermediate value
        dcc.Store(
            id=CONFIRM_SUBMITTED_CLICKS_ID,
            data=SUBMITTED_ADDRESSES,
        ),
        html.Br(),
        dcc.Loading(
            id=LOADING_ID,
            type="default",
            children=html.Div(
                "",
                id=ADDRESS_ID,
                style={"textAlign": "center"},
            ),
        ),
        html.Br(),
        html.Div(
            [
                html.Iframe(srcDoc=get_folium_map(None, INITIAL_SLIDER_VALUE), id=MAP_ID, width="50%", height="100%"),
            ],
            style={"textAlign": "center", "height": "66vh"},
        ),
        html.Br(),
        html.Div(
            [
                dcc.Slider(
                    0,
                    1,
                    0.25,
                    value=INITIAL_SLIDER_VALUE,
                    marks={
                        0: {"label": "0"},
                        0.25: {"label": "0.25"},
                        0.5: {"label": "0.5"},
                        0.75: {"label": "0.75"},
                        1: {"label": "1"},
                    },
                    id=SLIDER_ID,
                ),
            ],
            id=SLIDER_DIV_ID,
            hidden=True,
            style={"width": "50%", "padding-left": "25%", "padding-right": "25%"},
        ),
        html.Br(),
        html.Div(
            "",
            id="number-of-points",
            style={"textAlign": "right", "fontSize": 10},
        ),
        html.Button(
            "More Points",
            id=POINTS_BUTTON_ID,
            n_clicks=0,
            style={"textAlign": "center"},
            hidden=True,
        ),
    ]
)


@app.callback(
    Output(CONFIRM_ID, "displayed"),
    Output(CONFIRM_ID, "message"),
    Output(STORED_VALUE_ID, "data"),
    Input(INPUT_ID, "value"),
    prevent_initial_call=True,
)
def display_confirm(location_description: str) -> list[bool, str, dict]:
    """Displays the address confirmation window

    Args:
        location_description (str): description of the address

    Returns:
        list[bool, str, dict]: if the message should be displayed, the message of the display
                               and the location data to be stored
    """
    if location_description != "":
        location = requests.get(f"{BASE_URL}/location/{location_description}", timeout=5).json()
        print("Using %s", location)
        return True, f"We found following address:\n\n{location['address']}\n\nIs this address correct?", location
    return False, "", None


@app.callback(
    Output(ADDRESS_ID, "children"),
    Output(SLIDER_DIV_ID, "hidden"),
    Output(MAP_ID, "srcDoc"),
    Output("number-of-points", "children"),
    Output(POINTS_BUTTON_ID, "hidden"),
    Input(CONFIRM_ID, "submit_n_clicks_timestamp"),
    Input(CONFIRM_ID, "cancel_n_clicks_timestamp"),
    Input(POINTS_BUTTON_ID, "n_clicks"),
    Input(STORED_VALUE_ID, "data"),
    Input(SLIDER_ID, "value"),
    prevent_initial_call=True,
)
def get_location(last_submit: int, last_cancel: int, _, location: dict, opacity: float) -> list[str, int]:
    """Updates the figure whenever a new location is entered or the "New points" button is clicked

    Args:
        last_submit (int): when the last submit happened
        last_cancel (int): when the last cancel happened
        _ (int): ignored parameter from button
        location (dict): the stored location

    Raises:
        exceptions.PreventUpdate: if the location is not given, the update function should not be called

    Returns:
        list[str, int]: the intrated frame (html string) as string and the number of trips known for the given location
    """
    location_address = no_update
    is_hidden_slider = no_update
    total_trips = no_update

    if ctx.triggered_id != SLIDER_ID:
        if ctx.triggered_id == POINTS_BUTTON_ID:
            total_trips = len(requests.get(f"{BASE_URL}/all_trips/{location['id']}", timeout=5).json())
            requests.put(
                f"{BASE_URL}/trips/{location['address']}", params={"number_of_trips": NUMBER_OF_NEW_TRIPS}, timeout=180
            )
            while total_trips + NUMBER_OF_NEW_TRIPS - 3 > len(
                requests.get(f"{BASE_URL}/all_trips/{location['id']}", timeout=5).json()
            ):
                time.sleep(1)
        elif last_cancel is None or last_submit > last_cancel:
            response_trip = requests.get(f"{BASE_URL}/all_trips/{location['id']}", timeout=5).json()
            if response_trip == []:
                requests.put(f"{BASE_URL}/trips/{location['address']}", params={"number_of_trips": 9}, timeout=180)
                while 9 > len(requests.get(f"{BASE_URL}/all_trips/{location['id']}", timeout=5).json()):
                    time.sleep(0.5)
                requests.put(
                    f"{BASE_URL}/trips/{location['address']}",
                    params={"number_of_trips": NUMBER_OF_NEW_TRIPS},
                    timeout=180,
                )
                while 9 + NUMBER_OF_NEW_TRIPS - 3 > len(
                    requests.get(f"{BASE_URL}/all_trips/{location['id']}", timeout=5).json()
                ):
                    time.sleep(1)
            is_hidden_slider = False
            location_address = location["address"]

    response_trip = requests.get(f"{BASE_URL}/all_trips/{location['id']}", timeout=5).json()
    docsrc = get_folium_map(response_trip, opacity)

    return location_address, is_hidden_slider, docsrc, f"#Points {len(response_trip)}", False


if __name__ == "__main__":
    # For Development only, otherwise use uvicorn launch, e.g.
    # uvicorn visualization.main:app --host 0.0.0.0 --port 8080
    app.run_server(host="0.0.0.0", port=8082, debug=True)
