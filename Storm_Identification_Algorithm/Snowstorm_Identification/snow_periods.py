#This script identifies the snow periods for either historical or current weather following the algorithm.

import xarray as xr
import pandas as pd
import glob
import os

data_dir = "/era5_weather/historical/sn/"
out_csv  = "/snowstorm_identification/output/snow_periods_historical.csv"
os.makedirs(os.path.dirname(out_csv), exist_ok=True)
lat_min, lat_max = 41, 44.0
lon_min, lon_max = -73.5, -70.0

snow_var = "ETC_sn"
snow_thresh = 0.05       
grid_thresh = 80        
file_list = sorted(glob.glob(os.path.join(data_dir, "*.nc")))
print(f"Found {len(file_list)} files")

series_list = []

for f in file_list:
    print("Reading:", os.path.basename(f))
    ds = xr.open_dataset(f)

    # Ensure longitude is increasing (fixes many cases)
    if "longitude" in ds.coords:
        lon = ds["longitude"].values
        if lon[0] > lon[-1]:
            ds = ds.sortby("longitude")

    # subset region (latitude might be descending in your files, slice handles both if coords monotonic)
    ds_sub = ds.sel(
        latitude=slice(lat_max, lat_min),
        longitude=slice(lon_min, lon_max)
    )

    if snow_var not in ds_sub:
        ds.close()
        continue

    snow = ds_sub[snow_var]
    count_grids = (snow >= snow_thresh).sum(dim=("latitude", "longitude"))

    # to pandas series
    s = count_grids.to_series()
    s.index = pd.to_datetime(s.index)
    series_list.append(s)

    ds.close()

# concatenate and sort in time
if len(series_list) == 0:
    raise RuntimeError("No data found after reading/subsetting files.")

s_all = pd.concat(series_list).sort_index()

s_all = s_all.groupby(s_all.index).max().sort_index()

flag = s_all >= grid_thresh
group_id = flag.ne(flag.shift()).cumsum()

rows = []
for _, idx in flag.groupby(group_id).groups.items():
    if not flag.loc[idx].iloc[0]:
        continue

    start = flag.loc[idx].index[0]
    end   = flag.loc[idx].index[-1]
   
    # values within this period
    run_vals = s_all.loc[start:end]

    # peak time is the timestamp of the maximum grids in this period
    peak_time = run_vals.idxmax()
    peak_grids = int(run_vals.max())

    rows.append({
        "snow_start_time": start,
        "snow_end_time": end,
        "snow_peak_time": peak_time
    })

df = pd.DataFrame(rows).sort_values("snow_start_time")

#combine storms if storm1 end time-storm2 start time < 12 hours 
df = df.sort_values("snow_start_time").reset_index(drop=True)
window = pd.Timedelta(hours=12)

def finalize(start, end):
    peak_time = s_all.loc[start:end].idxmax()
    return {"snow_start_time": start, "snow_end_time": end, "snow_peak_time": peak_time}

merged = []
if not df.empty:
    start = pd.to_datetime(df.loc[0, "snow_start_time"])
    end   = pd.to_datetime(df.loc[0, "snow_end_time"])

    for i in range(1, len(df)):
        s2 = pd.to_datetime(df.loc[i, "snow_start_time"])
        e2 = pd.to_datetime(df.loc[i, "snow_end_time"])

        gap = s2 - end
        
        if gap <= window:
            end = max(end, e2)
        else:                                # close current, start new
            merged.append(finalize(start, end))
            start, end = s2, e2

    merged.append(finalize(start, end))

df = pd.DataFrame(merged)
# drop storms with duration of <3 hours 
df["snow_start_time"] = pd.to_datetime(df["snow_start_time"])
df["snow_end_time"]   = pd.to_datetime(df["snow_end_time"])

duration_hours = (df["snow_end_time"] - df["snow_start_time"]).dt.total_seconds() / 3600.0
df = df[duration_hours >= 3].reset_index(drop=True)

df.to_csv(out_csv, index=False)
print(f"Saved {len(df)} periods to: {out_csv}")
