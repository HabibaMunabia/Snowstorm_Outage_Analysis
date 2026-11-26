import pandas as pd
import os

# Input files
wind_file = "/shared/stormcenter/habiba/Eversource_Snowstorms/final/windstorm_identification/wind_event_periods.csv"
snow_file = "/shared/stormcenter/habiba/Eversource_Snowstorms/final/snowstorm_identification/output/storm_windows_48h_current.csv"

# Output file
out_file = "/shared/stormcenter/habiba/Eversource_Snowstorms/final/windstorm_identification/pure_wind_events_48h_current.csv"

# Read files
wind_df = pd.read_csv(wind_file)
snow_df = pd.read_csv(snow_file)

# Convert times to datetime
wind_df["storm_start_time"] = pd.to_datetime(wind_df["start_time"])
wind_df["storm_end_time"] = pd.to_datetime(wind_df["end_time"])

snow_df["storm_start_time"] = pd.to_datetime(snow_df["storm_start_time"])
snow_df["storm_end_time"] = pd.to_datetime(snow_df["storm_end_time"])

pure_wind_events = []

for _, wind_row in wind_df.iterrows():
    wind_start = wind_row["storm_start_time"]
    wind_end = wind_row["storm_end_time"]

    # Check overlap with any snowstorm
    overlap = (
        (wind_start <= snow_df["storm_end_time"]) &
        (wind_end >= snow_df["storm_start_time"])
    ).any()

    # Keep only if no overlap
    if not overlap:
        pure_wind_events.append(wind_row)
# Convert back to DataFrame
pure_wind_df = pd.DataFrame(pure_wind_events)

# Remove helper/duplicate columns
pure_wind_df = pure_wind_df.drop(
    columns=["storm_start_time", "storm_end_time", "_wind_start", "_wind_end"],
    errors="ignore"
)

# Rename columns
pure_wind_df = pure_wind_df.rename(columns={
    "start_time": "storm_start_time",
    "end_time": "storm_end_time"
})

# Save output
pure_wind_df.to_csv(out_file, index=False)