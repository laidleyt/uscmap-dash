# -*- coding: utf-8 -*-
"""
Created on Tue May 20 19:53:09 2025

@author: laidleyt
"""

import dash
from dash import dcc, html, Input, Output, State
import plotly.graph_objects as go
import pandas as pd
import json
import os
from urllib.request import urlopen 
import numpy as np
from dotenv import load_dotenv
import textwrap

# Load environment variables
load_dotenv()
mapbox_token = os.getenv("MAPBOX_TOKEN")

# Load data
csv_path = 'mapquintiles.csv'
df = pd.read_csv(csv_path, dtype={'fips': str})
df['fips'] = df['fips'].str.zfill(5)

# Load GeoJSON files
with urlopen("https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json") as response:
    counties_geojson = json.load(response)
with urlopen("https://raw.githubusercontent.com/PublicaMundi/MappingAPI/master/data/geojson/us-states.json") as response:
    states_geojson = json.load(response)

# Variable label mapping
variable_options = {
    'd_edu': 'Δ College Educated',
    'd_tothh': 'Δ Number of Households',
    'd_mhhinc': 'Δ Median Income',
    'd_youth': 'Δ Age 25–34 Population',
    'd_labor': 'Δ In Labor Force'
}

# Updated color scale for discrete quintiles
quintile_colors = {
    "1": '#C8E4C6',
    "2": '#77CCD0',
    "3": '#02BBDF',
    "4": '#0692D3',
    "5": '#003366'
}

# Build app
app = dash.Dash(__name__, external_stylesheets=['/assets/style.css'])
app.title = "County-Level Change Map"

app.layout = html.Div(className='container', children=[
    html.Div(className='header', children=[
        html.H1("US County-Level Changes: 2018–2023"),
        html.Div(className='controls', children=[
            html.Div(className='radio-group', children=[
                dcc.RadioItems(
                    id='view-selector',
                    options=[
                        {'label': 'Regular View', 'value': 'regular'},
                        {'label': 'Bottom 300', 'value': 'bottom'},
                        {'label': 'Top 300', 'value': 'top'}
                    ],
                    value='regular',
                    labelStyle={'display': 'inline-block'},
                    inputStyle={"display": "none"}
                )
            ])
        ])
    ]),
    html.Div(className='sidebar-map', children=[
        html.Div(className='sidebar', children=[
            html.P("Based on 5-Year Census ACS estimates; the 'top/bottom 300' buttons on top highlight the largest/smallest changes from 2018–2023. Hover the cursor over counties to see names and percent change."),
            html.Label("Select Variable:"),
            dcc.Dropdown(
                id='variable-dropdown',
                options=[{'label': name, 'value': var} for var, name in variable_options.items()],
                value='d_edu',
                clearable=False
            )
        ]),
        html.Div(className='main-content', children=[
            dcc.Graph(id='choropleth-map')
        ])
    ]),
    html.Div(className='footer-buttons', children=[
        html.Button("About", id='about-button', n_clicks=0),
        html.A("GitHub Repo", href="https://github.com/laidleyt", target="_blank")
    ]),
    html.Div(id='about-text',
    style={
        'display': 'none',
        'padding': '20px 30px',
        'margin-top': '40px',
        'margin-bottom': '80px',
        'backgroundColor': '#f5f5f5',
        'color': '#000000',
        'fontFamily': 'Poppins',
        'fontSize': '11px',
        'lineHeight': '1.5',
        'borderRadius': '6px',
        'maxWidth': '850px',
        'marginLeft': 'auto',
        'marginRight': 'auto',
        'boxShadow': '0 2px 6px rgba(0,0,0,0.1)'
    })
])

