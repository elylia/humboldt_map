import pandas as pd

df_lng_lat = pd.read_csv("../data.csv", sep=",")
df_metadaten = pd.read_csv("../Humboldt_Metadaten.csv", sep=";")


d = df_lng_lat.set_index("Erscheinungsort")["lat"].to_dict()
df_metadaten["lat"] = df_metadaten["Erscheinungsort"].map(d)

d = df_lng_lat.set_index("Erscheinungsort")["lng"].to_dict()
df_metadaten["lng"] = df_metadaten["Erscheinungsort"].map(d)

df_metadaten.to_csv(r"Humbold_Metadaten_lat_lng.csv")



print(df_metadaten["Sprache"].sort_values().unique())
print(df_metadaten["Jahr"].sort_values().unique())