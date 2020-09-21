import dash
from dash.dependencies import Input, Output, State
import plotly.graph_objects as go


def register_callbacks(app):
    # callback for the map
    @app.callback(
         Output('alpha-evolution', 'figure'),
        [Input('model-dropdown', 'value')])
    def update_output(layer):
        fig = go.Figure()
        return fig