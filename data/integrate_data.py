import pandas as pd
import numpy as np

df_runups = pd.read_csv("output_tsunami_runups.csv")

col = 'runupHt'
Q1 = df_runups[col].quantile(0.25)
Q3 = df_runups[col].quantile(0.75)
IQR = Q3 - Q1
lower_bound = Q1 - 1.5 * IQR
upper_bound = Q3 + 1.5 * IQR

df_runups = df_runups[(df_runups[col] >= lower_bound) & (df_runups[col] <= upper_bound)].copy()
df_runups = df_runups.dropna(subset=[col])
df_runups['logrunupHt'] = np.log(df_runups[col] + 1)
threshold = max(df_runups['logrunupHt'])/3
for index, instance in df_runups.iterrows(): 
    if instance['logrunupHt'] >= 0.0 and instance['logrunupHt'] < threshold:
        df_runups.loc[index, 'logrunupHt'] = "s"
    elif instance['logrunupHt'] >= threshold and instance['logrunupHt'] < 2*threshold:
        df_runups.loc[index, 'logrunupHt'] = "m"
    else: 
        df_runups.loc[index, 'logrunupHt'] = "l"

df_runups = df_runups.drop("runupHt", axis=1)

df_runups_linked_to_eq = df_runups
df_runups_linked_to_eq.insert(len(df_runups_linked_to_eq.columns)-1, "eqMagMb", [np.nan]*len(df_runups_linked_to_eq))
df_runups_linked_to_eq.insert(len(df_runups_linked_to_eq.columns)-1, "eqMagMl", [np.nan]*len(df_runups_linked_to_eq))
df_runups_linked_to_eq.insert(len(df_runups_linked_to_eq.columns)-1, "eqMagMs", [np.nan]*len(df_runups_linked_to_eq))
df_runups_linked_to_eq.insert(len(df_runups_linked_to_eq.columns)-1, "intensity", [np.nan]*len(df_runups_linked_to_eq))
df_runups_linked_to_eq.insert(len(df_runups_linked_to_eq.columns)-1, "eqDepth", [np.nan]*len(df_runups_linked_to_eq))

df_equakes = pd.read_csv("output_earthquakes.csv").set_index('id')
to_drop = []

for index, instance in df_runups_linked_to_eq.iterrows():
    if instance["earthquakeEventId"] in df_equakes.index and not pd.isna(instance['earthquakeEventId']):
        df_runups_linked_to_eq.loc[index, 'eqMagMb'] = df_equakes.loc[instance['earthquakeEventId'], 'eqMagMb']
        df_runups_linked_to_eq.loc[index, 'eqMagMl'] = df_equakes.loc[instance['earthquakeEventId'], 'eqMagMl']
        df_runups_linked_to_eq.loc[index, 'eqMagMs'] = df_equakes.loc[instance['earthquakeEventId'], 'eqMagMs']
        df_runups_linked_to_eq.loc[index, 'intensity'] = df_equakes.loc[instance['earthquakeEventId'], 'intensity']
        df_runups_linked_to_eq.loc[index, 'eqDepth'] = df_equakes.loc[instance['earthquakeEventId'], 'eqDepth']
    else: to_drop.append(index)

df_runups_linked_to_eq.drop(to_drop, inplace=True)
df_runups_linked_to_eq.to_csv("output_tsunami_logtransformed_discretized_droppednoneq_addedeqmag.csv", index=False)