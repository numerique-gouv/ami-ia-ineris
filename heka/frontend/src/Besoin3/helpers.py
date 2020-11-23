import json
import pandas as pd
import geopandas as gpd
import plotly.graph_objects as go


from datetime import datetime, timedelta, date
import pandas as pd
import numpy as np
import pandas.io.sql as sqlio
import plotly.graph_objects as go
import yaml
import os
import psycopg2




def get_df_full_query(query):
    conf = yaml.load(os.environ["PROJECT_CONFIG"], Loader=yaml.SafeLoader)
    conn_string = "host={} \
        port=5432 dbname={} user={} \
        password={}".format(
        conf["project-database"]["hostname"],
        conf["project-database"]["name"],
        conf["project-database"]["user"],
        conf["project-database"]["password"],
    )
    conn = psycopg2.connect(conn_string)
    df = sqlio.read_sql_query(query, conn)
    conn.close()
    return df



def get_profile_evolution_model(start_date, end_date, profile, model):
    if start_date==None or end_date==None or profile==None or model==None:
        fig = go.Figure()
        fig.update_layout(
            margin=dict(t=0, b=0, r=40, l=40),
            height=300
        )
        return(fig)

    query=f"""SELECT date, contribution, uncertainty FROM public.regressor_results WHERE date < '{end_date}' 
              AND date >= '{start_date}' AND model = '{model}' AND profile = '{profile}' ORDER BY date"""

    df = get_df_full_query(query).rename(
        columns={"date": "Date", "contribution": "Contribution", "uncertainty": "Uncertainty"}
    )
    return dict(
        data = [
            dict(
                x = df["Date"],
                y = df["Contribution"]+df["Uncertainty"],
                line = dict(
                    color = "#b1c8d3",
                    dash = "1px",
                    width = 1,
                ),
                name = "Upper bound",
                mode = "line",), 
            dict(
                x = df["Date"],
                y = df["Contribution"]-df["Uncertainty"],
                line = dict(
                    color = "#b1c8d3",
                    dash = "1px",
                    width = 1,
                ),
                name = "Lower bound",
                fill = 'tonexty',
                mode = "line",),
            dict(
                x = df["Date"],
                y = df["Contribution"],
                line = dict(
                    color = "#3f4e59",
                    dash = "1px",
                    width = 1,
                ),
                name = "Contribution",
                mode = "line",),
        ],
        layout = dict(
            margin = dict(t = 0, b = 0, r = 40, l = 40),
            template = "plotly_white", 
            height = 300,
            xaxis_tickformat="%d %B (%a)\n%H:%M",
            legend = dict(
                orientation = "h",
                x = 0.5, xanchor = "center",
            ),
            yaxis = dict(
                exponentformat = "SI",
                automargin = True
            ),
        ),
    )



def get_profile_evolution(start_date, end_date, profile):
    if start_date==None or end_date==None or profile==None:
        fig = go.Figure()
        fig.update_layout(
            margin=dict(t=0, b=0, r=40, l=40),
            height=300
        )
        return(fig)

    query_PMF=f"""SELECT date, contribution, uncertainty FROM public.regressor_results WHERE date < '{end_date}' 
              AND date >= '{start_date}' AND model = 'PMF' AND profile = '{profile}' ORDER BY date"""
    query_LASSO=f"""SELECT date, contribution, uncertainty FROM public.regressor_results WHERE date < '{end_date}' 
              AND date >= '{start_date}' AND model = 'LASSO' AND profile = '{profile}' ORDER BY date"""
    query_ODR=f"""SELECT date, contribution, uncertainty FROM public.regressor_results WHERE date < '{end_date}' 
              AND date >= '{start_date}' AND model = 'ODR' AND profile = '{profile}' ORDER BY date"""

    df_PMF = get_df_full_query(query_PMF).rename(
        columns={"date": "Date", "contribution": "Contribution", "uncertainty": "Uncertainty"}
    )
    df_LASSO = get_df_full_query(query_LASSO).rename(
        columns={"date": "Date", "contribution": "Contribution", "uncertainty": "Uncertainty"}
    )
    df_ODR = get_df_full_query(query_ODR).rename(
        columns={"date": "Date", "contribution": "Contribution", "uncertainty": "Uncertainty"}
    )
    return dict(
        data = [
            dict(
                x = df_ODR["Date"],
                y = df_ODR["Contribution"]+df_ODR["Uncertainty"],
                line = dict(
                    color = "#b1c8d3",
                    dash = "1px",
                    width = 1,
                ),
                name = "ODR upper bound",
                mode = "line",), 
            dict(
                x = df_ODR["Date"],
                y = df_ODR["Contribution"]-df_ODR["Uncertainty"],
                line = dict(
                    color = "#b1c8d3",
                    dash = "1px",
                    width = 1,
                ),
                name = "ODR lower bound",
                fill = 'tonexty',
                mode = "line",),
            dict(
                x = df_ODR["Date"],
                y = df_ODR["Contribution"],
                line = dict(
                    color = "#3f4e59",
                    dash = "1px",
                    width = 1,
                ),
                name = "ODR Contribution",
                mode = "line",),
            dict(
                x = df_PMF["Date"],
                y = df_PMF["Contribution"],
                line = dict(
                    color = "#c71585",
                    dash = "1px",
                    width = 1,
                ),
                name = "PMF Contribution",
                mode = "line",),
            dict(
                x = df_LASSO["Date"],
                y = df_LASSO["Contribution"],
                line = dict(
                    color = "#0d98ba",
                    dash = "1px",
                    width = 1,
                ),
                name = "Lasso Contribution",
                mode = "line",),
        ],
        layout = dict(
            margin = dict(t = 0, b = 0, r = 40, l = 40),
            template = "plotly_white", 
            height = 300,
            xaxis_tickformat="%d %B (%a)\n%H:%M",
            legend = dict(
                orientation = "h",
                x = 0.5, xanchor = "center",
            ),
            yaxis = dict(
                exponentformat = "SI",
                automargin = True
            ),
        ),
    )


