import xarray as xr
import pandas as pd
import glob
import os

data_dir = "/era5_weather/current/wind/"
out_dir = "/windstorm_identification/"
os.makedirs(out_dir, exist_ok=True)

file_list = sorted(glob.glob(os.path.join(data_dir, "*.nc")))

lat_min, lat_max = 41.0, 44.0
lon_min, lon_max = -73.5, -70.0

threshold = 10.0

all_data = []

for f in file_list:
    ds = xr.open_dataset(f)

    ds_sub = ds.sel(
        latitude=slice(lat_max, lat_min),
        longitude=slice(lon_min, lon_max)
    )

    wind = ds_sub["wind"]
    avg_wind = wind.mean(dim=("latitude", "longitude"))

    # Keep only Dec–Apr
    avg_wind = avg_wind.sel(
        time=avg_wind["time"].dt.month.isin([12, 1, 2, 3, 4])
    )
    df = avg_wind.to_dataframe(name="avg_wind").reset_index()
    df = df[df["avg_wind"] > threshold]

    df = df[["time", "avg_wind"]]

    all_data.append(df)

    ds.close()

if all_data:
    result = pd.concat(all_data).sort_values("time")

    out_csv = os.path.join(out_dir, "avg_wind_above_10ms.csv")
    result.to_csv(out_csv, index=False)

    print(f"Saved: {out_csv}")
else:
    print("No data above threshold.")
