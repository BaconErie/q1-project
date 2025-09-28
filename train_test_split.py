import pandas as pd, numpy as np, matplotlib.pyplot as plt, random
from sklearn.model_selection import train_test_split


file_name = "output_tsunami_logtransformed_discretized_droppednoneq_addedepmag_dropleakage&ids_dropextmissing_repmissing.csv"

df = pd.read_csv(file_name, quotechar='"')
df_elevation = pd.read_csv("elevation_data.csv")
df = df.merge(
    df_elevation[["latitude", "longitude", "elevation"]],
    on=["latitude", "longitude"],
    how="left"
)

x = df.drop(columns=["logrunupHt"])
y = df['logrunupHt']

x_train, x_test, y_train, y_test = train_test_split(x, y, random_state=42, test_size=0.2, stratify=y)

full_train = x_train.copy(); full_train['logrunupHt'] = y_train
full_test = x_test.copy(); full_test['logrunupHt'] = y_test

print(full_train)
print(full_test)
print(sum(1 for i in full_train["logrunupHt"] if i == "s")/len(full_train), sum(1 for i in full_train["logrunupHt"] if i == "m")/len(full_train), sum(1 for i in full_train["logrunupHt"] if i == "l")/len(full_train))
print(sum(1 for i in full_test["logrunupHt"] if i == "s")/len(full_test), sum(1 for i in full_test["logrunupHt"] if i == "m")/len(full_test), sum(1 for i in full_test["logrunupHt"] if i == "l")/len(full_test))

full_train.to_csv("tsunami_train.csv", index=False)
full_test.to_csv("tsunami_test.csv", index=False)
