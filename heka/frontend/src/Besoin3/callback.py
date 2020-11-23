import dash
from dash.dependencies import Input, Output, State
import plotly.graph_objects as go
import re
from datetime import date
from Besoin3.helpers import *


def register_callbacks(app):

    @app.callback(
        Output('correlation-HOA', 'figure'),
        [Input('my-date-picker-range', 'start_date'),
        Input('my-date-picker-range', 'end_date'),
        Input('model1', 'value'),
        Input('model2', 'value')])
    def update_output(start_date, end_date, model1, model2):
        if start_date==None or end_date==None or model1==None or model2==None:
            fig = go.Figure()
            fig.update_layout(
                margin=dict(t=0, b=0, r=40, l=40),
                height=300
            )
            return(fig)
        start_date = re.split('T| ', start_date)[0] 
        end_date = re.split('T| ', end_date)[0]
        fig=get_correlation(start_date, end_date, 'HOA', model1, model2)
        return(fig)


    @app.callback(
        Output('correlation-BBOA', 'figure'),
        [Input('my-date-picker-range', 'start_date'),
        Input('my-date-picker-range', 'end_date'),
        Input('model3', 'value'),
        Input('model4', 'value')])
    def update_output(start_date, end_date, model1, model2):
        if start_date==None or end_date==None or model1==None or model2==None:
            fig = go.Figure()
            fig.update_layout(
                margin=dict(t=0, b=0, r=40, l=40),
                height=300
            )
            return(fig)
        start_date = re.split('T| ', start_date)[0] 
        end_date = re.split('T| ', end_date)[0]
        fig=get_correlation(start_date, end_date, 'BBOA', model1, model2)
        return(fig)

    @app.callback(
        [Output('alpha-evolution', 'figure'),
        Output('beta-evolution', 'figure'),
        Output('gamma-evolution', 'figure'),
        Output('theta-evolution', 'figure'),
        Output('MAE-error', 'figure'),
        Output('MSE-error', 'figure'),
        Output('PMF-mass-error', 'data'),
        Output('LASSO-mass-error', 'data'),
        Output('ODR-mass-error', 'data')],
        [Input('my-date-picker-range', 'start_date'),
        Input('my-date-picker-range', 'end_date')])
    def update_output(start_date, end_date):
        if start_date==None or end_date==None:
            fig = go.Figure()
            fig.update_layout(
                margin=dict(t=0, b=0, r=40, l=40),
                height=300
            )
            return(fig,fig,fig,fig,fig,fig,fig,fig,fig)
        start_date = re.split('T| ', start_date)[0] 
        end_date = re.split('T| ', end_date)[0]
        fig_HOA=get_profile_evolution_HOA(start_date, end_date)
        fig_BBOA=get_profile_evolution_BBOA(start_date, end_date)
        fig_LOOA=get_profile_evolution(start_date, end_date, 'MO-OOA')
        fig_MOOA=get_profile_evolution(start_date, end_date, 'LO-OOA')
        fig_MAE=get_error_evolution(start_date, end_date, 'MAE', 0)
        fig_MSE=get_error_evolution(start_date, end_date, 'MSE', 0)
        table_PMF=get_error_table(start_date, end_date, 'PMF', 'MAE')
        table_LASSO=get_error_table(start_date, end_date, 'LASSO', 'MAE')
        table_ODR=get_error_table(start_date, end_date, 'ODR', 'MAE')

        return(fig_HOA,fig_BBOA,fig_LOOA,fig_MOOA,fig_MAE,fig_MSE,table_PMF,table_LASSO,table_ODR)
        # return get_profile_evolution_HOA(start_date, end_date)


    # @app.callback(
    #      Output('beta-evolution', 'figure'),
    #     [Input('my-date-picker-range', 'start_date'),
    #     Input('my-date-picker-range', 'end_date')])
    # def update_output(start_date, end_date):
    #     start_date = re.split('T| ', start_date)[0] 
    #     end_date = re.split('T| ', end_date)[0]
    #     return get_profile_evolution_BBOA(start_date, end_date)



    # @app.callback(
    #      Output('gamma-evolution', 'figure'),
    #     [Input('my-date-picker-range', 'start_date'),
    #     Input('my-date-picker-range', 'end_date')])
    # def update_output(start_date, end_date):
    #     start_date = re.split('T| ', start_date)[0] 
    #     end_date = re.split('T| ', end_date)[0]
    #     return get_profile_evolution(start_date, end_date, 'MO-OOA')



    # @app.callback(
    #      Output('theta-evolution', 'figure'),
    #     [Input('my-date-picker-range', 'start_date'),
    #     Input('my-date-picker-range', 'end_date')])
    # def update_output(start_date, end_date):
    #     start_date = re.split('T| ', start_date)[0] 
    #     end_date = re.split('T| ', end_date)[0]
    #     return get_profile_evolution(start_date, end_date, 'LO-OOA')


    # @app.callback(
    #      Output('MAE-error', 'figure'),
    #     [Input('my-date-picker-range', 'start_date'),
    #     Input('my-date-picker-range', 'end_date')])
    # def update_output(start_date, end_date):
    #     start_date = re.split('T| ', start_date)[0] 
    #     end_date = re.split('T| ', end_date)[0]
    #     return get_error_evolution(start_date, end_date, 'MAE', 0)


    # @app.callback(
    #      Output('MSE-error', 'figure'),
    #     [Input('my-date-picker-range', 'start_date'),
    #     Input('my-date-picker-range', 'end_date')])
    # def update_output(start_date, end_date):
    #     start_date = re.split('T| ', start_date)[0] 
    #     end_date = re.split('T| ', end_date)[0]
    #     return get_error_evolution(start_date, end_date, 'MSE', 0)


    # @app.callback(
    #      Output('PMF-mass-error', 'data'),
    #     [Input('my-date-picker-range', 'start_date'),
    #     Input('my-date-picker-range', 'end_date')])
    # def update_output(start_date, end_date):
    #     start_date = re.split('T| ', start_date)[0] 
    #     end_date = re.split('T| ', end_date)[0]
    #     return get_error_table(start_date, end_date, 'PMF', 'MAE')

    # @app.callback(
    #      Output('LASSO-mass-error', 'data'),
    #     [Input('my-date-picker-range', 'start_date'),
    #     Input('my-date-picker-range', 'end_date')])
    # def update_output(start_date, end_date):
    #     start_date = re.split('T| ', start_date)[0] 
    #     end_date = re.split('T| ', end_date)[0]
    #     return get_error_table(start_date, end_date, 'LASSO', 'MAE')

    # @app.callback(
    #      Output('ODR-mass-error', 'data'),
    #     [Input('my-date-picker-range', 'start_date'),
    #     Input('my-date-picker-range', 'end_date')])
    # def update_output(start_date, end_date):
    #     start_date = re.split('T| ', start_date)[0] 
    #     end_date = re.split('T| ', end_date)[0]
    #     return get_error_table(start_date, end_date, 'ODR', 'MAE')



    @app.callback(
         Output('mass1-error', 'figure'),
        [Input('my-date-picker-range', 'start_date'),
        Input('my-date-picker-range', 'end_date'),
        Input('mass1', 'value')])
    def update_output(start_date, end_date, mass):
        if start_date==None or end_date==None:
            fig = go.Figure()
            fig.update_layout(
                margin=dict(t=0, b=0, r=40, l=40),
                height=300
            )
            return(fig)
        start_date = re.split('T| ', start_date)[0] 
        end_date = re.split('T| ', end_date)[0]
        return get_error_evolution(start_date, end_date, 'MSE', mass)



    @app.callback(
         Output('mass2-error', 'figure'),
        [Input('my-date-picker-range', 'start_date'),
        Input('my-date-picker-range', 'end_date'),
        Input('mass2', 'value')])
    def update_output(start_date, end_date, mass):
        if start_date==None or end_date==None:
            fig = go.Figure()
            fig.update_layout(
                margin=dict(t=0, b=0, r=40, l=40),
                height=300
            )
            return(fig)
        start_date = re.split('T| ', start_date)[0] 
        end_date = re.split('T| ', end_date)[0]
        return get_error_evolution(start_date, end_date, 'MSE', mass)


    # @app.callback(
    #      Output('signal-reconstitution', 'figure'),
    #     [Input('my-date-picker-single', 'date'),
    #     Input('time-dropdown', 'value')])
    # def update_output(date_value, time):
    #     date_object = date.fromisoformat(date_value)
    #     date_string = date_object.strftime('%Y-%m-%d')
    #     return get_signal_reconst(date_string+time)

    @app.callback(
         Output('signal-reconstitution-1', 'figure'),
        [Input('my-date-picker-range', 'start_date'),
        Input('my-date-picker-range', 'end_date')])
    def update_output(start_date, end_date):
        if start_date==None or end_date==None:
            return(go.Figure())
        # start_date = date.fromisoformat(start_date)
        # start_date = start_date.strftime('%Y-%m-%d')
        # end_date = date.fromisoformat(end_date)
        # end_date = end_date.strftime('%Y-%m-%d')
        start_date = re.split('T| ', start_date)[0] 
        end_date = re.split('T| ', end_date)[0]
        return get_signal_reconst_avg_model(start_date, end_date)
        

    @app.callback(
        [Output('pie-PMF', 'figure'),
        Output('pie-LASSO', 'figure'),
        Output('pie-ODR', 'figure')],
        [Input('my-date-picker-range', 'start_date'),
        Input('my-date-picker-range', 'end_date')])
    def update_output(start_date, end_date):
        if start_date==None or end_date==None:
            return(go.Figure())
        # start_date = date.fromisoformat(start_date)
        # start_date = start_date.strftime('%Y-%m-%d')
        # end_date = date.fromisoformat(end_date)
        # end_date = end_date.strftime('%Y-%m-%d')
        start_date = re.split('T| ', start_date)[0] 
        end_date = re.split('T| ', end_date)[0]
        return(get_pie_profile_model(start_date, end_date, 'PMF'),get_pie_profile_model(start_date, end_date, 'LASSO'),get_pie_profile_model(start_date, end_date, 'ODR'))


    @app.callback(
         Output('stacked-bars', 'figure'),
        [Input('my-date-picker-range', 'start_date'),
        Input('my-date-picker-range', 'end_date'),
        Input('model-dropdown-2', 'value')])
    def update_output(start_date, end_date, model):
        if start_date==None or end_date==None:
            return(go.Figure())
        # start_date = date.fromisoformat(start_date)
        # start_date = start_date.strftime('%Y-%m-%d')
        # end_date = date.fromisoformat(end_date)
        # end_date = end_date.strftime('%Y-%m-%d')
        start_date = re.split('T| ', start_date)[0] 
        end_date = re.split('T| ', end_date)[0]
        return get_pie_profile_evolution_model(start_date, end_date, model)


    @app.callback(
         Output('alpha-evolution-1', 'figure'),
        [Input('my-date-picker-range', 'start_date'),
        Input('my-date-picker-range', 'end_date'),
        Input('model-dropdown', 'value')])
    def update_output(start_date, end_date, model):
        start_date = re.split('T| ', start_date)[0] 
        end_date = re.split('T| ', end_date)[0]
        return get_daily_contribution_profile_model(start_date, end_date, 'HOA', model)


    @app.callback(
         Output('beta-evolution-1', 'figure'),
        [Input('my-date-picker-range', 'start_date'),
        Input('my-date-picker-range', 'end_date'),
        Input('model-dropdown', 'value')])
    def update_output(start_date, end_date, model):
        start_date = re.split('T| ', start_date)[0] 
        end_date = re.split('T| ', end_date)[0]
        return get_daily_contribution_profile_model(start_date, end_date, 'BBOA', model)



    @app.callback(
         Output('gamma-evolution-1', 'figure'),
        [Input('my-date-picker-range', 'start_date'),
        Input('my-date-picker-range', 'end_date'),
        Input('model-dropdown', 'value')])
    def update_output(start_date, end_date, model):
        start_date = re.split('T| ', start_date)[0] 
        end_date = re.split('T| ', end_date)[0]
        return get_daily_contribution_profile_model(start_date, end_date, 'MO-OOA', model)


    @app.callback(
         Output('theta-evolution-1', 'figure'),
        [Input('my-date-picker-range', 'start_date'),
        Input('my-date-picker-range', 'end_date'),
        Input('model-dropdown', 'value')])
    def update_output(start_date, end_date, model):
        start_date = re.split('T| ', start_date)[0] 
        end_date = re.split('T| ', end_date)[0]
        return get_daily_contribution_profile_model(start_date, end_date, 'LO-OOA', model)



    @app.callback(
         Output('alpha-evolution-2', 'figure'),
        [Input('my-date-picker-range', 'start_date'),
        Input('my-date-picker-range', 'end_date'),
        Input('model-dropdown-3', 'value')])
    def update_output(start_date, end_date, model):
        start_date = re.split('T| ', start_date)[0] 
        end_date = re.split('T| ', end_date)[0]
        return get_daily_contribution_profile_avg_std_model(start_date, end_date, 'HOA', model)


    @app.callback(
         Output('beta-evolution-2', 'figure'),
        [Input('my-date-picker-range', 'start_date'),
        Input('my-date-picker-range', 'end_date'),
        Input('model-dropdown-3', 'value')])
    def update_output(start_date, end_date, model):
        start_date = re.split('T| ', start_date)[0] 
        end_date = re.split('T| ', end_date)[0]
        return get_daily_contribution_profile_avg_std_model(start_date, end_date, 'BBOA', model)


    @app.callback(
         Output('gamma-evolution-2', 'figure'),
        [Input('my-date-picker-range', 'start_date'),
        Input('my-date-picker-range', 'end_date'),
        Input('model-dropdown-3', 'value')])
    def update_output(start_date, end_date, model):
        start_date = re.split('T| ', start_date)[0] 
        end_date = re.split('T| ', end_date)[0]
        return get_daily_contribution_profile_avg_std_model(start_date, end_date, 'MO-OOA', model)


    @app.callback(
         Output('theta-evolution-2', 'figure'),
        [Input('my-date-picker-range', 'start_date'),
        Input('my-date-picker-range', 'end_date'),
        Input('model-dropdown-3', 'value')])
    def update_output(start_date, end_date, model):
        start_date = re.split('T| ', start_date)[0] 
        end_date = re.split('T| ', end_date)[0]
        return get_daily_contribution_profile_avg_std_model(start_date, end_date, 'LO-OOA', model)

    # @app.callback(
    #      Output('BCff-evolution', 'figure'),
    #     [Input('my-date-picker-range', 'start_date'),
    #     Input('my-date-picker-range', 'end_date')])
    # def update_output(start_date, end_date):
    #     start_date = re.split('T| ', start_date)[0] 
    #     end_date = re.split('T| ', end_date)[0]
    #     return get_coloc_data_evolution(start_date, end_date, 'BCff')

    # @app.callback(
    #      Output('BCwb-evolution', 'figure'),
    #     [Input('my-date-picker-range', 'start_date'),
    #     Input('my-date-picker-range', 'end_date')])
    # def update_output(start_date, end_date):
    #     start_date = re.split('T| ', start_date)[0] 
    #     end_date = re.split('T| ', end_date)[0]
    #     return get_coloc_data_evolution(start_date, end_date, 'BCwb')


    # @app.callback(
    #      Output('NOx-evolution', 'figure'),
    #     [Input('my-date-picker-range', 'start_date'),
    #     Input('my-date-picker-range', 'end_date')])
    # def update_output(start_date, end_date):
    #     start_date = re.split('T| ', start_date)[0] 
    #     end_date = re.split('T| ', end_date)[0]
    #     return get_coloc_data_evolution(start_date, end_date, 'NOx')

    # @app.callback(
    #      Output('CO-evolution', 'figure'),
    #     [Input('my-date-picker-range', 'start_date'),
    #     Input('my-date-picker-range', 'end_date')])
    # def update_output(start_date, end_date):
    #     start_date = re.split('T| ', start_date)[0] 
    #     end_date = re.split('T| ', end_date)[0]
    #     return get_coloc_data_evolution(start_date, end_date, 'CO')