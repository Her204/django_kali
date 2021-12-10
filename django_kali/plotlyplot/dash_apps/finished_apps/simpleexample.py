from logging import debug
from dash import dcc
from dash import html
import plotly.express as px
from dash.dependencies import Input, Output
import plotly.graph_objs as go
from django_plotly_dash import DjangoDash
import pandas as pd
import geopandas as gpd

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
path = "/mnt/d/data_ds/reviews-peruvian-food/data/data"
districts = gpd.read_file(path+"/geospatial/districts.dbf")
restaurants = pd.read_csv(path+"/restaurants.csv")
reviews = pd.read_csv(path+"/reviews.csv")

restaurants = restaurants.rename(columns={"id":"service"})
districts = districts.rename(columns={"DISTRITO":"district"})
merge = pd.merge(restaurants,reviews,on="service")

values = [str(float(val)) for val in range(1000)]
merge["min_price"] = merge.loc[merge.min_price.isin(values)].min_price
merge["max_price"] = merge.loc[merge.max_price.isin(values)].max_price
merge["min_price"] = merge.min_price.apply(lambda x: float(x))
merge["max_price"] = merge.max_price.apply(lambda x: float(x))

group_data = merge.groupby("district").agg({"score":["mean","sum"],
                                            "n_reviews":["sum"],
                                            "min_price":["mean"],
                                            "max_price":["mean"]})
gd = pd.DataFrame(group_data) 
gd = gd.fillna(0)    
gd = gd.reset_index()

fd = pd.merge(group_data,districts[["district","geometry"]],on="district")
fd = fd.fillna(0)

ideal_geo = districts.loc[(districts.district.isin(gd["district"]))& 
               (districts.DEPARTAMEN=="LIMA")]
               
geo = gpd.GeoSeries(ideal_geo.geometry.values).to_json()
geo = eval(geo)

for i,b in enumerate(ideal_geo.district.values):
    geo["features"][i]["id"]= b

gd.columns = gd.columns.map(lambda x: x[0]+"-"+x[1])

candidates = [a for a in gd.columns]

print(candidates[1:])

app = DjangoDash('SimpleExample', external_stylesheets=external_stylesheets)

app.layout = html.Div([
    html.P("Candidate:"),
    dcc.RadioItems(
        id='candidate', 
        options=[{'value': x, 'label': x} 
                 for x in candidates[1:]],
        value=candidates[1],
        labelStyle={'display': 'inline-block'}
    ),
    dcc.Graph(id="choropleth"),
])
@app.callback(
    Output("choropleth", "figure"), 
    [Input("candidate", "value")])
def display_choropleth(candidate):
    fig = px.choropleth_mapbox(gd.iloc[1:],
                                geojson=geo,
                                locations=gd["district-"].iloc[1:],
                                color=candidate,
                                mapbox_style="open-street-map",
                                opacity = 0.5,
                                zoom=9,
                                center = {"lat": -12.04318, "lon": -77.02824},
                                color_continuous_scale="Viridis")
    fig.update_layout(
            margin={"r":0,"t":0,"l":0,"b":0})
    return {"data":[fig]}

#if __name__ == "__main__":
#    app.runserver(debug=False)
