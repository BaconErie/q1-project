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
df_runups['logrunupHt'] = np.log(df_runups[col] + 1)
count_nan = 0
threshold = max(df_runups['logrunupHt'])/3
for index, instance in df_runups.iterrows(): 
    if np.isnan(instance['logrunupHt']): 
        count_nan += 1; continue
    if instance['logrunupHt'] >= 0.0 and instance['logrunupHt'] < threshold:
        df_runups.loc[index, 'logrunupHt'] = "s"
    elif instance['logrunupHt'] >= threshold and instance['logrunupHt'] < 2*threshold:
        df_runups.loc[index, 'logrunupHt'] = "m"
    else: 
        df_runups.loc[index, 'logrunupHt'] = "l"
df_runups = df_runups.drop("runupHt", axis=1)
df_runups.to_csv("output_tsunami_logtransformed_discretized.csv", index=False)