def get_coloc_data(start_date, end_date, coloc):
    if start_date==None or end_date==None or coloc==None:
        return(pd.Dataframe())

    query=f"""SELECT date, value FROM public.data_receptor_coloc WHERE date < '{end_date}' 
              AND date >= '{start_date}' and coloc = '{coloc}' ORDER BY 1"""

    df = get_df_full_query(query).rename(
        columns={"date": "Date", "value": "Value"}
    )
    return(df)


def get_profile_evolution_HOA(start_date, end_date):
    if start_date==None or end_date==None:
        fig = go.Figure()
        fig.update_layout(
            margin=dict(t=0, b=0, r=40, l=40),
            height=300
        )
        return(fig)

    query_PMF=f"""SELECT date, contribution, uncertainty FROM public.regressor_results WHERE date < '{end_date}' 
              AND date >= '{start_date}' AND model = 'PMF' AND profile = 'HOA' ORDER BY date"""
    query_LASSO=f"""SELECT date, contribution, uncertainty FROM public.regressor_results WHERE date < '{end_date}' 
              AND date >= '{start_date}' AND model = 'LASSO' AND profile = 'HOA' ORDER BY date"""
    query_ODR=f"""SELECT date, contribution, uncertainty FROM public.regressor_results WHERE date < '{end_date}' 
              AND date >= '{start_date}' AND model = 'ODR' AND profile = 'HOA' ORDER BY date"""

    df_PMF = get_df_full_query(query_PMF).rename(
        columns={"date": "Date", "contribution": "Contribution", "uncertainty": "Uncertainty"}
    )
    df_LASSO = get_df_full_query(query_LASSO).rename(
        columns={"date": "Date", "contribution": "Contribution", "uncertainty": "Uncertainty"}
    )
    df_ODR = get_df_full_query(query_ODR).rename(
        columns={"date": "Date", "contribution": "Contribution", "uncertainty": "Uncertainty"}
    )
    df_BCff = get_coloc_data(start_date, end_date, 'BCff')
    df_NOx = get_coloc_data(start_date, end_date, 'NOx')
    return dict(
        data = [
            dict(
                x = df_ODR["Date"],
                y = df_ODR["Contribution"]+df_ODR["Uncertainty"],
                line = dict(
                    color = "#b1c8d3",
                    dash = "1px",
                    width = 1,
                ),
                name = "ODR upper bound",
                mode = "line",), 
            dict(
                x = df_ODR["Date"],
                y = df_ODR["Contribution"]-df_ODR["Uncertainty"],
                line = dict(
                    color = "#b1c8d3",
                    dash = "1px",
                    width = 1,
                ),
                name = "ODR lower bound",
                fill = 'tonexty',
                mode = "line",),
            dict(
                x = df_ODR["Date"],
                y = df_ODR["Contribution"],
                line = dict(
                    color = "#3f4e59",
                    dash = "1px",
                    width = 1,
                ),
                name = "ODR Contribution",
                mode = "line",),
            dict(
                x = df_PMF["Date"],
                y = df_PMF["Contribution"],
                line = dict(
                    color = "#c71585",
                    dash = "1px",
                    width = 1,
                ),
                name = "PMF Contribution",
                mode = "line",),
            dict(
                x = df_LASSO["Date"],
                y = df_LASSO["Contribution"],
                line = dict(
                    color = "#0d98ba",
                    dash = "1px",
                    width = 1,
                ),
                name = "Lasso Contribution",
                mode = "line",),
            dict(
                x = df_BCff["Date"],
                y = df_BCff["Value"],
                line = dict(
                    # color = "#0d98ba",
                    dash = "1px",
                    width = 1,
                ),
                name = "BCff",
                mode = "line",
                visible='legendonly',),
            dict(
                x = df_NOx["Date"],
                y = df_NOx["Value"],
                line = dict(
                    # color = "#0d98ba",
                    dash = "1px",
                    width = 1,
                ),
                name = "NOx",
                mode = "line",
                visible='legendonly',),
        ],
        layout = dict(
            margin = dict(t = 0, b = 0, r = 40, l = 40),
            template = "plotly_white", 
            height = 300,
            xaxis_tickformat="%d %B (%a)\n%H:%M",
            legend = dict(
                orientation = "h",
                x = 0.5, xanchor = "center",
            ),
            yaxis = dict(
                exponentformat = "SI",
                automargin = True
            ),
        ),
    )


