import xarray as xr
from netcdf_analysis import netcdf

import netcdf_analysis

Datapath="/Volumes/Abhirup_HD/PyclimData/"

ds=xr.open_dataset(Datapath+"2m_air_1980_2010.nc")

lat=ds.lat.values
lon=ds.lon.values

