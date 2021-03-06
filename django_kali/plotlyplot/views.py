import os
import numpy as np
import matplotlib.pyplot as plt
from django.shortcuts import render
from plotly.offline import plot
import plotly.graph_objects as go
import pandas as pd
import plotly.io as pio
import plotly.express as px
import pandas_datareader.data as web
import datetime as dt
import time
import networkx as nx
from faker import Faker
from .models import fao_forest_data
# Create your views here.
def plot_fao(request):
    start_ldb = time.time()
    data_data = [a for a in fao_forest_data.objects.values()]

    df_1 = pd.DataFrame(data=data_data)
    end_ldb = time.time()
    print("time loading table: ", end_ldb-start_ldb)
    def graph_network_plot(num):
        #df = pd.read_csv("sales_data.csv")
        df = df_1.copy()
        values = df.GOAL.value_counts().head(num).index
        values_2 = df["AREA_NEW"].value_counts().head(50).index
        values_3 = df["ELEM"].value_counts().head(num).index

        df = df.loc[(df.GOAL.isin(values))&
                    (df["AREA_NEW"].isin(values_2))&
                    (df["ELEM"].isin(values_3))]

        group = df.groupby(["AREA_NEW","GOAL"]).VALUE.sum().reset_index()
        print(group)

        G = nx.from_pandas_edgelist(group,"AREA_NEW","GOAL",edge_attr="VALUE")

        revenue = [i['VALUE'] for i in dict(G.edges).values()]

        pos = nx.spring_layout(G)

        edge_x = []
        edge_y = []
        edge_mid_x = []
        edge_mid_y = []

        for edge in G.edges():
            x0,y0 = pos[edge[0]]
            x1,y1 = pos[edge[1]]
            edge_x.append(x0)
            edge_x.append(x1)
            edge_mid_x.append((x0+x1)/2)
            edge_y.append(y0)
            edge_y.append(y1)
            edge_mid_y.append((y0+y1)/2)


        edge_trace = go.Scatter(
            x=edge_x, y=edge_y,
            line=dict(width=0.2, color='#111'),
            hoverinfo='none',
            mode="lines")

        edge_text = go.Scatter(
            x = edge_mid_x,
            y = edge_mid_y,
            hoverinfo ="text",
            marker=dict(
                #showscale=True,
                colorscale='Hot',
                reversescale=True,
                color=[],
                size=5,
                line_width=2),
            mode='markers')

        node_x = []
        node_y = []
        for node in G.nodes():
            x, y = pos[node]
            node_x.append(x)
            node_y.append(y)


        x_q = []
        x_p = []

        for edge in  G.edges():
            data_goal = G[edge[0]][edge[1]]["VALUE"]
            x_q.append(data_goal)
            x_p.append("Valor Acumulado: "+str(data_goal)+", Link: "+edge[0]+"<--->"+edge[1])

        edge_text.marker.color = x_q
        edge_text.text = x_p

        node_trace = go.Scatter(
            x=node_x, y=node_y,
            mode='markers',
        #    hovertext = pos.keys(),
            hoverinfo='text',
            marker=dict(
           #     showscale=True,
                colorscale='Rainbow',
                reversescale=True,
                color=[],
                size=15,
                line_width=2
                ))

        node_adjacencies = []
        node_text = []
        dica = {a:b for a,b in G.degree}

        for (node, (adjacencies)) in enumerate(pos.items()):
            node_adjacencies.append(dica[adjacencies[0]])
            node_text.append('Product: '+adjacencies[0])

        node_trace.marker.color = node_adjacencies
        node_trace.text = node_text
        return [edge_trace,edge_text,node_trace]
    def graph_networks_frames():
        frames = []
        for a in range(1,11):
            frame = graph_network_plot(5*a)
            print(a)
            frames.append(frame)

        fig = go.Figure(data=frames[0],
                        layout=go.Layout(
                            updatemenus=[dict(
                                type="buttons",
                                buttons=[dict(
                                    label="Play",
                                    method="animate",
                                    args=[None])])]),
                        frames=[go.Frame(data=fram) for fram in frames[1:]]
                        )
        fig.update_layout(autosize=True,title="GRAPH ANIMATION FROM FAO TABLE",height=1100)
        plot_div= plot(fig,output_type="div",include_plotlyjs=False)
        return plot_div

    def pie():
        start = time.time()
        df = df_1.copy()
        df = df.loc[(df.ELEM==df.ELEM.unique()[1])&(df.GOAL==df.GOAL.unique()[1])]
        df = df.sort_values("VALUE",ascending=False)
        print(df.columns)
        pivot = df.pivot(columns="YEAR",index="AREA_NEW",values="VALUE")
        pivot["TOTAL"] = pivot.sum(axis=1)
        pivot = pivot.sort_values("TOTAL",ascending=False)
        #pivot = pivot.iloc[:15]

        fp = pivot[pivot.columns[0]].reset_index()
        fp[fp.columns[1]] = fp[fp.columns[1]]/fp[fp.columns[1]].sum()
        fp = fp.iloc[:10]
        trace = go.Pie(labels=fp[fp.columns[0]].values,values=fp[fp.columns[1]].values)

        fig = go.Figure(data=[trace])
        fig.update_layout(title="PIE",autosize=True,height=1000)
        plot_div= plot(fig,output_type="div",include_plotlyjs=False)
        end = time.time()
        print("time executing function pie(): ",end-start)
        return plot_div

    def table():
        st_1 = time.time()
        start = dt.datetime(2019,1,1)
        end = dt.datetime(2021,11,8)
        df= web.DataReader(("TSLA"), "yahoo",start,end)
        df = df.reset_index()
        data = go.Table(header=dict(values=list([col for col in df.columns]),
                              fill_color="paleturquoise",
                              align="left"),
                  cells=dict(values=[df[col] for col in df.columns],
                             fill_color="lavender",
                             align="left"))
        fig = go.Figure(data=data)
        fig.update_layout(title="TESLA TABLE FROM ACTIONS",height=1000,autosize=True)
        plot_div= plot(fig,output_type="div",include_plotlyjs=False)
        en_1 = time.time()
        print("time executing function table(): ",en_1-st_1)
        return plot_div

    def box_2():
        st_1 = time.time()
        start = dt.datetime(2019,1,1)
        end = dt.datetime(2021,11,21)
        df= web.DataReader(("TSLA"), "yahoo",start,end)
        #another = df[[col for col in df.columns if col !="Volume"]].transpose()

        fig = go.Figure()

        #for step in range(50,df.shape[0],50):
        data = go.Candlestick(x=df.index,
                            open=df.Open,
                            high=df.High,
                            low=df.Low,
                            close=df.Close)
        fig.add_trace(data)
        fig.update_layout(autosize=True,height=1000,
                        title="TESLA ACTIONS BOX PLOT ON PLOTLY")

        plot_div = plot(fig,output_type="div",include_plotlyjs=False)
        en_1 = time.time()
        print("time executing function box_2(): ",en_1-st_1)
        return plot_div

    def heat():
        start = time.time()
        df = df_1.copy()
        df = df.loc[(df.ELEM==df.ELEM.unique()[1])&(df.GOAL==df.GOAL.unique()[1])]
        df = df.sort_values("VALUE",ascending=False)
        print(df.columns)
        pivot = df.pivot(columns="YEAR",index="AREA-NEW",values="VALUE")
        pivot["TOTAL"] = pivot.sum(axis=1)
        pivot = pivot.sort_values("TOTAL",ascending=False)
        pivot = pivot.iloc[:5]
        pivot = pivot.corr()
        data = go.Heatmap(x=pivot.index,y=pivot.columns,z=pivot.values)

        fig = go.Figure(data=data)
        fig.update_layout(title="HEAT",autosize=True,height=1100)
        plot_div= plot(fig,output_type="div",include_plotlyjs=False)
        end = time.time()
        print("time executing function heat(): ",end-start)
        return plot_div

    def img_ploting():
        start= time.time()
        url = "/mnt/d/data_ds/minerals_images/images.png"
        img = plt.imread(url)
        data = px.imshow(img*255)

        fig = go.Figure(data=data)
        fig.update_layout(title="IMAGE",autosize=True,height=1100)
        plot_div = plot(fig,output_type="div",include_plotlyjs=False)
        end = time.time()
        print("time executing function img_ploting(): ",end-start)
        return plot_div

    def geoplot(num):
        start = time.time()
        import geopandas as gpd
        path = "/mnt/d/data_ds/reviews-peruvian-food/data/data"
        geo_data = gpd.read_file(path+"/geospatial/districts.dbf")
        restaurants = pd.read_csv(path+"/restaurants.csv")
        reviews = pd.read_csv(path+"/reviews.csv")

        restaurants = restaurants.rename(columns={"id":"service"})

        merge = pd.merge(restaurants,reviews,on="service")
        geo_data = geo_data.rename(columns={"DISTRITO":"district"})
        merge_2 = pd.merge(merge,geo_data,on="district")

        merge_2 = merge_2.drop_duplicates(subset="district",keep="first")
        geo = gpd.GeoSeries(merge_2["geometry"].values).to_json()
        geo = eval(geo)

        for a,b in zip(geo["features"],merge_2.district):
            geo["features"][int(a["id"])]["id"]= b

        columns = [col for col in merge_2.columns if col not in
                                        ["district","geometry"] and
                                        str(merge_2[col].dtype) in ["int32","float32",
                                                                    "int64","float64"]]
        print(columns)
        data = px.choropleth_mapbox(merge_2,
                            geojson=geo,
                            locations=merge_2.district,
                            color=columns[num],
                            mapbox_style="carto-positron",
                            opacity = 0.5,
                            zoom=9,
                            center = {"lat": -12.04318, "lon": -77.02824},
                            color_continuous_scale="Viridis")
        #print(fig.data)
        data.update_layout(autosize=True,title="GEOGRAFIC PLOT FROM CITIZENS REVIEWS ON PERU-LIMA",height=1100)
        plot_div = plot(go.Figure(data=data),output_type="div",include_plotlyjs=False)
        return plot_div

    functions = [
        "geoplot(-2)","table()","pie()",
        "box_2()","img_ploting()","graph_networks_frames()"
    ]
    q_vals = [
        "geographic_plots",
        "show_tables",
        "pie_plotings",
        "box_plotings",
        "images_plots",
        "graphs_networks_plots"
    ]
    z_vals = {abc:defg for abc,defg in zip(q_vals,functions)}
    print(z_vals)
    context = {
        "data":q_vals,
    }
    if request.POST.get("new-1a"):
        txt_2 = request.POST.get("newa")
        print(z_vals[txt_2])
        context["plot"] = eval(z_vals[txt_2])
    return render(request,"plotlyplot/welcome.html",context)