def get_profile_evolution_BBOA(start_date, end_date):
    if start_date==None or end_date==None:
        fig = go.Figure()
        fig.update_layout(
            margin=dict(t=0, b=0, r=40, l=40),
            height=300
        )
        return(fig)

    query_PMF=f"""SELECT date, contribution, uncertainty FROM public.regressor_results WHERE date < '{end_date}' 
              AND date >= '{start_date}' AND model = 'PMF' AND profile = 'BBOA' ORDER BY date"""
    query_LASSO=f"""SELECT date, contribution, uncertainty FROM public.regressor_results WHERE date < '{end_date}' 
              AND date >= '{start_date}' AND model = 'LASSO' AND profile = 'BBOA' ORDER BY date"""
    query_ODR=f"""SELECT date, contribution, uncertainty FROM public.regressor_results WHERE date < '{end_date}' 
              AND date >= '{start_date}' AND model = 'ODR' AND profile = 'BBOA' ORDER BY date"""

    df_PMF = get_df_full_query(query_PMF).rename(
        columns={"date": "Date", "contribution": "Contribution", "uncertainty": "Uncertainty"}
    )
    df_LASSO = get_df_full_query(query_LASSO).rename(
        columns={"date": "Date", "contribution": "Contribution", "uncertainty": "Uncertainty"}
    )
    df_ODR = get_df_full_query(query_ODR).rename(
        columns={"date": "Date", "contribution": "Contribution", "uncertainty": "Uncertainty"}
    )
    df_BCwb = get_coloc_data(start_date, end_date, 'BCwb')
    df_CO = get_coloc_data(start_date, end_date, 'CO')
    return dict(
        data = [
            dict(
                x = df_ODR["Date"],
                y = df_ODR["Contribution"]+df_ODR["Uncertainty"],
                line = dict(
                    color = "#b1c8d3",
                    dash = "1px",
                    width = 1,
                ),
                name = "ODR upper bound",
                mode = "line",), 
            dict(
                x = df_ODR["Date"],
                y = df_ODR["Contribution"]-df_ODR["Uncertainty"],
                line = dict(
                    color = "#b1c8d3",
                    dash = "1px",
                    width = 1,
                ),
                name = "ODR lower bound",
                fill = 'tonexty',
                mode = "line",),
            dict(
                x = df_ODR["Date"],
                y = df_ODR["Contribution"],
                line = dict(
                    color = "#3f4e59",
                    dash = "1px",
                    width = 1,
                ),
                name = "ODR Contribution",
                mode = "line",),
            dict(
                x = df_PMF["Date"],
                y = df_PMF["Contribution"],
                line = dict(
                    color = "#c71585",
                    dash = "1px",
                    width = 1,
                ),
                name = "PMF Contribution",
                mode = "line",),
            dict(
                x = df_LASSO["Date"],
                y = df_LASSO["Contribution"],
                line = dict(
                    color = "#0d98ba",
                    dash = "1px",
                    width = 1,
                ),
                name = "Lasso Contribution",
                mode = "line",),
            dict(
                x = df_BCwb["Date"],
                y = df_BCwb["Value"],
                line = dict(
                    # color = "#0d98ba",
                    dash = "1px",
                    width = 1,
                ),
                name = "BCwb",
                mode = "line",
                visible='legendonly',),
            dict(
                x = df_CO["Date"],
                y = df_CO["Value"],
                line = dict(
                    # color = "#0d98ba",
                    dash = "1px",
                    width = 1,
                ),
                name = "CO",
                mode = "line",
                visible='legendonly',),
        ],
        layout = dict(
            margin = dict(t = 0, b = 0, r = 40, l = 40),
            template = "plotly_white", 
            height = 300,
            xaxis_tickformat="%d %B (%a)\n%H:%M",
            legend = dict(
                orientation = "h",
                x = 0.5, xanchor = "center",
            ),
            yaxis = dict(
                exponentformat = "SI",
                automargin = True
            ),
        ),
    )



