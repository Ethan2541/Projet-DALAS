# TODO
# Sections : Parties importantes de l'EDA
# ---
# Mise en forme conditionnelle
# Visualisation des données
# Résultats du clustering
# ---
# Paragraphes pour expliquer quelques analyses et résumer légèrement les résultats

from dash import Dash, html, dash_table, dcc, callback, Output, Input
import numpy as np
import pandas as pd
import plotly.express as px


app = Dash(__name__)

app.layout = html.Div([
    html.H1(children='Votes et Elections', style={'text-align': 'center'}),
    html.Hr(style={'height':'3px', 'color': '#026b9c', 'border': 'none', 'background-color': '#026b9c'}),
    html.Div([
        html.H2(children='Aperçu des Données', style={'text-align': 'center', 'margin': '0', 'color': '#2a303b'}),
        dcc.RadioItems(options=['Résumé', 'Résumé (normalisé)', 'Données'], value='Résumé', id='radio-data', style={'display': 'flex', 'justify-content': 'space-around', 'margin': '20px 0 10px 0'}),
        dash_table.DataTable(data=df[['GEOID', 'winner', 'votes_gop', 'Median_Household_Income_2019']].to_dict('records'), page_size=10, id='data-table', style_table={'overflowX': 'auto'})
    ], style={'background-color': '#f5f6f8', 'padding': '20px', 'border-radius': '5px', 'margin-bottom': '30px'}),
    html.Div([
        html.H2(children='Exploration des Données', style={'text-align': 'center', 'margin': '0', 'color': '#2a303b'}),
        dcc.Graph(figure=px.bar(df_bar, x='bins', y='freq', labels={'bins': 'Catégorie de Revenu', 'freq': 'Proportion'}, title='Médiane des revenus selon la localisation géographique'), id='freq-income-bar'),
        html.Div([
            dcc.Graph(figure=px.histogram(df, x='winner', y='votes_gop', labels={'winner': 'Parti gagnant', 'votes_gop': 'Nombre de votes'}, title='Résultats des élections'), id='votes-gop-hist'),
            dcc.Graph(figure=px.bar(df_bar2, x='bins', y='freq', labels={'bins': 'Catégorie selon le nombre de votes', 'freq': 'Proportion des votes'}, title='Répartition des voix selon la localisation'), id='zipf-bar')
        ], style={'display': 'grid', 'grid-template-columns': '1fr 2fr', 'gap': '10px'})
    ], style={'padding': '20px', 'border-radius': '5px'})
], style={'font-family': 'Helvetica', 'background-color': 'white', 'padding': '10px', 'border-radius': '5px', 'margin-bottom': '10px'})

@callback(
    Output(component_id='data-table', component_property='data'),
    Input(component_id='radio-data', component_property='value')
)
def update_table(mode):
    if mode == 'Résumé':
        return df.describe().to_dict('records')
    elif mode == 'Résumé (normalisé)':
        return df_norm.describe().to_dict('records')
    elif mode == 'Données':
        return df.to_dict('records')
    
if __name__ == '__main__':
    app.run(debug=True)