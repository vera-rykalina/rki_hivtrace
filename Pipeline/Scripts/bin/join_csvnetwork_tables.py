#!/usr/bin/env python3

# Import libraries
import pandas as pd
import sys

# Create a list of dfs and assign and a ref dataframe as a separate df
dfs = []
for infilename in sys.argv[1:]:
    name = infilename.rsplit("/")[-1] # gives a file name name.csv
    newcolname = infilename.rsplit("/")[-1].split("_")[0]
    list_of_substrings = name.split("_")
    if "SubA1" in list_of_substrings:
        f = open(infilename, "rb")
        df = pd.read_excel(f, sheet_name="SubA1_all", index_col=False)
        print(df)
        f.close()
    else:
        dfs.append(pd.read_csv(infilename, sep = ",", index_col=False))
        for df_ in dfs:
            # Create "Scount" columns bases on "ID|fakedate" (extract our internal ID)
            df_["Scount"] = df_["SequenceID"].str.extract("(\d{2}-\d{5})\|02022022", expand = True)
            # Remove a column
            #df_.drop(["SequenceID"], errors="ignore", axis=1, inplace=True)
            df_.rename({"ClusterID": newcolname}, axis = 1, inplace = True)
            df_ = df_[~df_["Scount"].isin([newcolname])]
            print(df_)


# Join each df in dfs to the SubA1_GesamtDatensatz_inklCluster.xlsx df
for df_ in dfs[0:]:
    # Remove a column
    df_.drop(["SequenceID"], errors="ignore", axis=1, inplace=True)
    df = df.merge(df_, on="Scount", how="left")
print(df)

# Replace empty cells with zeros
df.fillna(0, inplace=True, downcast="infer")

# Create clean output csv
df = df.to_csv("joined_csvnetwork_tables" + ".csv", sep = ",", index = False, encoding = "utf-8")




