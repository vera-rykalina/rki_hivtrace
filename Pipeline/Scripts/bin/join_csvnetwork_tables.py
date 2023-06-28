#!/usr/bin/env python3

# Import libraries
import sys
import pandas as pd

# Create a list of dfs
dfs = []

for infilename in sys.args[1:]:
    newcolname = infilename.rsplit("/")[-1]
    dfs.append(pd.read_csv(infilename, sep = ",", index_col = False))

# Rename column name to be the file name
for df in dfs:
    df = df.rename(columns={"ClusterID":"newcolname"})

df = dfs[0]
for df_ in dfs[1:]:
    df = df.merge(df_, on = "SequenceID", how = "inner")

# Create clean output csv
df.to_csv = ("joined_csvnetwork_tables" + ".csv", sep = ",", index = False, encoding = "utf-8")
