import pandas as pd, numpy as np

df_runups = pd.read_csv("output_tsunami_runups.csv")
df_runups['logrunupHt'] = np.log(df_runups['runupHt'] + 1)
for index, instance in df_runups.iterrows(): 
    if np.isnan(instance['logrunupHt']): continue
    if instance['logrunupHt'] >= 0.0 and instance['logrunupHt'] < 2.08796446:
        df_runups.loc[index, 'logrunupHt'] = "s"
    elif instance['logrunupHt'] >= 2.08796446 and instance['logrunupHt'] < 2*2.08796446:
        df_runups.loc[index, 'logrunupHt'] = "m"
    else: 
        df_runups.loc[index, 'logrunupHt'] = "l"
print((df_runups['logrunupHt'] == "l").sum())
df_runups.to_csv("output_tsunami_logtransformed_discretized.csv", index=False)