def get_error_evolution_model(start_date, end_date, error_type, model, mass):
    if start_date==None or end_date==None or error_type==None or model==None:
        fig = go.Figure()
        fig.update_layout(
            margin=dict(t=0, b=0, r=40, l=40),
            height=300
        )
        return(fig)

    query=f"""SELECT date, error, error_relative FROM public.model_error WHERE date < '{end_date}' 
              AND date >= '{start_date}' AND model = '{model}' and error_type = '{error_type}' and mass = {mass} ORDER BY date"""

    df = get_df_full_query(query).rename(
        columns={"date": "Date", "error": "Error", "error_relative": "Relative error"}
    )

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=df["Date"],
            y=df["Error"],
            name="Error",
            line = dict(
                color = "#3f4e59",
                dash = "1px",
                width = 1,
            ),
        )
    )
    fig.update_layout(
        margin=dict(t=0, b=0, r=40, l=40),
        height=300,
        xaxis_showticklabels=True)
    return fig



def get_error_evolution(start_date, end_date, error_type, mass):
    if start_date==None or end_date==None or error_type==None or mass==None:
        fig = go.Figure()
        fig.update_layout(
            margin=dict(t=0, b=0, r=40, l=40),
            height=300
        )
        return(fig)

    query_PMF=f"""SELECT date, error, error_relative FROM public.model_error WHERE date < '{end_date}' 
              AND date >= '{start_date}' AND model = 'PMF' and error_type = '{error_type}' and mass = {mass} ORDER BY date"""
    query_LASSO=f"""SELECT date, error, error_relative FROM public.model_error WHERE date < '{end_date}' 
              AND date >= '{start_date}' AND model = 'LASSO' and error_type = '{error_type}' and mass = {mass} ORDER BY date"""
    query_ODR=f"""SELECT date, error, error_relative FROM public.model_error WHERE date < '{end_date}' 
              AND date >= '{start_date}' AND model = 'ODR' and error_type = '{error_type}' and mass = {mass} ORDER BY date"""

    df_PMF = get_df_full_query(query_PMF).rename(
        columns={"date": "Date", "error": "Error", "error_relative": "Relative error"}
    )
    df_LASSO = get_df_full_query(query_LASSO).rename(
        columns={"date": "Date", "error": "Error", "error_relative": "Relative error"}
    )
    df_ODR = get_df_full_query(query_ODR).rename(
        columns={"date": "Date", "error": "Error", "error_relative": "Relative error"}
    )

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=df_ODR["Date"],
            y=df_ODR["Error"],
            name="ODR error",
            line = dict(
                color = "#3f4e59",
                dash = "1px",
                width = 1,
            ),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=df_LASSO["Date"],
            y=df_LASSO["Error"],
            name="Lasso error",
            line = dict(
                color = "#0d98ba",
                dash = "1px",
                width = 1,
            ),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=df_PMF["Date"],
            y=df_PMF["Error"],
            name="PMF error",
            line = dict(
                color = "#c71585",
                dash = "1px",
                width = 1,
            ),
        )
    )
    fig.update_layout(
        margin=dict(t=0, b=0, r=40, l=40),
        height=300,
        xaxis_showticklabels=True)
    return fig



