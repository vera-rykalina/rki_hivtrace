#!/usr/bin/env python3

# Import libraries
import sys
import pandas as pd

# Create a list of dfs
dfs = []

for infilename in sys.argv[1:]:
    newcolname = infilename.rsplit("/")[-1].split("_")[0]
    print(newcolname)
    dfs.append(pd.read_csv(infilename, sep = ",", index_col = False))
    # Rename column names to have file names as column names
    for df in dfs:
        df.rename({"ClusterID": newcolname}, axis = 1, inplace = True)


df = dfs[0]
for df_ in dfs[1:]:
    df = df.merge(df_, on = "SequenceID", how = "inner")

# Create clean output csv
df = df.to_csv("joined_csvnetwork_tables" + ".csv", sep = ",", index = False, encoding = "utf-8")
