import pandas as pd
import os

input_csv = "/windstorm_identification/avg_wind_above_10ms.csv"
output_csv = "/windstorm_identification/wind_event_periods.csv"

df = pd.read_csv(input_csv)
df["time"] = pd.to_datetime(df["time"])

df = df.sort_values("time").reset_index(drop=True)
df["time_diff"] = df["time"].diff()

# Start a new event when the gap is greater than 24 hours
df["event_id"] = (df["time_diff"] > pd.Timedelta(hours=24)).cumsum()

events = []

for _, group in df.groupby("event_id"):
    # Find the peak hour in this cluster
    peak_idx = group["avg_wind"].idxmax()
    peak_row = group.loc[peak_idx]

    peak_time = peak_row["time"]

    start_time = peak_time - pd.Timedelta(hours=24)
    end_time = peak_time + pd.Timedelta(hours=24)

    storm_code = start_time.strftime("%Y%m%d%H%M")

    events.append({
        "stormCode": storm_code,
        "start_time": start_time,
        "end_time": end_time
    })

events_df = pd.DataFrame(events).sort_values("start_time")
events_df.to_csv(output_csv, index=False)