def get_error_by_mass_evolution(start_date, end_date, error_type, model, mass):
    if start_date==None or end_date==None or error_type==None or model==None:
        fig = go.Figure()
        fig.update_layout(
            margin=dict(t=0, b=0, r=40, l=40),
            height=300
        )
        return(fig)

    query=f"""SELECT date, error, error_relative FROM public.model_error WHERE date < '{end_date}' 
              AND date >= '{start_date}' AND model = '{model}' and error_type = '{error_type}' and mass = {mass} ORDER BY date"""

    df = get_df_full_query(query).rename(
        columns={"date": "Date", "error": "Error", "error_relative": "Relative error"}
    )

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=df["Date"],
            y=df["Error"],
            name="Error",
            line = dict(
                color = "#3f4e59",
                dash = "1px",
                width = 1,
            ),
        )
    )
    fig.update_layout(
        margin=dict(t=0, b=0, r=40, l=40),
        height=300,
        xaxis_showticklabels=True)
    return fig



def get_signal_reconst_model(date, model):
    if date==None or model==None:
        fig = go.Figure()
        fig.update_layout(
            margin=dict(t=0, b=0, r=40, l=40),
            height=300
        )
        return(fig)

    query=f"""SELECT mass, value FROM public.signal_reconst WHERE date = '{date}' AND model = '{model}' ORDER BY 1"""

    df_signal_recons = get_df_full_query(query).rename(
        columns={"mass": "Mass", "value": "Value"}
    )

    query=f"""SELECT mass, value FROM public.data_receptor WHERE date = '{date}' ORDER BY 1"""

    df_signal_receptor = get_df_full_query(query).rename(
        columns={"mass": "Mass", "value": "Value"}
    )

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=df_signal_receptor["Mass"],
            y=df_signal_receptor["Value"],
            name="Receptor signal",
        )
    )
    fig.add_trace(
        go.Bar(
            x=df_signal_recons["Mass"],
            y=df_signal_recons["Value"],
            name="Reconstituted signal",
        )
    )
    fig.update_layout(
        margin=dict(t=0, b=0, r=40, l=40),
        height=300,
        xaxis_showticklabels=True)
    return fig



def get_signal_reconst_avg_model(start_date, end_date):
    if start_date==None or end_date==None:
        fig = go.Figure()
        fig.update_layout(
            margin=dict(t=0, b=0, r=40, l=40),
            height=300
        )
        return(fig)
    if start_date>end_date:
        fig = go.Figure()
        fig.update_layout(
            margin=dict(t=0, b=0, r=40, l=40),
            height=300
        )
        return(fig)

    query_PMF=f"""SELECT mass, avg(value), stddev_samp(value) FROM public.signal_reconst WHERE date <= '{end_date}' 
              AND date >= '{start_date}' AND model = 'PMF' GROUP BY 1 ORDER BY 1"""
    query_ODR=f"""SELECT mass, avg(value), stddev_samp(value) FROM public.signal_reconst WHERE date <= '{end_date}' 
              AND date >= '{start_date}' AND model = 'ODR' GROUP BY 1 ORDER BY 1"""
    query_LASSO=f"""SELECT mass, avg(value), stddev_samp(value) FROM public.signal_reconst WHERE date <= '{end_date}' 
              AND date >= '{start_date}' AND model = 'LASSO' GROUP BY 1 ORDER BY 1"""

    df_signal_recons_PMF = get_df_full_query(query_PMF).rename(
        columns={"mass": "Mass", "avg": "Average", "stddev_samp":"Standard deviation"}
    )
    df_signal_recons_ODR = get_df_full_query(query_ODR).rename(
        columns={"mass": "Mass", "avg": "Average", "stddev_samp":"Standard deviation"}
    )
    df_signal_recons_LASSO = get_df_full_query(query_LASSO).rename(
        columns={"mass": "Mass", "avg": "Average", "stddev_samp":"Standard deviation"}
    )

    query=f"""SELECT mass, avg(value), stddev_samp(value) FROM public.data_receptor WHERE date <= '{end_date}' 
              AND date >= '{start_date}' GROUP BY 1 ORDER BY 1"""

    df_signal_receptor = get_df_full_query(query).rename(
        columns={"mass": "Mass", "avg": "Average", "stddev_samp":"Standard deviation"}
    )

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=df_signal_receptor["Mass"],
            y=df_signal_receptor["Average"],
            # error_y=dict(
            # type='data', # value of error bar given in data coordinates
            # array=df_signal_receptor["Standard deviation"],
            # visible=True),
            name="Receptor signal",
        )
    )
    fig.add_trace(
        go.Bar(
            x=df_signal_recons_PMF["Mass"],
            y=df_signal_recons_PMF["Average"],
            # error_y=dict(
            # type='data', # value of error bar given in data coordinates
            # array=df_signal_recons_PMF["Standard deviation"],
            # visible=True),
            name="PMF signal",
        )
    )
    fig.add_trace(
        go.Bar(
            x=df_signal_recons_ODR["Mass"],
            y=df_signal_recons_ODR["Average"],
            # error_y=dict(
            # type='data', # value of error bar given in data coordinates
            # array=df_signal_recons_ODR["Standard deviation"],
            # visible=True),
            name="ODR signal",
        )
    )
    fig.add_trace(
        go.Bar(
            x=df_signal_recons_LASSO["Mass"],
            y=df_signal_recons_LASSO["Average"],
            # error_y=dict(
            # type='data', # value of error bar given in data coordinates
            # array=df_signal_recons_LASSO["Standard deviation"],
            # visible=True),
            name="LASSO signal",
        )
    )
    fig.update_layout(
        margin=dict(t=0, b=0, r=40, l=40),
        height=300,
        xaxis_showticklabels=True)
    return fig


