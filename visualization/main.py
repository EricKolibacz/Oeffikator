"""Main visualization module containing a dash app."""
import requests
from dash import Dash, Input, Output, ctx, dcc, exceptions, html

from visualization import settings
from visualization.map import get_folium_map

MAP_ID = "map-id"
INPUT_ID = "input-id"
ADDRESS_ID = "address-id"
SLIDER_DIV_ID = "slider-div-id"
SLIDER_ID = "silder-id"

INITIAL_SLIDER_VALUE = 0.75

app = Dash(__name__, meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}])
server = app.server
BASE_URL = f"http://{settings.app_container_name}:8000"

print("This is the base url %s,", BASE_URL)

app.layout = html.Div(
    children=[
        html.H1(children="Oeffikator", style={"textAlign": "center"}),
        html.Div(
            [
                dcc.Input(
                    id=INPUT_ID,
                    placeholder="Friedrichstr. 50",
                    type="text",
                    debounce=True,
                    style={"width": 300},
                ),
            ],
            style={"textAlign": "center"},
        ),
        html.Br(),
        html.Div(
            "",
            id=ADDRESS_ID,
            style={"textAlign": "center"},
        ),
        html.Br(),
        html.Div(
            [
                html.Iframe(srcDoc=get_folium_map(None, INITIAL_SLIDER_VALUE), id=MAP_ID, width="80%", height="100%"),
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
            id="new-points-button",
            n_clicks=0,
            style={"textAlign": "center"},
        ),
    ]
)


@app.callback(
    Output(MAP_ID, "srcDoc"),
    Output(component_id="number-of-points", component_property="children"),
    Output(ADDRESS_ID, "children"),
    Output(SLIDER_DIV_ID, "hidden"),
    Input(INPUT_ID, component_property="value"),
    Input(component_id="new-points-button", component_property="n_clicks"),
    Input(SLIDER_ID, "value"),
)
def update_figure(location_description: str, _, slider_value: float) -> list[str, int]:
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
    if ctx.triggered_id == "new-points-button":
        print("New points, yummy...")
        print("New points, yummy...")
        requests.put(f"{BASE_URL}/trips/{location_description}", params={"number_of_trips": 5}, timeout=180)

    print("Rendering figure")
    response_location = requests.get(f"{BASE_URL}/location/{location_description}", timeout=5).json()
    print("%s", response_location)

    response_trip = requests.get(f"{BASE_URL}/all_trips/{response_location['id']}", timeout=5).json()

    docsrc = get_folium_map(response_trip, slider_value)

    return docsrc, f"{len(response_trip)} Points", response_location["address"], False


if __name__ == "__main__":
    # For Development only, otherwise use uvicorn launch, e.g.
    # uvicorn visualization.main:app --host 0.0.0.0 --port 8080
    app.run_server(host="0.0.0.0", port=8082, debug=True)