@app.callback(
    Output('choropleth-map', 'figure'),
    [Input('variable-dropdown', 'value'),
     Input('view-selector', 'value'),
     Input('choropleth-map', 'relayoutData')]
)
def update_map(selected_var, selected_view, relayoutData):
    # Default view
    center = {"lat": 37.8, "lon": -96}
    zoom = 3.2

    # Preserve user zoom/pan if available
    if relayoutData:
        center = relayoutData.get("mapbox.center", center)
        zoom = relayoutData.get("mapbox.zoom", zoom)

    filtered_df = df[df['var'] == selected_var].copy()

    if selected_view == 'top':
        filtered_df = filtered_df.nlargest(300, 'raw_value')
    elif selected_view == 'bottom':
        filtered_df = filtered_df.nsmallest(300, 'raw_value')

    filtered_df['quintile'] = filtered_df['quintile'].astype(str)
    colorscale = [[i / 4, quintile_colors[str(i + 1)]] for i in range(5)]

    fig = go.Figure()

    # Add county layer with discrete category mapping
    fig.add_trace(go.Choroplethmapbox(
        geojson=counties_geojson,
        locations=filtered_df['fips'],
        z=filtered_df['quintile'].astype(float),
        colorscale=colorscale,
        zmin=1,
        zmax=5,
        featureidkey="id",
        marker_line_width=0.5 if selected_view == 'bottom' else 0,
        colorbar=dict(
            title=dict(
                text="Quintiles",
                font=dict(size=14, color="black", family="Arial", weight="bold")
            ),
            tickvals=[1, 2, 3, 4, 5],
            ticktext=["1", "2", "3", "4", "5"],
            tickfont=dict(size=12, color="black", family="Arial", weight="bold"),
            len=0.5,
            thickness=10,
            xpad=10,
            yanchor="middle",
            y=0.5
        ),
        customdata=np.stack([filtered_df['county_name'], filtered_df['raw_value']], axis=-1),
        hovertemplate="<b>%{customdata[0]}</b><br>Change: %{customdata[1]:.1f}%<extra></extra>"
    ))

    # Add transparent-fill state outlines
    fig.add_trace(go.Choroplethmapbox(
        geojson=states_geojson,
        locations=[feature['id'] for feature in states_geojson['features']],
        z=[0] * len(states_geojson['features']),
        showscale=False,
        colorscale=[[0, 'rgba(0,0,0,0)'], [1, 'rgba(0,0,0,0)']],
        marker_line_color='black',
        marker_line_width=1,
        hoverinfo='skip',
        featureidkey="id"
    ))

    fig.update_layout(
    mapbox=dict(
        center=center,
        zoom=zoom,
        style="carto-positron"
    ),
    margin={"r": 0, "t": 40, "l": 0, "b": 0},
    autosize=True
)

    return fig

@app.callback(
    Output('about-text', 'style'),
    Output('about-text', 'children'),
    Input('about-button', 'n_clicks'),
    State('about-text', 'style')
)
def toggle_about(n_clicks, current_style):
    visible_style = {
        'display': 'block',
        'padding': '20px 30px',
        'margin-top': '40px',
        'margin-bottom': '80px',
        'backgroundColor': '#f5f5f5',
        'color': '#000000',
        'fontFamily': 'Poppins',
        'fontSize': '13px',
        'lineHeight': '1.5',
        'borderRadius': '6px',
        'maxWidth': '850px',
        'marginLeft': 'auto',
        'marginRight': 'auto',
        'boxShadow': '0 2px 6px rgba(0,0,0,0.1)'
    }

    if n_clicks % 2 == 1:
        about_content = html.Div([
            html.H4("About This Dashboard"),
            html.P("This dashboard visualizes county-level percent change across five key demographic and economic indicators, "
                   "based on the 2018 and 2023 vintages of the Census Bureau's 5-Year American Community Survey, which has a "
                   "high enough level of precision to offer reliable estimates down to more granular geographies. These changes "
                   "are not dispositive; there will always be some measurement error, and other sources of bias in any survey data. "
                   "Moreover, I must issue a caveat for Connecticut and Alaska — CT recently changed their counties to planning areas, "
                   "and the borders are not consistent; because of this, I instituted a 'fuzzy' crosswalk, and these estimates cannot be "
                   "reliably cited; this is merely illustrative and a more serious workaround might be attempted "
                   "if this project continues in another context. Also, a stylistic caveat: I prefer to project US maps (eg Albers) and not"
                   "flatten them, but it was unavoidable here; so too was the scale legend--vagaries of plotly, dash, etc."),
            html.P("The percent change in each of the following variables from 2018–2023 are mapped here, with their Census data variable name equivalents:"),
            html.Ul([
                html.Li("Δ College Educated (DP02_0068E OR _0067E FOR 2018 VINTAGE)"),
                html.Li("Δ Number of Households (DP02_0001E)"),
                html.Li("Δ Median Income (DP03_0062E)"),
                html.Li("Δ Age 25–34 Population (DP05_0010E)"),
                html.Li("Δ Age 16+ In Labor Force (DP03_0002E)")
            ]),
            html.H5("View Modes:"),
            html.Ul([
                html.Li("Regular View: All counties"),
                html.Li("Top 300: Counties with the largest positive change"),
                html.Li("Bottom 300: Counties with the largest negative change (or smallest positive change...)")
            ]),
            html.H5("Links:"),
            html.P([
                "Data Source: ",
                html.A("ACS 5-Year Estimates, Census Bureau", href="https://www.census.gov/data/developers/data-sets/acs-5year.html", target="_blank")
            ]),
            html.P([
                "Code and a more detailed readme available on ",
                html.A("GitHub", href="https://github.com/laidleyt", target="_blank")
            ]),
            html.P([
                "Feel free to touch base on ",
                html.A("LinkedIn – Tom L", href="https://linkedin.com/in/tomlaidley", target="_blank")
            ])
        ])
        return visible_style, about_content

    return {'display': 'none'}, ''


if __name__ == '__main__':
    import os
    app.run(debug=False, host='0.0.0.0', port=int(os.environ.get("PORT", 8050)))
