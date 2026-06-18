# app.py - Archivo principal de la aplicación Dash
import dash
from dash import dcc, html, Input, Output, callback
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from datetime import datetime
import os

# Inicializar la aplicación Dash
app = dash.Dash(__name__, suppress_callback_exceptions=True)
server = app.server

# Leer datos
def load_data():
    try:
        df = pd.read_csv(r'D:\nvargas\Downloads\Nueva carpeta (2)\data\sensor.csv')
        return df
    except:
        # Datos de ejemplo si no existe el archivo
        return pd.DataFrame()

# Layout principal
app.layout = html.Div([
    html.Header([
        html.H1("EDA - Bomba de Agua", 
                style={'textAlign': 'center', 'color': '#0074D9', 'margin': '20px'}),
        html.Hr()
    ]),
    
    # Tabs para diferentes visualizaciones
    dcc.Tabs([
        dcc.Tab(label='Distribución de Estados', children=[
            html.Div([
                html.H3("Conteo por Estado de la Bomba"),
                dcc.Graph(id='bar-chart-estado'),
                html.H3("Proporción por Estado"),
                dcc.Graph(id='pie-chart-estado')
            ], style={'padding': '20px'})
        ]),
        
        dcc.Tab(label='Series Temporales', children=[
            html.Div([
                html.H3("Serie Temporal por Sensor"),
                dcc.Dropdown(
                    id='dropdown-sensor',
                    options=[],
                    value='sensor_00'
                ),
                dcc.Graph(id='time-series-plot')
            ], style={'padding': '20px'})
        ]),
        
        dcc.Tab(label='Distribuciones', children=[
            html.Div([
                html.H3("Histograma y KDE"),
                dcc.Dropdown(
                    id='dropdown-sensor-hist',
                    options=[],
                    value='sensor_00'
                ),
                dcc.Graph(id='histogram-plot'),
                html.H3("Box Plot por Estado"),
                dcc.Dropdown(
                    id='dropdown-sensor-box',
                    options=[],
                    value='sensor_00'
                ),
                dcc.Graph(id='boxplot-plot')
            ], style={'padding': '20px'})
        ]),
        
        dcc.Tab(label='Correlaciones', children=[
            html.Div([
                html.H3("Matriz de Correlación"),
                dcc.Graph(id='correlation-heatmap')
            ], style={'padding': '20px'})
        ]),
        
        dcc.Tab(label='Violin Plots', children=[
            html.Div([
                html.H3("Distribución por Estado"),
                dcc.Dropdown(
                    id='dropdown-sensor-violin',
                    options=[],
                    value='sensor_00'
                ),
                dcc.Graph(id='violin-plot')
            ], style={'padding': '20px'})
        ]),
        
        dcc.Tab(label='Hexbin', children=[
            html.Div([
                html.H3("Densidad Bivariada"),
                dcc.Dropdown(
                    id='dropdown-sensor-hexbin-1',
                    options=[],
                    value='sensor_00'
                ),
                dcc.Dropdown(
                    id='dropdown-sensor-hexbin-2',
                    options=[],
                    value='sensor_01'
                ),
                dcc.Graph(id='hexbin-plot')
            ], style={'padding': '20px'})
        ])
    ]),
    
    html.Footer([
        html.P("Análisis Exploratorio de Datos - Bomba de Agua", 
               style={'textAlign': 'center', 'margin': '20px', 'color': '#666'})
    ])
])

# Callbacks
@app.callback(
    [Output('bar-chart-estado', 'figure'),
     Output('pie-chart-estado', 'figure')],
    Input('bar-chart-estado', 'id')  # Dummy input
)
def update_estado_charts(dummy):
    df = load_data()
    if df.empty or 'machine_status' not in df.columns:
        return go.Figure(), go.Figure()
    
    conteo = df['machine_status'].value_counts()
    
    # Bar chart
    fig_bar = px.bar(
        x=conteo.index, 
        y=conteo.values,
        labels={'x': 'Estado', 'y': 'Número de registros'},
        title='Conteo por Estado de la Bomba',
        color=conteo.index,
        color_discrete_map={'NORMAL': '#4CAF50', 'RECOVERING': '#FF9800', 'BROKEN': '#F44336'}
    )
    fig_bar.update_layout(showlegend=False)
    
    # Pie chart
    fig_pie = px.pie(
        values=conteo.values,
        names=conteo.index,
        title='Proporción por Estado de la Bomba',
        color_discrete_map={'NORMAL': '#4CAF50', 'RECOVERING': '#FF9800', 'BROKEN': '#F44336'}
    )
    
    return fig_bar, fig_pie

