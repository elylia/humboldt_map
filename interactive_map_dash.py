# Erstmal alle wichtigen Sachen importieren :)
import pandas as pd
import plotly.express as px
from dash import dcc, html, Input, Output, dash_table, dash
import numpy as np

app = dash.Dash(__name__)
app.title = "Karte Humboldt"

# -- Daten importieren
# Daten werden aus CSV-Datei in ein Dataframe gelesen
df = pd.read_csv("Humbold_Metadaten_lat_lng_ohne_manuell.csv", sep=",")
# Dataframe wird für die Tabelle kopiert
df_table = df
# Es wird eine Spalte "Links" erstellt. Die Links sind für Markdown geschrieben, damit sie später auch als Links erkannt werden
df_table["Link"] = "[" + df_table["Titel"] + "]" + "(https://humboldt.unibe.ch/text/" + df_table["Dateiname"] + ")"
# Wir setzen zwei Variablen - wir wollen alle vorkommenden Sprachen und alle vorkommenden Jahre erhalten
sprachen = df["Sprache"].sort_values().unique()
jahre = df["Jahr"].sort_values().unique()

# -- App Layout
# Hier wird unsere Dash App gestaltet.
# Wo möglich ist das Styling in die CSS Datei ausgelagert worden. Im Sinne der Lesbarkeit des Codes sollten wir das auch so fortführen denke ich :)
# Wir beginnen mit einem Div...
app.layout = html.Div([
    # Dann fügen wir eine Überschrift hinzu
    html.H1("Interaktive Karte Humboldt"),
    # Nun kommen verschachtelte Divs. Das ist notwendig, damit die Tabelle neben der Karte platziert werden kann
    # In den Divs sind die einzelnen Komponenten unserer Dash-App drin. Jede Komponente hat eine ID, damit wir sie später ansteuern können und Daten abgreifen und übergeben können
    html.Div([
        html.Div([
        html.H2("Interaktive Karte"),
            # Hier wird der Dropdown für die Auswahl der Sprache eingefügt
            dcc.Dropdown(id="auswahl_sprache",
                         # In der ersten eckigen Klammer wird die Option "Alle Sprachen hinzugefügt, in der zweiten eckigen Klammer verwenden wir unsere "sprachen"-Variable um alle anderen individuellen Sprachoptionen an das Dropdown zu übergeben
                         options=[{"label": "Alle Sprachen", "value": "Alle"}] + [{"label": x, "value": x} for x in
                                                                                  sprachen],
                         # Hier schalten wir aus, dass man mehrere Länder auswählen kann (das hab ich gemacht, da das sonst für mich viel komplizierter zu programmieren gewesen wäre. Wenn ihr das Feature aber wichtig findet, kann ich das auch noch machen
                         multi=False,
                         # Hier schalten wir aus, dass man die Auswahl komplett löschen kann (das wollen wir nicht, weil der resultierende Wert dann leer wäre)
                         clearable=False,
                         # Hier wird der Standardwert (Alle Sprachen) gesetzt
                         value="Alle",
                         # Hier wird die Breite, Schriftart und Schriftgröße des Dropdowns festgelegt
                         className="Dropdown"
                         ),
            # Hier wird die Weltkarte eingefügt. Figure ist noch leer. Das wird dann über unseren Callback übergeben
            dcc.Graph(id="world_map", figure={}),

            html.Div(
                # Hier fügen wir den Slider ein. Die ersten beiden Zahlen geben den maximalen und minimalen Wert an. Die dritte Zahl gibt die Schrittgröße an (es kann also immer um ein Jahr verstellt werden)

                dcc.RangeSlider(1789, 1859, 1,
                                # Mit Value wird der Startwert angegeben
                                value=[1789, 1799],
                                # Marks haben wir ausgeschaltet, da ich Tooltips für unseren Einsatzzweck geeigneter fand
                                marks=None,
                                # Stattdessen haben wir einen Tooltip. Dieser ist immer sichtbar und wird unter der Karte platziert
                                tooltip={"placement": "bottom", "always_visible": True},
                                # Wir setzen auch hier eine ID, um den im Slider eingestellten Wert später abgreifen zu können
                                id="auswahl_jahr",
                                # Die beiden Punkte am Slider können nicht überkreuzt werden
                                allowCross=False),
                #Styling des Divs. Mit Margin sorgen wir dafür, dass der Slider in der Mitte ist
                className="Slider"), ],
            # ID & Classname (fürs CSS) für Div wird vergeben
            id="map-Container", className="DivKarte"),
        # Jetzt kommt unsere Tabelle
        html.Div([
            html.H2("Tabelle mit Verlinkung zur digitalen Edition"),
            dash_table.DataTable(
            # Auch hier vergeben wir wieder eine ID
            id="tabelle",
            # Hier bereiten wir unsere Daten aus dem Dataframe df_table vor
            data=df_table.to_dict('records'),
            # Wir definieren die verschiedenen Spalten
            columns=[
                # In der Spalte "Links" müssen wir noch definieren, dass der Text als Link interpretiert werden soll. Wir haben den Link in Markdown vorbereitet. Daher geben wir jetzt presentation: markdown an.
                {'id': "Link", 'name': "Titel", "presentation": 'markdown'},
                {"id": "Sprache", "name": "Sprache"},
                {'id': "Erscheinungsort", 'name': "Ort"},
                {'id': "Jahr", 'name': "Jahr"},
                ],
            # Styling der Zellen 1
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
            # Styling der einzelnen Zellen 2
            style_cell={"textAlign": "left", "font-family": "sans-serif", "font-size": 12},
            # Styling der Kopfzeile
            style_header={"position": "sticky", "top": -1},
            # Sorgt dafür, dass wir nach den einzelnen Spalten sortieren können
            sort_action="native",
            # Sorgt dafür, dass man die Tabelle herunterladen kann
            export_format="csv",
            # Allgemeines Styling der Tabelle
            style_table={'max-height': '70vh', "width": "100%", 'overflowX': 'auto'})],
            className="DivTable")
    ],
    className="OberesDiv"),
    html.Div([
    html.Div([
        html.H2("Anzahl Publikationen für ausgewählten Zeitraum / Sprache"),
        # Hier wird der Bar Plot eingefügt
        dcc.Graph(id="bar_plot")], className="DivBar"),
    html.Div([
        html.H2("Anzahl Publikationen pro Ort für ausgewählten Zeitraum / Sprache"),
        # Hier wird der Pie Plot eingefügt
        dcc.Graph(id="pie_plot")], className="DivPie")],
        className="UnteresDiv"),
        ])


