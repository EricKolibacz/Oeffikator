import requests
from dash import Dash, Input, Output, ctx, dcc, exceptions, html

from visualization import settings
from visualization.map import get_folium_map

MAP_ID = "map-id"

app = Dash(__name__)
server = app.server
BASE_URL = f"http://{settings.app_container_name}:8000"

print("This is the base url %s,", BASE_URL)

app.layout = html.Div(
    children=[
        html.H1(children="Oeffikator"),
        html.Div(
            [
                "Location Description: ",
                dcc.Input(
                    id="my-input",
                    value="Friedrichstr. 50",
                    type="text",
                    debounce=True,
                ),
            ]
        ),
        html.Br(),
        html.Button("New Points", id="new-points-button", n_clicks=0),
        html.Br(),
        html.Br(),
        html.Div("Number of Points:", id="number-of-points"),
        html.Br(),
        html.Iframe(id=MAP_ID, width=1000, height=500),
    ]
)


@app.callback(
    Output(MAP_ID, "srcDoc"),
    Output(component_id="number-of-points", component_property="children"),
    Input(component_id="my-input", component_property="value"),
    Input(component_id="new-points-button", component_property="n_clicks"),
)
def update_figure(input_value, _):
    if input_value is None:
        # PreventUpdate prevents ALL outputs updating
        raise exceptions.PreventUpdate
    if ctx.triggered_id == "new-points-button":
        print("New points, yummy...")
        print("New points, yummy...")
        requests.put(f"{BASE_URL}/trips/{input_value}", params={"number_of_trips": 5}, timeout=180)
    return render_figure(input_value)


def render_figure(input_value):
    print("Rendering figure")
    response_location = requests.get(f"{BASE_URL}/location/{input_value}", timeout=5).json()
    print("%s", response_location)

    response_trip = requests.get(f"{BASE_URL}/all_trips/{response_location['id']}", timeout=5).json()

    docsrc = get_folium_map(response_trip)

    return docsrc, f"Number of Points: {len(response_trip)}"


if __name__ == "__main__":
    # For Development only, otherwise use uvicorn launch, e.g.
    # uvicorn visualization.main:app --host 0.0.0.0 --port 8080
    app.run_server(host="0.0.0.0", port=8081, debug=True)