def get_signal_reconst(date):
    if date==None:
        fig = go.Figure()
        fig.update_layout(
            margin=dict(t=0, b=0, r=40, l=40),
            height=300
        )
        return(fig)

    query_PMF=f"""SELECT mass, value FROM public.signal_reconst WHERE date = '{date}' AND model = 'PMF' ORDER BY 1"""
    query_ODR=f"""SELECT mass, value FROM public.signal_reconst WHERE date = '{date}' AND model = 'ODR' ORDER BY 1"""
    query_LASSO=f"""SELECT mass, value FROM public.signal_reconst WHERE date = '{date}' AND model = 'LASSO' ORDER BY 1"""

    df_signal_recons_PMF = get_df_full_query(query_PMF).rename(
        columns={"mass": "Mass", "value": "Value"}
    )
    df_signal_recons_ODR = get_df_full_query(query_ODR).rename(
        columns={"mass": "Mass", "value": "Value"}
    )
    df_signal_recons_LASSO = get_df_full_query(query_LASSO).rename(
        columns={"mass": "Mass", "value": "Value"}
    )

    query=f"""SELECT mass, value FROM public.data_receptor WHERE date = '{date}' ORDER BY 1"""

    df_signal_receptor = get_df_full_query(query).rename(
        columns={"mass": "Mass", "value": "Value"}
    )

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=df_signal_receptor["Mass"],
            y=df_signal_receptor["Value"],
            name="Receptor signal",
        )
    )
    fig.add_trace(
        go.Bar(
            x=df_signal_recons_PMF["Mass"],
            y=df_signal_recons_PMF["Value"],
            name="PMF reconstituted signal",
        )
    )
    fig.add_trace(
        go.Bar(
            x=df_signal_recons_LASSO["Mass"],
            y=df_signal_recons_LASSO["Value"],
            name="Lasso reconstituted signal",
        )
    )
    fig.add_trace(
        go.Bar(
            x=df_signal_recons_ODR["Mass"],
            y=df_signal_recons_ODR["Value"],
            name="ODR reconstituted signal",
        )
    )
    fig.update_layout(
        margin=dict(t=0, b=0, r=40, l=40),
        height=300,
        xaxis_showticklabels=True)
    return fig



def get_pie_profile_model(start_date, end_date, model):
    if start_date==None or end_date==None:
        fig = go.Figure()
        fig.update_layout(
            margin=dict(t=0, b=0, r=40, l=40),
            height=300
        )
        return(fig)

    query=f"""SELECT profile, avg(contribution) FROM public.regressor_results WHERE date <= '{end_date}' 
              AND date >= '{start_date}' AND model = '{model}' GROUP BY 1 ORDER BY profile"""

    df = get_df_full_query(query).rename(
        columns={"profile": "Profile", "avg": "Contribution"}
    )
    colors = ['gold', 'mediumturquoise', 'darkorange', 'lightgreen']

    fig = go.Figure()
    fig.add_trace(
        go.Pie(
            labels=df["Profile"].values,
            values=df["Contribution"].values,
            sort=False
        )
    )
    fig.update_traces(
        marker=dict(colors=colors))
    fig.update_layout(
        margin=dict(t=0, b=0, r=40, l=40),
        height=300)
    return(fig)