# -- Karte mit Dash verknüpfen
# Hier findet der eigentliche Prozess statt. Bisher haben wir nur definiert, wie unsere Seite aussehen soll. Jetzt kommt der interaktive Part dazu
# Dieser Callback sorgt dafür, dass man die Auswahl der Orte resetten kann, indem man auf irgendeine leere Stelle auf der Karte klickt
@app.callback(
    # Es gibt sogenannte click-Daten. Diese speichern bestimmte Informationen, je nachdem, wo man hinklickt. Wenn man z.B. auf den Punkt Paris klickt, werden in den click-Daten die Längen- und Breitengrade, der Name etc. von Paris gespeichert
    # Das machen wir uns jetzt zunutze. Im zweiten Callback verwenden wir die Click-Daten nämlich, um in der Tabelle nur die Texte anzuzeigen, die in dem Land entstanden sind, auf das gerade geklickt wurde
    # Um die so getroffene Auswahl zu resetten, wollen wir, dass click-Data wieder geleert wird.
    [Output(component_id="world_map", component_property="clickData")],
    [Input(component_id="map-Container", component_property="n_clicks")],
)
def reset_clickData(n_clicks):
    # Um die Auswahl zu resetten, geben wir einfach gar nichts zurück, sobald irgendwo hingeklickt wird, wo kein Ort ist
    return [None]

