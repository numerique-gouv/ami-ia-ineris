import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import custom_components as cc
import dash_table as dtable
from datetime import datetime as dt
from datetime import date



MASSES = [13,15,16,17,18,24,25,26,27,29,30,31,37,38,41,42,43,44,45]+[i for i in range(48,101)]
TIMES = [' 0'+str(i)+':00:00' for i in range(10)] + [' '+str(i)+':00:00' for i in range(10,24)]
MODELS = ['PMF', 'LASSO', 'ODR']
MODELS_CORR = ['PMF', 'LASSO', 'ODR', 'BCff', 'NOx', 'BCwb', 'CO']


layout = html.Div(
    [
        html.H1('Chemical mass balance'),
        html.Div([
            dcc.DatePickerRange(
                id='my-date-picker-range',
                min_date_allowed=dt(2011, 1, 1),
                display_format='DD-MM-YYYY',
                # initial_visible_month=dt(2018, 1, 1),
                # start_date=dt(2018, 1, 1).date(),
                # end_date=dt(2018, 1, 31).date(),
                clearable=True,
                updatemode='bothdates'
            ),
            ],style={'width': '50%', 'display': 'inline-block'}),


        dbc.Row(
            [
                dbc.Col(
                    [
                    cc.ChartCard("alpha-evolution", "HOA"),
                ],width=6),
                dbc.Col(
                    [
                    cc.ChartCard("beta-evolution", "BBOA"),
                ],width=6),
            ]
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                        dcc.Dropdown(
                        id='model1',
                        options=[{'label':model, 'value':model} for model in MODELS_CORR],
                        value='PMF'
                        ),

                ],width=3),
                dbc.Col(
                    [
                        dcc.Dropdown(
                        id='model2',
                        options=[{'label':model, 'value':model} for model in MODELS_CORR],
                        value='LASSO'
                        ),

                ],width=3),
                dbc.Col(
                    [
                        dcc.Dropdown(
                        id='model3',
                        options=[{'label':model, 'value':model} for model in MODELS_CORR],
                        value='PMF'
                        ),

                ],width=3),
                dbc.Col(
                    [
                        dcc.Dropdown(
                        id='model4',
                        options=[{'label':model, 'value':model} for model in MODELS_CORR],
                        value='LASSO'
                        ),

                ],width=3),
            ]
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                    cc.ChartCard("correlation-HOA", "Correlation HOA"),
                ],width=6),
                dbc.Col(
                    [
                    cc.ChartCard("correlation-BBOA", "Correlation BBOA"),
                ],width=6),
            ]
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                    cc.ChartCard("gamma-evolution", "MO-OOA"),
                ],width=6),
                dbc.Col(
                    [
                    cc.ChartCard("theta-evolution", "LO-OOA"),
                ],width=6),
            ]
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                    cc.ChartCard("MAE-error", "MAE error"),
                ],width=6),
                dbc.Col(
                    [
                    cc.ChartCard("MSE-error", "MSE error"),
                ],width=6),
            ]
        ),


        html.Hr(),

        dbc.Row(
            [
                dbc.Col(
                    [
                        html.H4("PMF"),
                        html.Div([
                                    dtable.DataTable(id='PMF-mass-error', 
                                        columns = [{"id": 'Date', "name": 'Date'}, {"id": 'Mass', "name": 'Mass'}, {"id": 'Error', "name": 'Error'}],
                                        style_data={'whiteSpace': 'pre-line'}, 
                                        style_cell={'textAlign': 'left'},
                                        page_size=10,
                                        )
                                ])
                ],width=4),
                dbc.Col(
                    [
                        html.H4("LASSO"),
                        html.Div([
                                    dtable.DataTable(id='LASSO-mass-error', 
                                        columns = [{"id": 'Date', "name": 'Date'}, {"id": 'Mass', "name": 'Mass'}, {"id": 'Error', "name": 'Error'}],
                                        style_data={'whiteSpace': 'pre-line'}, 
                                        style_cell={'textAlign': 'left'},
                                        page_size=10,
                                        )
                                ])
                ],width=4),
                dbc.Col(
                    [
                        html.H4("ODR"),
                        html.Div([
                                    dtable.DataTable(id='ODR-mass-error', 
                                        columns = [{"id": 'Date', "name": 'Date'}, {"id": 'Mass', "name": 'Mass'}, {"id": 'Error', "name": 'Error'}],
                                        style_data={'whiteSpace': 'pre-line'}, 
                                        style_cell={'textAlign': 'left'},
                                        page_size=10,
                                        )
                                ])
                ],width=4),
            ]
        ),

        html.Hr(),

        dbc.Row(
            [
                dbc.Col(
                    [
                        html.P("Select mass"),
                        dcc.Dropdown(
                        id='mass1',
                        options=[{'label':mass, 'value':mass} for mass in MASSES],
                        value = 29
                        ),
                ],width=6),
                dbc.Col(
                    [
                        html.P("Select mass"),
                        dcc.Dropdown(
                        id='mass2',
                        options=[{'label':mass, 'value':mass} for mass in MASSES],
                        value = 44
                        ),
                ],width=6),
            ]
        ),



        dbc.Row(
            [
                dbc.Col(
                    [
                    cc.ChartCard("mass1-error", "Error by mass"),
                ],width=6),
                dbc.Col(
                    [
                    cc.ChartCard("mass2-error", "Error by mass"),
                ],width=6),
            ]
        ),


        html.Hr(),



        # dbc.Row(
        #     [
        #         dbc.Col(
        #             [
        #                 dcc.DatePickerSingle(
        #                     id='date-picker-start',
        #                     min_date_allowed=date(2011, 1, 1),
        #                     display_format='DD-MM-YYYY',
        #                     initial_visible_month=date(2018, 1, 1),
        #                     date=date(2018, 1, 6)
        #                 ),
        #         ],width=3),
        #         dbc.Col(
        #             [
        #                 dcc.Dropdown(
        #                     id='time-1',
        #                     options=[{'label':time, 'value':time} for time in TIMES],
        #                     value = ' 00:00:00'
        #                 ),
        #         ],width=3),
        #         dbc.Col(
        #             [
        #                 dcc.DatePickerSingle(
        #                     id='date-picker-end',
        #                     min_date_allowed=date(2011, 1, 1),
        #                     display_format='DD-MM-YYYY',
        #                     initial_visible_month=date(2018, 1, 1),
        #                     date=date(2018, 3, 26)
        #                 ),
        #         ],width=3),
        #         dbc.Col(
        #             [
        #                 dcc.Dropdown(
        #                     id='time-2',
        #                     options=[{'label':time, 'value':time} for time in TIMES],
        #                     value = ' 00:00:00'
        #                 ),
        #         ],width=3),
        #     ]
        # ),

        dbc.Row(
            [
                dbc.Col(
                    [
                    cc.ChartCard("signal-reconstitution-1", "Signal reconstituton average"),
                ],width=12),
            ]
        ),

        dbc.Row(
            [
                dbc.Col(
                    [
                    cc.ChartCard("pie-PMF", "PMF"),
                ],width=4),
                dbc.Col(
                    [
                    cc.ChartCard("pie-LASSO", "Lasso"),
                ],width=4),
                dbc.Col(
                    [
                    cc.ChartCard("pie-ODR", "ODR"),
                ],width=4),
            ]
        ),

        dbc.Row(
            [
                dbc.Col(
                    [
                        dcc.Dropdown(
                            id='model-dropdown-2',
                            options=[{'label':model, 'value':model} for model in MODELS],
                            value = 'PMF'
                        ),
                ],width=6),
            ]
        ),

        dbc.Row(
            [
                dbc.Col(
                    [
                    cc.ChartCard("stacked-bars", "Stacked bars contributions"),
                ],width=12),
            ]
        ),



        html.Hr(),



        dbc.Row(
            [
                # dbc.Col(
                #     [
                #         dcc.DatePickerRange(
                #             id='my-date-picker-range-1',
                #             min_date_allowed=date(2011, 1, 1),
                #             display_format='DD-MM-YYYY',
                #             initial_visible_month=date(2018, 1, 1),
                #             start_date=dt(2018, 1, 1).date(),
                #             end_date=dt(2018, 3, 26).date()
                #         ),
                # ],width=6),
                dbc.Col(
                    [
                        dcc.Dropdown(
                            id='model-dropdown',
                            options=[{'label':model, 'value':model} for model in MODELS],
                            value = 'PMF'
                        ),
                ],width=6),
            ]
        ),

        dbc.Row(
            [
                dbc.Col(
                    [
                    cc.ChartCard("alpha-evolution-1", "HOA"),
                ],width=6),
                dbc.Col(
                    [
                    cc.ChartCard("beta-evolution-1", "BBOA"),
                ],width=6),
            ]
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                    cc.ChartCard("gamma-evolution-1", "MO-OOA"),
                ],width=6),
                dbc.Col(
                    [
                    cc.ChartCard("theta-evolution-1", "LO-OOA"),
                ],width=6),
            ]
        ),



        html.Hr(),



        dbc.Row(
            [
                # dbc.Col(
                #     [
                #         dcc.DatePickerRange(
                #             id='my-date-picker-range-4',
                #             min_date_allowed=date(2011, 1, 1),
                #             display_format='DD-MM-YYYY',
                #             initial_visible_month=date(2018, 1, 1),
                #             start_date=dt(2018, 1, 1).date(),
                #             end_date=dt(2018, 3, 26).date()
                #         ),
                # ],width=6),
                dbc.Col(
                    [
                        dcc.Dropdown(
                            id='model-dropdown-3',
                            options=[{'label':model, 'value':model} for model in MODELS],
                            value = 'PMF'
                        ),
                ],width=6),
            ]
        ),

        dbc.Row(
            [
                dbc.Col(
                    [
                    cc.ChartCard("alpha-evolution-2", "HOA"),
                ],width=6),
                dbc.Col(
                    [
                    cc.ChartCard("beta-evolution-2", "BBOA"),
                ],width=6),
            ]
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                    cc.ChartCard("gamma-evolution-2", "MO-OOA"),
                ],width=6),
                dbc.Col(
                    [
                    cc.ChartCard("theta-evolution-2", "LO-OOA"),
                ],width=6),
            ]
        ),



        html.Hr(),



        # dbc.Row(
        #     [
        #         dbc.Col(
        #             [
        #                 dcc.DatePickerSingle(
        #                     id='date-picker-start',
        #                     min_date_allowed=date(2011, 1, 1),
        #                     display_format='DD-MM-YYYY',
        #                     initial_visible_month=date(2018, 1, 1),
        #                     date=date(2018, 1, 6)
        #                 ),
        #         ],width=3),
        #         dbc.Col(
        #             [
        #                 dcc.Dropdown(
        #                     id='time-1',
        #                     options=[{'label':time, 'value':time} for time in TIMES],
        #                     value = ' 00:00:00'
        #                 ),
        #         ],width=3),
        #         dbc.Col(
        #             [
        #                 dcc.DatePickerSingle(
        #                     id='date-picker-end',
        #                     min_date_allowed=date(2011, 1, 1),
        #                     display_format='DD-MM-YYYY',
        #                     initial_visible_month=date(2018, 1, 1),
        #                     date=date(2018, 3, 26)
        #                 ),
        #         ],width=3),
        #         dbc.Col(
        #             [
        #                 dcc.Dropdown(
        #                     id='time-2',
        #                     options=[{'label':time, 'value':time} for time in TIMES],
        #                     value = ' 00:00:00'
        #                 ),
        #         ],width=3),
        #         # dbc.Col(
        #         #     [
        #         #         dcc.DatePickerRange(
        #         #             id='my-date-picker-range-2',
        #         #             min_date_allowed=date(2011, 1, 1),
        #         #             display_format='DD-MM-YYYY',
        #         #             initial_visible_month=date(2018, 1, 1),
        #         #             start_date=dt(2018, 1, 1).date(),
        #         #             end_date=dt(2018, 3, 26).date()
        #         #         ),
        #         # ],width=6),
        #         # dbc.Col(
        #         #     [
        #         #         dcc.Dropdown(
        #         #             id='model-dropdown-1',
        #         #             options=[{'label':model, 'value':model} for model in MODELS],
        #         #             value = 'PMF'
        #         #         ),
        #         # ],width=6),
        #     ]
        # ),

        # dbc.Row(
        #     [
        #         dbc.Col(
        #             [
        #             cc.ChartCard("signal-reconstitution-1", "Signal reconstituton average"),
        #         ],width=12),
        #     ]
        # ),




    ])