def get_pie_profile_evolution_model(start_date, end_date, model):
    if date==None or model==None:
        fig = go.Figure()
        fig.update_layout(
            margin=dict(t=0, b=0, r=40, l=40),
            height=300
        )
        return(fig)

    query=f"""SELECT date, profile, contribution FROM public.regressor_results WHERE date <= '{end_date}' 
              AND date >= '{start_date}' AND model = '{model}' ORDER BY date, profile"""

    df = get_df_full_query(query)
    df['contr_abs'] = df['contribution'].abs()
    df['contr_sum'] = df.groupby('date').contr_abs.transform(np.sum)
    df['perc'] = df['contr_abs']/df['contr_sum']*100
    df['sign'] = np.sign(df['contribution'])
    df['perc'] = df['perc']*df['sign']



    fig = go.Figure()
    fig.add_trace(go.Bar(x=df[df['profile']=='HOA']['date'], y=df[df['profile']=='HOA']['perc'], name='HOA'))
    fig.add_trace(go.Bar(x=df[df['profile']=='BBOA']['date'], y=df[df['profile']=='BBOA']['perc'], name='BBOA'))
    fig.add_trace(go.Bar(x=df[df['profile']=='LO-OOA']['date'], y=df[df['profile']=='LO-OOA']['perc'], name='LO-OOA'))
    fig.add_trace(go.Bar(x=df[df['profile']=='MO-OOA']['date'], y=df[df['profile']=='MO-OOA']['perc'], name='MO-OOA'))
    fig.update_layout(
        margin=dict(t=0, b=0, r=40, l=40),
        height=300,
        barmode='relative', 
        title_text='Relative Barmode',
        xaxis_showticklabels=True
        )   
    return(fig)




def get_daily_contribution_profile_model(start_date, end_date, profile, model):
    if start_date==None or end_date==None or profile==None or model==None:
        fig = go.Figure()
        fig.update_layout(
            margin=dict(t=0, b=0, r=40, l=40),
            height=300
        )
        return(fig)

    query=f"""SELECT date, contribution FROM public.regressor_results WHERE date < '{end_date}' 
              AND date >= '{start_date}' AND model = '{model}' AND profile = '{profile}' ORDER BY date"""

    df = get_df_full_query(query).rename(
        columns={"date": "Date", "contribution": "Contribution", "uncertainty": "Uncertainty"}
    )
    df['time'] = df['Date'].dt.strftime('%H')

    fig = go.Figure()
    fig.add_trace(
        go.Box(
            x=df["time"].values,
            y=df["Contribution"].values,
        )
    )
    fig.update_layout(
        margin=dict(t=0, b=0, r=40, l=40),
        height=300,
        xaxis_title='Time',
        yaxis_title='Contribution'
        )
    return(fig)



def get_daily_contribution_profile_avg_std_model(start_date, end_date, profile, model):
    if start_date==None or end_date==None or profile==None or model==None:
        fig = go.Figure()
        fig.update_layout(
            margin=dict(t=0, b=0, r=40, l=40),
            height=300
        )
        return(fig)

    query=f"""SELECT date, contribution FROM public.regressor_results WHERE date < '{end_date}' 
              AND date >= '{start_date}' AND model = '{model}' AND profile = '{profile}' ORDER BY date"""

    df = get_df_full_query(query).rename(
        columns={"date": "Date", "contribution": "Contribution", "uncertainty": "Uncertainty"}
    )
    df['time'] = df['Date'].dt.strftime('%H')
    df_group = df.groupby(['time'], as_index=False).agg({'Contribution':['mean', 'std']})

    x = df_group['time'].values.tolist()
    y = df_group['Contribution']['mean'].values.tolist()
    y_upper = (df_group['Contribution']['mean']+df_group['Contribution']['std']).values.tolist()
    y_lower = (df_group['Contribution']['mean']-df_group['Contribution']['std']).values.tolist()

    fig = go.Figure([
        go.Scatter(
            x=x,
            y=y,
            line=dict(color='rgb(0,100,80)'),
            name="Moyenne "+profile,
            mode='lines'
        ),
        go.Scatter(
            x=x+x[::-1], # x, then x reversed
            y=y_upper+y_lower[::-1], # upper, then lower reversed
            fill='toself',
            fillcolor='rgba(0,100,80,0.2)',
            line=dict(color='rgba(255,255,255,0)'),
            hoverinfo="skip",
            showlegend=False
        )
    ])
    fig.update_layout(
        margin=dict(t=0, b=0, r=40, l=40),
        height=300,
        xaxis_title='Time',
        yaxis_title='Contribution'
        )
    return(fig)


