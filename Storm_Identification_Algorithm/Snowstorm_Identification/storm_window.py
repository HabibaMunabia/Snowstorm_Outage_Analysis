#This script defines 48 h storm windows

import pandas as pd

# Input CSV with peak_time column
in_csv = "/shared/stormcenter/habiba/Eversource_Snowstorms/final/snowstorm_identification/output/snow_periods_historical.csv"

# Output CSV
out_csv = "/shared/stormcenter/habiba/Eversource_Snowstorms/final/snowstorm_identification/output/storm_windows_48h_historical.csv"

# Read input
df = pd.read_csv(in_csv)

# Ensure peak_time is datetime
df["snow_peak_time"] = pd.to_datetime(df["snow_peak_time"])

# Create 48-hour storm window
df["storm_start_time"] = df["snow_peak_time"] - pd.Timedelta(hours=24)
df["storm_end_time"]   = df["snow_peak_time"] + pd.Timedelta(hours=24)

# Create stormCode from storm_start_time (YYYYMMDDHHMM → integer)
df["stormCode"] = df["storm_start_time"].dt.strftime("%Y%m%d%H%M")


df["year"] = df["stormCode"].str[:4].astype(int)

df = df[
    (df["year"] >= 1978) &     # for current chage these to 2005 and 2023
    (df["year"] <= 2004)
].reset_index(drop=True)

df = df.drop(columns="year") 


# Keep ONLY required columns
out_df = df[["stormCode", "storm_start_time", "storm_end_time"]]

# Save
out_df.to_csv(out_csv, index=False)
print(f"Saved {len(out_df)} storms to: {out_csv}")
