# Erstmal alle wichtigen Sachen importieren :)
import pandas as pd
import plotly.express as px
from dash import dcc, html, Input, Output, dash_table, dash
import numpy as np
import dash_bootstrap_components as dbc
app = dash.Dash(__name__)
app = dash.Dash(external_stylesheets=[dbc.themes.COSMO], meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1"}
    ])
app.title = "Karte Humboldt"
server = app.server


# -- Daten importieren
df = pd.read_csv("Humbold_Metadaten_lat_lng_ohne_manuell.csv", sep=",")
df_table = df
df_table["Link"] = "[" + df_table["Titel"] + "]" + "(https://humboldt.unibe.ch/text/" + df_table["Dateiname"] + ")"
sprachen = df["Sprache"].sort_values().unique()
jahre = df["Jahr"].sort_values().unique()
orte = df["Erscheinungsort"].sort_values().unique()

# -- App Layout

tab1_content = dbc.Card(
    dbc.CardBody([

    dbc.Row([
        dbc.Col(html.Div([
            dcc.Dropdown(id="auswahl_sprache",
                         options=[{"label": "Alle Sprachen", "value": "Alle"}] + [{"label": x, "value": x} for x in
                                                                                  sprachen],
                         multi=True,
                         clearable=False,
                         value="Alle",
                         className="Dropdown"
                         ),

                dcc.Dropdown(id="auswahl_ort",
                             options=[{"label": "Alle Orte", "value": "Alle"}] + [{"label": x, "value": x} for x in
                                                                                  orte],
                             multi=True,
                             clearable=False,
                             value="Alle",
                             className="Dropdown"
                             ),

            ], style={"width": "50%"}), width=12, lg=12),
    ]),
    dbc.Row([
        dbc.Col([html.Div(
            dcc.Graph(id="world_map", figure={}, config = {'modeBarButtonsToRemove': ["pan2d", "zoomInGeo", "zoomOutGeo", "select2d", "lasso2d"]}), id="map-Container", ),
            dcc.RangeSlider(1789, 1859, 1,
                            value=[1789, 1799],
                            marks=None,
                            tooltip={"placement": "bottom", "always_visible": True},
                            id="auswahl_jahr",
                            allowCross=False),
        ], width=12, lg=8),
        dbc.Col(
            dash_table.DataTable(
                id="tabelle",
                data=df_table.to_dict('records'),
                columns=[
                    {'id': "Link", 'name': "Titel", "presentation": 'markdown'},
                    {"id": "Sprache", "name": "Sprache"},
                    {'id': "Erscheinungsort", 'name': "Ort"},
                    {'id': "Jahr", 'name': "Jahr"},
                ],
                style_data={
                    'whiteSpace': 'normal',
                    'height': 'auto'},
                style_data_conditional=[
                    {
                        "if": {"state": "selected"},
                        "backgroundColor": "inherit !important",
                        "border": "inherit !important",
                    }
                ],
                style_cell={"textAlign": "left", "font-family": "sans-serif", "font-size": 12},
                style_header={"position": "sticky", "top": -1},
                sort_action="native",
                export_format="csv",
                style_table={'max-height': '70vh', "width": "100%", 'overflowX': 'auto'}),
        width=12, lg=4, align="start")
    ]),
    html.Div(
    dbc.Row([
        dbc.Col(
            dcc.Graph(id="bar_plot", config = {'modeBarButtonsToRemove': ["pan2d", "zoom2d", "zoomIn2d", "zoomOut2d", "select2d", "lasso2d", "autoScale2d", "resetScale2d"]}),
        width=12, lg=8),
        dbc.Col(
            dcc.Graph(id="pie_plot", config = {'modeBarButtonsToRemove': ["pan2d", "zoomIn2d", "zoomOut2d", "select2d", "lasso2d"]})
        ,width=12, lg=4)
    ]), id="UnteresDiv")

]))

tab2_content = dbc.Card(
    dbc.CardBody(
        dbc.Row(
            dbc.Col(
                dcc.Graph(id="animierte_karte", style={'height': '90vh'} )
            ,width=12, lg=12)
        )
    ))

app.layout = dbc.Tabs(
    [
        dbc.Tab(tab1_content, label="Dashboard"),
        dbc.Tab(tab2_content, label="Animierte Karte"),
    ]
)

# -- Karte mit Dash verknüpfen
@app.callback(
    [Output(component_id="world_map", component_property="clickData")],
    [Input(component_id="map-Container", component_property="n_clicks")],
)
def reset_clickData(n_clicks):
    return [None]