def get_coloc_data_evolution(start_date, end_date, coloc):
    if start_date==None or end_date==None or coloc==None:
        fig = go.Figure()
        fig.update_layout(
            margin=dict(t=0, b=0, r=40, l=40),
            height=300
        )
        return(fig)

    query=f"""SELECT date, value FROM public.data_receptor_coloc WHERE date < '{end_date}' 
              AND date >= '{start_date}' and coloc = '{coloc}' ORDER BY 1"""

    df = get_df_full_query(query).rename(
        columns={"date": "Date", "value": "Value"}
    )
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=df["Date"],
            y=df["Value"],
            line = dict(
                color = "#3f4e59",
                dash = "1px",
                width = 1,
            ),
        )
    )
    fig.update_layout(
        margin=dict(t=0, b=0, r=40, l=40),
        height=300,
        xaxis_title='Date',
        yaxis_title='Concentration'
        )
    return(fig)


def get_error_table(start_date, end_date, model, error_type):
    if start_date==None or end_date==None or model==None or error_type==None:
        return([{"Date" : None, "Mass" : None, 'Error' :None}])

    query=f"""SELECT date, mass, error FROM public.model_error WHERE date < '{end_date}' 
              AND date >= '{start_date}' and model = '{model}' AND mass != 0 and error_type = '{error_type}' 
              ORDER BY 3 DESC LIMIT 100"""

    df = get_df_full_query(query)

    dict_table = [{"Date":i[0], "Mass":i[1], 'Error':i[2]} for i in df.values]
    return(dict_table)



def get_correlation(start_date, end_date, profile, model1, model2):
    if start_date==None or end_date==None or model1==None or model2==None or profile==None:
        fig = go.Figure()
        fig.update_layout(
            margin=dict(t=0, b=0, r=40, l=40),
            height=300
        )
        return(fig)


    if model1 in ['BCff', 'NOx', 'BCwb', 'CO']:
        df_model1 = get_coloc_data(start_date, end_date, model1).rename(columns={"Value":"Contribution1"})


    if model2 in ['BCff', 'NOx', 'BCwb', 'CO']:
        df_model2 = get_coloc_data(start_date, end_date, model2).rename(columns={"Value":"Contribution2"})


    if model1 in ['PMF', 'ODR', 'LASSO']:
        query_model1=f"""SELECT date, contribution FROM public.regressor_results WHERE date < '{end_date}' 
                         AND date >= '{start_date}' AND model = '{model1}' AND profile = '{profile}' ORDER BY date""" 
        df_model1=get_df_full_query(query_model1).rename(columns={"date": "Date", "contribution": "Contribution1"})


    if model2 in ['PMF', 'ODR', 'LASSO']:
        query_model2=f"""SELECT date, contribution FROM public.regressor_results WHERE date < '{end_date}' 
                         AND date >= '{start_date}' AND model = '{model2}' AND profile = '{profile}' ORDER BY date""" 
        df_model2=get_df_full_query(query_model2).rename(columns={"date": "Date", "contribution": "Contribution2"})

    merged_inner = pd.merge(left=df_model1, right=df_model2, left_on='Date', right_on='Date')


    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=merged_inner["Contribution1"],
            y=merged_inner["Contribution2"],
            mode='markers'
        )
    )
    fig.update_layout(
        margin=dict(t=0, b=0, r=40, l=40),
        height=300,
        xaxis_title=model1,
        yaxis_title=model2
        )
    return(fig)


    # return dict(
    #     data = [
    #         dict(
    #             x = merged_inner["Contribution1"],
    #             y = merged_inner["Contribution2"],
    #             line = dict(
    #                 color = "#c71585",
    #                 dash = "1px",
    #                 width = 1,
    #             ),
    #             # name = "PMF Contribution",
    #             mode = "markers",),
    #     ],
    #     layout = dict(
    #         margin = dict(t = 0, b = 0, r = 40, l = 40),
    #         template = "plotly_white", 
    #         height = 300,
    #         # xaxis_tickformat="%d %B (%a)\n%H:%M",
    #         legend = dict(
    #             orientation = "h",
    #             x = 0.5, xanchor = "center",
    #         ),
    #         yaxis = dict(
    #             exponentformat = "SI",
    #             automargin = True
    #         ),
    #         xaxis_title=model1,
    #         yaxis_title=model2,
    #     ),
    # )

