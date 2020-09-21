import json
import pandas as pd
import geopandas as gpd
import plotly.graph_objects as go


with open('/heka/dash/input/\'s-Hertogenbosch.geojson', 'r') as f:
    geojson = json.load(f)

geo_data = pd.read_csv("/heka/dash/input/den_bosch_geo_data.csv").round(2)
geo_data = geo_data.dropna()


def make_stacked_bar(feature, pc6_list):
    if feature == "Age":
        filters = ['INW_014', 'INW_1524', 'INW_2544', 'INW_4564', 'INW_65PL']
        top_labels = ["0-14", "15-24", "25-44", "45-64", "65PL"]
        colors = ['rgba(38, 24, 74, 0.8)', 'rgba(71, 58, 131, 0.8)',
          'rgba(122, 120, 168, 0.8)', 'rgba(164, 163, 204, 0.85)',
          'rgba(190, 192, 213, 1)']
    elif feature == "Built year":
        filters = ['WONVOOR45', 'WON_4564', 'WON_6574', 'WON_7584', 'WON_8594', 'WON_9504', 'WON_0514',]
        top_labels = ["VOOR45", "45-64", "65-74", "75-84", "85-94", "95-04", "05-14"]
        colors = ['rgba(38, 24, 74, 0.8)', 'rgba(71, 58, 131, 0.8)',
          'rgba(122, 120, 168, 0.8)', 'rgba(164, 163, 204, 0.85)',
          'rgba(190, 192, 213, 1)', 'rgb(205,207,223, 0.8)', 'rgba(221,222,233, 0.8)']
    elif feature == "Ownership":
        filters = ['P_HUURWON', 'P_KOOPWON']
        top_labels = ["HUUR", "KOOP"]
        colors = ['rgba(38, 24, 74, 0.8)', 'rgba(71, 58, 131, 0.8)']
    elif feature == "Gender":
        filters = ['MAN', 'VROUW']
        colors = ['rgba(38, 24, 74, 0.8)', 'rgba(71, 58, 131, 0.8)']
    elif feature == "Ethnicity":
        filters = ['P_NL_ACHTG', 'P_WE_MIG_A', 'P_NW_MIG_A',]
        top_labels = ["NL ACHTG", "WEST MIG", "NW MIG"]
        colors = ['rgba(38, 24, 74, 0.8)', 'rgba(71, 58, 131, 0.8)',
          'rgba(122, 120, 168, 0.8)']
    elif feature == "Household type":
        filters = ['TOTHH_EENP', 'TOTHH_MPZK', 'HH_EENOUD', 'HH_TWEEOUD']
        top_labels = ["EENP", "MPZK", "EEN OUD", "TWEE OUD"]
        colors = ['rgba(38, 24, 74, 0.8)', 'rgba(71, 58, 131, 0.8)',
          'rgba(122, 120, 168, 0.8)', 'rgba(164, 163, 204, 0.85)',]
    elif feature == "Market Response":
        filters = [ 'pBehoudend_y', 'pCalculerend_y', 'pIdealistisch_y', 'pVolgend_y', 'pGemakzuchtig_y', 'pSober_y',]
        top_labels = ['Behoudend', 'Calculerend', 'Idealistisch', 'Volgend', 'Gemakzuchtig', 'Sober']
        colors = ['rgba(38, 24, 74, 0.8)', 'rgba(71, 58, 131, 0.8)',
          'rgba(122, 120, 168, 0.8)', 'rgba(164, 163, 204, 0.85)',
          'rgba(190, 192, 213, 1)', 'rgb(205,207,223, 0.8)']

    x_data = geo_data[geo_data["PC6"].isin(pc6_list)].filter(filters).values
    y_data = pc6_list

    fig = go.Figure()

    for i in range(0, len(x_data[0])):
        for xd, yd in zip(x_data, y_data):
            fig.add_trace(go.Bar(
                x=[xd[i]], y=[yd],
                orientation='h',
                marker=dict(
                    color=colors[i],
                    line=dict(color='rgb(248, 248, 249)', width=1)
                ),
                name = top_labels[i],
            ))

    fig.update_layout(
        xaxis=dict(
            showgrid=False,
            showline=False,
            showticklabels=False,
            zeroline=False,
            domain=[0.15, 1]
        ),
        yaxis=dict(
            showgrid=False,
            showline=False,
            showticklabels=False,
            zeroline=False,
        ),
        barmode='stack',
        paper_bgcolor='rgb(255, 255, 255)',
        plot_bgcolor='rgb(255, 255, 255)',
        margin=dict(l=0, r=0, t=40, b=80),
        showlegend=False
    )

    annotations = []

    for yd, xd in zip(y_data, x_data):
        # labeling the y-axis
        annotations.append(dict(xref='paper', yref='y',
                                x=0.14, y=yd,
                                xanchor='right',
                                text=str(yd),
                                font=dict(family='Arial', size=10,
                                          color='rgb(67, 67, 67)'),
                                showarrow=False, align='right'))
        # labeling the first percentage of each bar (x_axis)
        annotations.append(dict(xref='x', yref='y',
                                x=xd[0] / 2, y=yd,
                                text=str(xd[0]) + '%',
                                font=dict(family='Arial', size=10,
                                          color='rgb(248, 248, 255)'),
                                showarrow=False))
        # labeling the first Likert scale (on the top)
        if yd == y_data[-1]:
            annotations.append(dict(xref='x', yref='paper',
                                    x=xd[0] / 2, y=1.1,
                                    text=top_labels[0],
                                    font=dict(family='Arial', size=10,
                                              color='rgb(67, 67, 67)'),
                                    textangle=270,
                                    showarrow=False))
        space = xd[0]
        for i in range(1, len(xd)):
                # labeling the rest of percentages for each bar (x_axis)
                annotations.append(dict(xref='x', yref='y',
                                        x=space + (xd[i]/2), y=yd,
                                        text=str(xd[i]) + '%',
                                        font=dict(family='Arial', size=10,
                                                  color='rgb(248, 248, 255)'),
                                        showarrow=False))
#                 # labeling the Likert scale
                if yd == y_data[-1]:
                    annotations.append(dict(xref='x', yref='paper',
                                            x=space + (xd[i]/2), y=1.1,
                                            text=top_labels[i],
                                            font=dict(family='Arial', size=10,
                                                      color='rgb(67, 67, 67)'),
                                            textangle=270,

                                            showarrow=False))
                space += xd[i]

    fig.update_layout(annotations=annotations)

    return fig