@app.callback(
    [Output(component_id="world_map", component_property="figure")],
    [Output(component_id="bar_plot", component_property="figure")],
    [Output(component_id="pie_plot", component_property="figure")],
    [Output(component_id="animierte_karte", component_property="figure")],
    [Output(component_id="tabelle", component_property="data")],
    [Input(component_id="world_map", component_property="figure")],
    [Input(component_id="auswahl_sprache", component_property="value")],
    [Input(component_id="auswahl_jahr", component_property="value")],
    [Input(component_id="auswahl_ort", component_property="value")],
    [Input(component_id="world_map", component_property="clickData")],
)
def update_data(original_figure, sprache, jahr, ort, clickData):
    dff = df.copy()
    dff_animated = df.copy()
    dff_animated = dff_animated.groupby(["Erscheinungsort", "lat", "lng", "Jahr"]).size().reset_index(name='Anzahl Publikationen')

    if "Alle" in sprache:
        dff = dff
    else:
        dff = dff[dff["Sprache"].isin(sprache)]


    if "Alle" in ort:
        dff = dff
    else:
        dff = dff[dff["Erscheinungsort"].isin(ort)]

    dff = dff[(dff["Jahr"] >= jahr[0]) & (dff["Jahr"] <= jahr[1])]

    dff_tabelle = dff
    if clickData == None:
        dff_tabelle = dff_tabelle
    else:
        dff_tabelle = dff_tabelle[(clickData["points"][0]["lat"] == dff_tabelle["lat"].astype(float)) & (
                    clickData["points"][0]["lon"] == dff_tabelle["lng"].astype(float))]
    dff2 = dff.copy()
    dff2 = dff2.groupby(["Erscheinungsort", "lat", "lng", "Jahr"]).size().reset_index(name='Anzahl Publikationen')
    dff = dff.groupby(["Erscheinungsort", "lat", "lng"]).size().reset_index(name='Anzahl Publikationen')

    if len(dff) == 0:
        dff["lat"] = [0.0]
        dff["lng"] = [0.0]
        fig = px.scatter_geo(
            dff, lat="lat", lon="lng", projection="natural earth",
            hover_data={"lat": False, "lng": False, }, labels=dict(x="Erscheinungsort")

        )
        fig.update_traces(marker={"size": 0.0000001}, hovertemplate=None, hoverinfo="skip")
    else:
        fig = px.scatter_geo(
            dff, lat="lat", lon="lng", projection="natural earth", opacity=0.9, size_max=15,
            hover_data={"lat": False, "lng": False, "Erscheinungsort": True}, size="Anzahl Publikationen",
            color="Anzahl Publikationen", color_continuous_scale=px.colors.sequential.Redor)
        fig.update_traces(customdata=np.stack((dff["Erscheinungsort"], dff["Anzahl Publikationen"]), axis=-1))

        fig.update_traces(hovertemplate='<b>%{customdata[0]}</b><br>Anzahl Publikationen: %{customdata[1]}<extra></extra>')
        fig.update_traces(marker_sizemin=4, )
        fig.update_layout(
            margin=dict(l=0, r=0, t=50, b=50),
            font=dict(size=10),
            font_family="sans-serif"

        )

        fig.layout.coloraxis.colorbar.title = 'Publikationen'

        if 'layout' in original_figure:
            fig.update_geos(original_figure['layout']['geo'])

    dff_bar = dff_tabelle.groupby(["Erscheinungsort", "lat", "lng", "Jahr"]).size().reset_index(name='Anzahl Publikationen')
    dff_bar = dff_bar.groupby(["Jahr"])['Anzahl Publikationen'].sum().reset_index(name='Anzahl Publikationen')
    fig2 = px.bar(dff_bar, x="Jahr", y="Anzahl Publikationen", color_discrete_sequence=px.colors.qualitative.Pastel)
    fig2.update_traces(customdata=np.stack((dff_bar["Anzahl Publikationen"], dff_bar["Jahr"]), axis=-1))
    fig2.update_traces(hovertemplate='%{customdata[1]}<br><b>Publikationen absolut:</b> %{customdata[0]}<extra></extra>')
    fig2.update_xaxes(dtick="1")
    fig2.update_traces(width=1)
    fig2.update_layout(
        xaxis=dict(
            tickfont=dict(size=9)),
    dragmode=False )
    dff_pie = dff2
    dff_pie = dff_pie.groupby(["Erscheinungsort"])['Anzahl Publikationen'].sum().reset_index(
        name='Anzahl Publikationen')
    fig3 = px.pie(dff_pie,
                  values="Anzahl Publikationen",
                  names="Erscheinungsort",
                  hole=.3,
                  color_discrete_sequence=px.colors.qualitative.Pastel,
                  )
    fig3.update_traces(textinfo='none')
    fig3.update_traces(customdata=np.stack((dff_pie["Erscheinungsort"], dff_pie["Anzahl Publikationen"]), axis=-1))
    fig3.update_traces(hovertemplate='<b>%{customdata[0][0]}</b><br>Anzahl: %{customdata[0][1]}<br>%{percent}')
    fig3.update_layout(showlegend=False)
    dff_animated = dff_animated.sort_values("Jahr")

    fig4 = px.scatter_geo(
        dff_animated, lat="lat", lon="lng", hover_name="Erscheinungsort",
        hover_data={"Erscheinungsort": False, "Anzahl Publikationen": False, "Jahr": False, "lat": False,
                    "lng": False},
        size="Anzahl Publikationen", animation_frame="Jahr", color="Anzahl Publikationen",
        projection="natural earth", opacity=0.9,
        title="Karte Erscheinungsorte und Erscheinungsjahre",  color_continuous_scale=px.colors.sequential.Redor
    )
    fig4.update_traces(marker_sizemin=4, )

    #fig4.update_traces(customdata=np.stack((dff["Erscheinungsort"], dff["Anzahl Publikationen"]), axis=-1))
    #fig4.update_traces(hovertemplate = '<b>%{customdata[0]}</b><br>Anzahl Publikationen: %{customdata[1]}<extra></extra>')
    #for f in fig4.frames:
     #   f.data[0].update(hovertemplate='<b>%{customdata[0]}</b><br>Anzahl Publikationen: %{customdata[1]}<extra></extra>')

    dff_tabelle = dff_tabelle.sort_values("Jahr")
    return [fig, fig2, fig3, fig4, dff_tabelle.to_dict("records")]


# -- Und jetzt starten wir unsere App!
if __name__ == '__main__':
    app.run_server(debug=True)
