import dash
import yaml
import os
from flask_caching import Cache
import flask

config = yaml.safe_load(os.getenv("PROJECT_CONFIG", "---"))

try:
    base = "/{}/".format(config["project"]["name"])
except KeyError:
    base = "/"

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
