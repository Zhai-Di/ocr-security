import pandas as pd


df_all = pd.read_csv("../data/eth_usd_observations.csv")
df_full_lists = df_all[df_all["obs_len"] == 31].copy().reset_index(drop=True)
file_full_lists = pd.read_csv("../data/eth_usd_full_lists.csv")
is_identical = df_full_lists.equals(file_full_lists)
if is_identical:
    print("eth_usd_full_lists.csv is the result obtained after filtering out the complete lists.")
else:
    print("eth_usd_full_lists.csv is not the result obtained after filtering out the complete lists.")