@app.callback(
    [Output('dropdown-sensor', 'options'),
     Output('dropdown-sensor-hist', 'options'),
     Output('dropdown-sensor-box', 'options'),
     Output('dropdown-sensor-violin', 'options'),
     Output('dropdown-sensor-hexbin-1', 'options'),
     Output('dropdown-sensor-hexbin-2', 'options')],
    Input('bar-chart-estado', 'id')
)
def update_dropdowns(dummy):
    df = load_data()
    if df.empty:
        return [], [], [], [], [], []
    
    sensor_cols = [col for col in df.columns if col.startswith('sensor')]
    options = [{'label': col, 'value': col} for col in sensor_cols[:20]]  # Limitar a 20 sensores
    return options, options, options, options, options, options

@app.callback(
    Output('time-series-plot', 'figure'),
    Input('dropdown-sensor', 'value')
)
def update_time_series(sensor):
    df = load_data()
    if df.empty or sensor not in df.columns:
        return go.Figure()
    
    if 'timestamp' in df.columns:
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df_sorted = df.sort_values('timestamp')
    else:
        df_sorted = df
    
    fig = px.line(
        df_sorted, 
        x=df_sorted.index if 'timestamp' not in df.columns else 'timestamp',
        y=sensor,
        color='machine_status' if 'machine_status' in df.columns else None,
        title=f'Serie Temporal - {sensor}',
        labels={'index': 'Tiempo', sensor: 'Valor'}
    )
    fig.update_layout(hovermode='x unified')
    
    return fig

@app.callback(
    Output('histogram-plot', 'figure'),
    Input('dropdown-sensor-hist', 'value')
)
def update_histogram(sensor):
    df = load_data()
    if df.empty or sensor not in df.columns:
        return go.Figure()
    
    fig = px.histogram(
        df, 
        x=sensor,
        nbins=50,
        title=f'Distribución - {sensor}',
        marginal='box'
    )
    
    return fig

@app.callback(
    Output('boxplot-plot', 'figure'),
    Input('dropdown-sensor-box', 'value')
)
def update_boxplot(sensor):
    df = load_data()
    if df.empty or sensor not in df.columns or 'machine_status' not in df.columns:
        return go.Figure()
    
    fig = px.box(
        df,
        x='machine_status',
        y=sensor,
        color='machine_status',
        title=f'Distribución por Estado - {sensor}',
        color_discrete_map={'NORMAL': '#4CAF50', 'RECOVERING': '#FF9800', 'BROKEN': '#F44336'}
    )
    
    return fig

@app.callback(
    Output('violin-plot', 'figure'),
    Input('dropdown-sensor-violin', 'value')
)
def update_violin(sensor):
    df = load_data()
    if df.empty or sensor not in df.columns or 'machine_status' not in df.columns:
        return go.Figure()
    
    fig = px.violin(
        df,
        x='machine_status',
        y=sensor,
        color='machine_status',
        box=True,
        points='all',
        title=f'Distribución Violin - {sensor}',
        color_discrete_map={'NORMAL': '#4CAF50', 'RECOVERING': '#FF9800', 'BROKEN': '#F44336'}
    )
    
    return fig

@app.callback(
    Output('correlation-heatmap', 'figure'),
    Input('correlation-heatmap', 'id')
)
def update_correlation(dummy):
    df = load_data()
    if df.empty:
        return go.Figure()
    
    sensor_cols = [col for col in df.columns if col.startswith('sensor')]
    if not sensor_cols:
        return go.Figure()
    
    corr_matrix = df[sensor_cols].corr()
    
    fig = px.imshow(
        corr_matrix,
        title='Matriz de Correlación de Sensores',
        color_continuous_scale='RdBu_r',
        zmin=-1,
        zmax=1
    )
    fig.update_layout(height=800)
    
    return fig

@app.callback(
    Output('hexbin-plot', 'figure'),
    [Input('dropdown-sensor-hexbin-1', 'value'),
     Input('dropdown-sensor-hexbin-2', 'value')]
)
def update_hexbin(sensor1, sensor2):
    df = load_data()
    if df.empty or sensor1 not in df.columns or sensor2 not in df.columns:
        return go.Figure()
    
    fig = px.density_heatmap(
        df,
        x=sensor1,
        y=sensor2,
        title=f'Densidad Bivariada - {sensor1} vs {sensor2}',
        nbinsx=50,
        nbinsy=50
    )
    
    return fig

if __name__ == '__main__':
    app.run(debug=True, port=8050)