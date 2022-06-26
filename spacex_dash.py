from xml.etree.ElementInclude import include
import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px
from dash import no_update

app = dash.Dash(__name__)

#Clear the layout and do not display exception till callback gets executed
app.config.suppress_callback_exceptions = True

#read the spacex data into dataframe 
spacex_df = pd.read_csv('https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBM-DS0321EN-SkillsNetwork/datasets/spacex_launch_dash.csv',
                        encoding='ISO-8859-1')
min_payload = spacex_df['Payload Mass (kg)'].min()
max_payload = spacex_df['Payload Mass (kg)'].max()

# Layout section of dash
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard', style={'textAlign':'center', 'color':'#503D36','font-size':40}),
    html.Div([
        dcc.Dropdown(
            id='site-dropdown',
            options=[
                {'label': 'All Sites', 'value': 'ALL'},
                {'label': 'CCAFS LC-40', 'value':'CCAFS LC-40'},
                {'label': 'CCAFS SLC-40', 'value':'CCAFS SLC-40'},
                {'label': 'VAFB SLC-4E', 'value':'VAFB SLC-4E'},
                {'label': 'KSC LC-39A', 'value':'KSC LC-39A'},
            ], 
            value='ALL',
            placeholder='Select a Launch Site here',
            searchable=True
        ),
        html.Div(dcc.Graph(id='success-pie-chart')),
        html.Br(),

        #add a slider to select payload range
        html.P("Payload range (Kg):"),
        html.Div(dcc.RangeSlider(id='payload-slider', 
                                min=0, 
                                max=10000,
                                step=1000, 
                                value=[min_payload, max_payload],
                                marks={0:'0', 2000:'2000',5000:'5000',8000:'8000',10000:'10000'})),

        #add a scatter chart to show the correlation between payload and launch success
        html.Div(dcc.Graph(id='success-payload-scatter-chart'))
    ])
    #outer divisions
])
#layout ends

#place to add @app.callback decorator
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'), 
    Input(component_id='site-dropdown', component_property='value'))

#place to define the callback function
def get_pie_chart(value):
    if value == 'ALL':
        filter_df = spacex_df[spacex_df['class']==1].groupby(['Launch Site', 'class'], as_index=False).count()
        fig = px.pie(filter_df, values='Flight Number', names='Launch Site', title='Total Success Launches by Site')
        return fig
    else:
        filter_df = spacex_df[spacex_df['Launch Site'] == value].groupby(['Launch Site','class'], as_index=False).count()
        fig= px.pie(filter_df, values='Flight Number', names='class', title='Total Success Launches for '+value)
        return fig

#place to add a callback functon for 'site-down' and payload-slider' as inputs, 'success-payload-scatter-chart ' as output
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [Input(component_id='site-dropdown', component_property='value'),
    Input(component_id='payload-slider', component_property='value')]
)
#place to define the callback function
def get_scatter_chart(entered_site, payload):
    if entered_site == 'ALL':
        print(payload)
        filter_df = spacex_df[spacex_df['Payload Mass (kg)'].between(payload[0], payload[1], inclusive=True)]
        fig = px.scatter(filter_df, x='Payload Mass (kg)', y='class', color='Booster Version Category', title='Correlation between Payload and Success for all sites')
        return fig
    else:
        print(payload)
        filter_df = spacex_df[spacex_df['Launch Site']==entered_site]
        filter_df = filter_df[filter_df['Payload Mass (kg)'].between(payload[0], payload[1], inclusive=True)]
        fig = px.scatter(filter_df, x='Payload Mass (kg)', y='class', color='Booster Version Category',title='Correlation between Payload and Success for '+entered_site)
        return fig


if __name__ == '__main__':
    app.run_server()