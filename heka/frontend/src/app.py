import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import yaml
import os
import plotly.io as pio
import flask
from flask_caching import Cache


config = yaml.safe_load(os.getenv("PROJECT_CONFIG", "---"))

try:
    base = "/{}/".format(config["project"]["name"])
except KeyError:
    base = "/"


pio.templates.default = "plotly_white"


server = flask.Flask(__name__)

app = dash.Dash(
    __name__,
    requests_pathname_prefix=base,
    routes_pathname_prefix=base,
    include_assets_files=False,
    server=server
)

cache = Cache(
    app.server,
    config={"CACHE_TYPE": "filesystem", "CACHE_DIR": "cache-directory"},
)


app.title = "INERIS Dashboard"

# HTML skeleton
full_path = os.path.realpath(__file__)
directory = os.path.dirname(full_path)
file = open(directory + "/index_string.html", "r")
app.index_string = file.read()

app.config.suppress_callback_exceptions = True

# Default layout
app.layout = html.Div(
    [dcc.Location(id="url", refresh=False), html.Div(id="page-content")]
)

# Pages
from Besoin1.callback import register_callbacks as besoin1_callbacks
from Besoin1.layout import layout as besoin1_layout

from Besoin3.callback import register_callbacks as besoin3_callbacks
from Besoin3.layout import layout as besoin3_layout


# Callbacks
besoin1_callbacks(app)
besoin3_callbacks(app)


# Routing
@app.callback(
    dash.dependencies.Output("page-content", "children"),
    [dash.dependencies.Input("url", "pathname")],
)
def display_page(pathname):
    if pathname == f"{base}besoin1":
        return besoin1_layout
    elif pathname == f"{base}besoin3":
        return besoin3_layout
    else:
        return besoin1_layout


if __name__ == "__main__":
    app.run_server(debug=True, host="0.0.0.0", port=80)

