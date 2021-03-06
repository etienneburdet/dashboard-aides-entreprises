import pandas as pd
# Load SIREN + Effectif
print("Load SIREN + Effectif")
df = pd.read_csv("../data/extracts/extract-siren.csv")
dfeff = pd.read_csv("../data/simu-effectifs/effectif.csv")
# Calculate delta effectif (nb + %)
print("Calculate delta effectif (nb + %)");
dfeff['delta_effectif'] = dfeff['effectif2'] - dfeff['effectif']
dfeff['delta_effectif_percent'] = dfeff['delta_effectif'] / dfeff['effectif']
dfeff['delta_effectif_percent'] = dfeff['delta_effectif_percent'].apply(lambda x: x if pd.notna(x) else 0)
dfeff.siret = dfeff.siret.astype(str)
df.siret = df.siret.astype(str)
# Get classe effectif (To change with real slots)
print("Get classe effectif (To change with real slots)")
dfeff['classe_effectif'] = dfeff['effectif'].apply(lambda x: '00' if x == 0 else '01' if x <= 2 else '02' if x <= 5 else '03' if x <= 9 else '11' if x <= 19 else '12' if x <= 49 else '21' if x <= 99 else '22' if x <= 199 else '31' if x <= 249 else '32' if x <= 499 else '41' if x <= 999 else '42' if x <= 1999 else '51' if x <= 4999 else '52' if x <= 9999 else '53')
dfeff = dfeff[['siret', 'delta_effectif', 'delta_effectif_percent', 'classe_effectif']]
# Merging Effectif + Siren
print("Merging Effectif + Siren")
dffinal = pd.merge(df, dfeff, on='siret', how='left')

dfstatfinal = pd.DataFrame({"dimension": [], "sous_dimension": [], "valeur_sous_dimension": [], "total_siret": [], "delta_effectif_total": [], "delta_effectif_percent_mean": []})

# Calculate Global Stat
print("Calculate Global Stat")
for dim in "reg","dep","codecommuneetablissement", "activiteprincipaleetablissement", "classe_effectif":
    print("For "+dim)
    dfstatcount = dffinal[[dim,'siret']].groupby([dim], as_index = False).count()
    dfstatcount = dfstatcount.rename(columns={"siret": "total_siret"})
    dfstatsum = dffinal[[dim,'delta_effectif']].groupby([dim], as_index = False).sum()
    dfstatsum = dfstatsum.rename(columns={"delta_effectif": "delta_effectif_total"})
    dfstatmean = dffinal[[dim,'delta_effectif_percent']].groupby([dim], as_index = False).mean()
    dfstatmean = dfstatmean.rename(columns={"delta_effectif_percent": "delta_effectif_percent_mean"})
    dfstat = pd.merge(dfstatcount,dfstatsum,on=dim,how='left')
    dfstat = pd.merge(dfstat, dfstatmean,on=dim,how='left')
    dfstat = dfstat.rename(columns={dim: "valeur_sous_dimension"})
    if((dim == "reg") | (dim == "dep") | (dim == "codecommuneetablissement")):
        dfstat['dimension'] = "geo"
    else:
        dfstat['dimension'] = dim
    dfstat['sous_dimension'] = dim
    dfstat = dfstat[['dimension','sous_dimension','valeur_sous_dimension','total_siret','delta_effectif_total','delta_effectif_percent_mean']]
    dfstatfinal = dfstatfinal.append(dfstat)

# Saving Csv
print("Saving CSV")
dfstatfinal.to_csv("../data/stats-global/stats-global.csv", index=False)