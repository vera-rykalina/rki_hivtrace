#!/usr/bin/env python3

# Import libraries
import pandas as pd
import sys


# Read dfs
for infilename in sys.argv[1:]:
    name = infilename.rsplit("/")[-1] # gives a file name name.csv
    list_of_substrings = name.split("_")
    if "SubA1" in list_of_substrings:
        f = open(infilename, "rb")
        ref_df = pd.read_excel(f, sheet_name="SubA1_all", index_col=False)
        f.close()
        ref_df = ref_df[["Scount", "Cluster-ID_KH"]]

    else:
        new_sample = infilename.rsplit("/")[-1].split("_")[0]
        ht_df = pd.read_csv(infilename, sep = ",", index_col=False)
        ht_df["Scount"] = ht_df["SequenceID"].str.extract("(\d{2}-\d{5})\|02022022", expand = True)
        # Swap columns to have "Scount" first
        ht_df = ht_df.iloc[:, [-1, 0] + list(range(1, ht_df.shape[1] - 1 ))]
        ht_df.drop(["SequenceID"], axis = 1, inplace = True)

# Extract only a cluster which associated with a new sample from csvnetwork df
sample = ht_df["Scount"].isin([new_sample])
print(ht_df[sample].dtypes)


for i, row in ht_df.iterrows():
    sample = ht_df["Scount"].isin([new_sample])
    if len(ht_df[sample]) == 0:
        ht_df = pd.DataFrame({"ClusterID": [0], "Scount": [new_sample]})
    elif row["Scount"] == new_sample:
        cluster = row["ClusterID"]
        ht_df = ht_df[ht_df["ClusterID"] == cluster]
        print(ht_df)

       

ht_groupped = ht_df.groupby(["ClusterID"]).agg({"Scount": list}).reset_index()
# Create clean output csv
ht_groupped.to_csv("cluster_" + new_sample + ".csv", sep = ",", index = False, encoding = "utf-8")