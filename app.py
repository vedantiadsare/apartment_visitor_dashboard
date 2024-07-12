import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px

# Load the data
df = pd.read_csv('data/visitor_data.csv')

# Convert 'date' column to datetime
df['date'] = pd.to_datetime(df['date'])

# Initialize the Dash app
app = dash.Dash(__name__)

# Layout of the app
app.layout = html.Div([
    html.H1('Apartment Visitor Analytics Dashboard'),
    dcc.DatePickerRange(
        id='date-picker',
        start_date=df['date'].min(),
        end_date=df['date'].max(),
        display_format='YYYY-MM-DD'
    ),
    dcc.Graph(id='visitor-trend-graph'),
    dcc.Dropdown(
        id='apartment-dropdown',
        options=[{'label': apt, 'value': apt} for apt in df['apartment_no'].unique()],
        multi=True,
        placeholder='Select apartment(s)'
    ),
    dcc.Graph(id='visitor-heatmap')
])

# Callback to update visitor trend graph
@app.callback(
    Output('visitor-trend-graph', 'figure'),
    [Input('date-picker', 'start_date'),
     Input('date-picker', 'end_date'),
     Input('apartment-dropdown', 'value')]
)
def update_visitor_trend(start_date, end_date, selected_apartments):
    filtered_df = df[(df['date'] >= start_date) & (df['date'] <= end_date)]
    if selected_apartments:
        filtered_df = filtered_df[filtered_df['apartment_no'].isin(selected_apartments)]
    trend_data = filtered_df.groupby('date')['visitors'].sum().reset_index(name='visitors')
    fig = px.bar(trend_data, x='date', y='visitors',
                 labels={'date': 'Date', 'visitors': 'Number of Visitors'},
                 title='Number of Visitors per Day')
    return fig

# Callback to update visitor heatmap
@app.callback(
    Output('visitor-heatmap', 'figure'),
    [Input('date-picker', 'start_date'),
     Input('date-picker', 'end_date'),
     Input('apartment-dropdown', 'value')]
)
def update_visitor_heatmap(start_date, end_date, selected_apartments):
    filtered_df = df[(df['date'] >= start_date) & (df['date'] <= end_date)]
    if selected_apartments:
        filtered_df = filtered_df[filtered_df['apartment_no'].isin(selected_apartments)]
    
    # Pivot the data to create a matrix for the heatmap
    heatmap_data = filtered_df.pivot_table(index='time', columns='apartment_no', values='visitors', aggfunc='sum', fill_value=0)
    
    # Create the heatmap figure
    fig = px.imshow(heatmap_data, color_continuous_scale='blues', labels={'color': 'Number of Visitors'}, title='Visitor Count Heatmap')
    return fig

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)