# Dieser Callback macht die eigentliche Arbeit und ist für das Filtern der Daten, das Anzeigen der Karte und die Übergabe der gefilterten Daten an Karte und Tabelle zuständig
@app.callback(
    # Erstmal haben wir hier unsere Outputs - wir wollen den Filter auf zwei Komponenten anwenden: Die Karte (world_map) und die Tabelle (tabelle)
    # Für die Karte und den Bar-Plot wollen wir natürlich eine Figure zurückgeben (component_property="figure")
    [Output(component_id="world_map", component_property="figure")],
    [Output(component_id="bar_plot", component_property="figure")],
    [Output(component_id="pie_plot", component_property="figure")],
    # Und die Tabelle benötigt lediglich Daten (component_property="data")
    [Output(component_id="tabelle", component_property="data")],
    # Nun haben wir für alle relevanten Parameter einen Input
    # Dieser Input enthält den aktuellen "Zustand" der Karte. Also wie weit reingezoomt wurde und welcher Längen- und Breitengrad gerade im Zentrum ist
    [Input(component_id="world_map", component_property="figure")],
    # Hier ist die Auswahl aus dem Dropdown für die Sprache enthalten
    [Input(component_id="auswahl_sprache", component_property="value")],
    # Hier sind die zwei Werte vom Slider für die Jahre enthalten
    [Input(component_id="auswahl_jahr", component_property="value")],
    # Hier sind die click-Daten enthalten, die ich zuvor schon kurz erklärt habe. Wir brauchen sie, um genau das zu tun, für das wir im vorigen Callback den Reset programmiert haben
    [Input(component_id="world_map", component_property="clickData")],
)
# In unsere Definition übergeben wir jetzt alle unsere Inputs
def update_data(original_figure, sprache, jahr, clickData):
    # Erstmal kopieren wir unser Dataframe, damit wir ein eigenes Dataframe für die Funktion haben
    dff = df.copy()
    # Nun geht es um den Filter für die Sprache
    # Wenn Sprache auf "Alle" eingeestellt ist, müssen wir nichts Filtern und das Dataframe (dff) bleibt einfach wie es ist (dff = dff)
    if sprache == "Alle":
        dff = dff
    # Wenn jedoch eine Sprache ausgewählt wurde, dann wollen wir, dass nur die Zeilen mit der entsprechenden Sprache in unserem Dataframe enthalten sins (dff = dff[dff["Sprache"] == sprache])
    else:
        dff = dff[dff["Sprache"] == sprache]

    # Nun wollen wir noch den Filter mit den Jahren anwenden. Dieser wird auf den Dataframe angewendet, der zuvor bei dem Filtern der Sprache rausgekommen ist
    # Wir nehmen uns nur die Zeilen, bei denen das Jahr größer/gleich des ersten/kleineren Wertes ist (dff["Jahr"] >= jahr[0]) und kleiner/gleich des zweiten/größeren Wertes ist (dff["Jahr"] <= jahr[1])
    dff = dff[(dff["Jahr"] >= jahr[0]) & (dff["Jahr"] <= jahr[1])]

    # Bevor wir uns nun um die Karte kümmern, bereiten wir zuerst die Tabelle vor. Dazu erstellen wir ein eigenes Dataframe für die Tabelle (dff_tabelle). Das müssen wir jetzt schon machen, weil wir das Dataframe für die Karte später verändern und Informationen verloren gehen, die in der Tabelle enthalten sein sollen
    dff_tabelle = dff
    # Jetzt geht es los mit den click-Daten. Wir wollen ja, dass die Nutzer*innen auf einen Erscheinungsort auf der Karte klicken können, und dann in der Tabelle nur die Einträge von dem entsprechenden Ort angezeigt werden
    # Wenn noch nirgends hingeklickt wurde, oder click-Data zurückgesetzt wurde (siehe erstes Callback), dann ist clickData = None und es ändert sich natürlich auch nichts und kein Ort ist ausgewählt
    if clickData == None:
        dff_tabelle = dff_tabelle
    # Wenn jedoch auf einen Ort geklickt wurde, haben wir Inhalt in unseren click-Daten
    # Jetzt wollen wir, dass unser Dataframe nur die Orte mit den Längen- und Breitengraden aus den click-Daten hat. Die Daten aus den click-Daten übergeben wir vor dem ==, die aus der Tabelle hinter dem == (die Daten aus der Tabelle müssen zuvor in ein Float geändert werden, da sie den gleichen Dateityp haben müssen, wie die Daten aus den click-Daten
    else:
        dff_tabelle = dff_tabelle[(clickData["points"][0]["lat"] == dff_tabelle["lat"].astype(float)) & (clickData["points"][0]["lon"] == dff_tabelle["lng"].astype(float))]
    # Nachdem wir unsere Daten für die Tabelle haben, wenden wir uns der Karte zu
    # Auf der Karte wollen wir keine Titel haben (das hat leider technisch doch nicht funktioniert, weil sich Punkte überlagert haben. Es gibt bereits seit zwei Jahren ein Issue auf Github, aber noch keine Lösung für das Problem)
    # Stattdessen wollen wir, ähnlich wie bei der animierten Karte, einfach zeigen, wo publiziert wurde und wie viel. Dafür summieren wir hier die identischen Zeilen (bzgl. Ort, lat und lng) auf und erhalten so die Anzahl der Publikationen für einen Ort für die eingestellten Filter. Diese Information fügen wir zu unserem Dataframe hinzu
    dff2 = dff.copy()
    dff2 = dff2.groupby(["Erscheinungsort", "lat", "lng", "Jahr"]).size().reset_index(name='Anzahl Publikationen')
    dff = dff.groupby(["Erscheinungsort", "lat", "lng"]).size().reset_index(name='Anzahl Publikationen')

    # Nun kann es sein, dass wir die Filter so gesetzt haben, dass es keine Einträge gibt. In diesem Fall wird eigentlich keine Karte angezeigt. Daher brauchen wir einen Workaround
    # Wenn in unserem Dataframe also nichts drinsteht, dann erstellen wir einen Eintrag. Ich habe jetzt einfach mal einen Eintrag mit lat und lng = 0.0 genommen
    if len(dff) == 0:
        dff["lat"] = [0.0]
        dff["lng"] = [0.0]
        # Mit dem so gefüllten Dataframe machen wir ganz normal unsere Karte (mit plotly express scatter_geo
        fig = px.scatter_geo(
            dff, lat="lat", lon="lng", projection="natural earth",
            hover_data={"lat": False, "lng": False, }, labels=dict(x="Erscheinungsort")

        )
        # Allerdings würde nun ein Punkt auftauchen, für den Wert (lat = 0.0, lng = 0.0), den wir hinzugefügt haben. Der soll aber nicht sichtbar sein. Er ist ja nur dazu da, damit überhaupt eine Karte angezeigt wird. Also machen wir ihn ganz klein (marker={"size": 0.0000001}) und sorgen dafür, dass auch beim Hovern nichts angezeigt wird (hovertemplate=None, hoverinfo="skip")
        fig.update_traces(marker={"size": 0.0000001}, hovertemplate=None, hoverinfo="skip")
    # Wenn die Filter so gewählt sind, dass in unserem Dataframe etwas enthalten ist, können wir unsere Map natürlich einfach erstellen
    else:
        # Hier erstellen wir also unsere Karte. Die einzelnen Einstellungen sind denke ich selbsterklärend
        fig = px.scatter_geo(
            dff, lat="lat", lon="lng", projection="natural earth", opacity=0.9, size_max=15,
            hover_data={"lat": False, "lng": False, "Erscheinungsort": True}, size="Anzahl Publikationen",
            color="Anzahl Publikationen", color_continuous_scale=px.colors.sequential.Burg)
        # Hier definieren wir die Daten, die später beim Hovern angezeigt werden sollen. dff["lat] ist nur ein Platzhalter - das nutzen wir nicht. Aber man muss aus einem mir nicht bekannten Grund auf jeden Fall zwei Werte hier übergeben
        fig.update_traces(customdata=np.stack((dff["Erscheinungsort"], dff["lat"]), axis=-1))
        # Jetzt wird das Hovertemplate eingerichtet und damit wird definiert, das beim drüberhovern erscheint
        fig.update_traces(hovertemplate='%{customdata[0]}<extra></extra>')
        # Hier stylen wir noch unsere Legende
        fig.update_layout(
            margin=dict(l=0, r=0, t=50, b=50),
            font=dict(size=10),
            font_family="sans-serif"

        )
        # Hier kümmern wir uns darum, dass die Karte an genau der Stelle bleibt, an der sie war, bevor ein click-Event passiert ist. Ansonsten springt die Karte zurück in den Ausgangsmodus, wenn irgendwo auf die Karte gklickt wird. Das wollen wir natürlich vermeiden
        if 'layout' in original_figure:
            fig.update_geos(original_figure['layout']['geo'])

    #Hier erstellen wir den Bar-Plot
    dff3 = dff2
    dff3 = dff3.groupby(["Jahr"])['Anzahl Publikationen'].sum().reset_index(name='Anzahl Publikationen')
    fig2 = px.bar(dff3, x="Jahr", y="Anzahl Publikationen", color_discrete_sequence=px.colors.qualitative.Pastel)
    # Auch hier wird werden wieder die Informationen für den Hover festgelegt
    fig2.update_traces(customdata=np.stack((dff3["Anzahl Publikationen"], dff3["Jahr"]), axis=-1))
    fig2.update_traces(hovertemplate='<b>Publikationen absolut: %{customdata[0]}</b><extra></extra>')
    # Hier wird festgelegt, dass jedes Jahr auf der X-Achse des Bar-Plots angezeigt werden soll
    fig2.update_xaxes(dtick="1")
    # Hier erstellen wir den Pie Plot
    dff_pie = dff2
    dff_pie = dff_pie.groupby(["Erscheinungsort"])['Anzahl Publikationen'].sum().reset_index(name='Anzahl Publikationen')
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

    # Zuletzt sortieren wir noch die Daten in unserer Tabelle nach Jahr
    dff_tabelle = dff_tabelle.sort_values("Jahr")
    # Und dann geben wir die Karte (fig), den Bar-Plot (fig2) und die Daten für die Tabelle (dff_tabelle.to_dict("records")) zurück
    return [fig, fig2, fig3, dff_tabelle.to_dict("records")]


# -- Und jetzt starten wir unsere App!
if __name__ == '__main__':
    app.run_server(debug=True)
