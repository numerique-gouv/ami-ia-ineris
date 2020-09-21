import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import plotly.graph_objects as go


def Graph(id, height=280):
    fig = go.Figure()
    fig.update_layout(
        template="plotly_white", margin=dict(t=0, b=0, r=40, l=40), height=height
    )
    return dcc.Graph(
        id=id,
        figure=fig,
        config={
            "modeBarButtonsToRemove": [
                "toggleSpikelines",
                "pan2d",
                "select2d",
                "lasso2d",
                "hoverClosestCartesian",
                "hoverCompareCartesian",
                "autoScale2d",
                "zoom2d",
                "zoomIn2d",
                "zoomOut2d",
            ],
            "displaylogo": False,
        },
    )


def ChartCard(id, description=False, height=280):
    body = (
        [html.H5(description, className="text-dark pb-2"), Graph(id, height)]
        if description
        else Graph(id, height)
    )
    return dbc.Card([dbc.CardBody(body),], className="shadow mb-4",)


def KPICard(title, id, icon, color, appendix=""):
    return (
        dbc.Card(
            dbc.CardBody(
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                html.Div(
                                    title,
                                    className=f"text-xs font-weight-bold text-{color} text-uppercase mb-1",
                                ),
                                html.Div(
                                    [
                                        html.Span("...", id=id),
                                        html.Small(appendix, className="text-muted pl-2"),
                                    ],
                                    className="h5 mb-0 font-weight-bold text-gray-800",
                                ),
                            ],
                            className="mr-2",
                        ),
                        html.Div(
                            html.I([], className="fas fa-2x text-gray-300 " + icon),
                            className="col-auto",
                        ),
                    ],
                    className="no-gutters align-items-center",
                )
            ),
            className=f"border-left-{color} shadow h-100 py-2",
        ),
    )

