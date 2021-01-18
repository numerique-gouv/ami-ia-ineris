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

from Besoin2.callback import register_callbacks as besoin2_callbacks
from Besoin2.layout import layout as besoin2_layout

from Besoin2_final.callback import register_callbacks as besoin2_final_callbacks
from Besoin2_final.layout import layout as besoin2_final_layout

from Besoin3.callback import register_callbacks as besoin3_callbacks
from Besoin3.layout import layout as besoin3_layout

from Bdd.callback import register_callbacks as bdd_callbacks
from Bdd.layout import layout as bdd_layout

from Bdd_analysis.callback import register_callbacks as bdd_analysis_callbacks
from Bdd_analysis.layout import layout as bdd_analysis_layout

from Boucle_retour.callback import register_callbacks as Boucle_retour_callbacks
from Boucle_retour.layout import layout as Boucle_retour_layout

from Besoin3ech.callback import register_callbacks as besoin3ech_callbacks
from Besoin3ech.layout import layout as besoin3ech_layout


# Callbacks
besoin1_callbacks(app)
besoin2_callbacks(app)
besoin2_final_callbacks(app)
besoin3_callbacks(app)
bdd_callbacks(app)
bdd_analysis_callbacks(app)
Boucle_retour_callbacks(app)
besoin3ech_callbacks(app)

# Routing
@app.callback(
    dash.dependencies.Output("page-content", "children"),
    [dash.dependencies.Input("url", "pathname")],
)
def display_page(pathname):
    if pathname == f"{base}besoin1":
        return besoin1_layout
    if pathname == f"{base}besoin2_exploration":
        return besoin2_layout
    if pathname == f"{base}besoin2_analyse":
        return besoin2_final_layout
    elif pathname == f"{base}besoin3dash":
        return besoin3_layout
    elif pathname == f"{base}besoin3ech":
        return besoin3ech_layout
    elif pathname == f"{base}bdd":
        return bdd_layout
    elif pathname == f"{base}bdd_analysis":
        return bdd_analysis_layout
    elif pathname == f"{base}resultats":
        return Boucle_retour_layout
    else:
        return bdd_layout

if __name__ == "__main__":
    app.run_server(debug=True, host="0.0.0.0", port=80)

