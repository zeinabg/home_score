import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import pandas as pd
import numpy as np
from urllib.request import urlopen
import json
import geopandas as gpd


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

def create_geofile():
  zip_shape = gpd.read_file('data/cb_2018_us_zcta510_500k/cb_2018_us_zcta510_500k.shp').rename(columns={'ZCTA5CE10': 'zipcode'})
  california_zipcodes = pd.read_csv('data/zipcodes.csv')
  zip_shape = zip_shape.loc[zip_shape.zipcode.isin(california_zipcodes.zipcode.astype(str))]
  zip_shape.set_index('zipcode', drop=False, inplace=True)
  np.random.seed(13)
  zip_shape['crime'] = np.round(10 * np.random.rand(len(zip_shape)))
  zip_shape['health'] = np.round(10 * np.random.rand(len(zip_shape)))
  zip_geojson = json.loads(zip_shape[['geometry', 'zipcode', 'crime', 'health']].to_json())
  with open('data/zip_geojson.json', 'w') as f:
    json.dump(zip_geojson, f)
  zip_shape.to_pickle('data/zip_shape.pkl')


def load_geofile():
  with open('data/zip_geojson.json', 'r') as f:
    zip_geojson = json.load(f)
  zip_shape = pd.read_pickle('data/zip_shape.pkl')
  return zip_shape, zip_geojson


def render_map(metric):
  assert metric in ['crime', 'health']
  zip_shape, zip_geojson = load_geofile()
  return px.choropleth_mapbox(
      zip_shape, geojson=zip_geojson,
      locations='zipcode', color=metric,
      color_continuous_scale="reds" if metric == 'crime' else 'blues',
     range_color=(0, 10),
     zoom=7, center = {"lat": 37.3902, "lon": -121.9129},
     opacity=0.5,
     labels={metric:'%s score' % metric},
      mapbox_style="open-street-map",
      width=1000, height=800
  )


create_geofile()
crime_map = render_map('crime')#.update_layout(margin={"r":0,"t":20,"l":0,"b":20})
health_map = render_map('health')#.update_layout(margin={"r":20,"t":20,"l":20,"b":20})



app.layout = html.Div(children=[
  html.H1(
    children='Home Score'
  ),
  html.H3(children='Find your new home with all factors considered.'),
 html.Div([
  html.Div([
            html.H4('Crime Score', style={'textAligh': 'center'}),
            dcc.Graph(id='crime-map', figure=crime_map)
        ], className="six columns"),

        html.Div([
            html.H4('Health Score', style={'textAligh': 'center'}),
            dcc.Graph(id='health-map', figure=health_map)
        ], className="six columns"),
    ], className="row")
])

if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0')
