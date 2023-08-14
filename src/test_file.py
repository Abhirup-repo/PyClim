
import xarray as xr
from netcdf_analysis import netcdf
import time
import numpy as np
from numba import jit
from scipy.stats import linregress,pearsonr
import matplotlib.pyplot as plt
from netcdf_analysis import netcdf

path="/Volumes/Outdrive/Pyclim_Data/"

ds1=xr.open_dataset(path+"2m_air1981.nc")
ds2=xr.open_dataset(path+"2m_air1982.nc")

da=ds1["air"].mean("time") - ds2["air"].mean("time")








#da._zonal_mean("air",ds1.lat,dim=4)


#data1=ds1['air'][0,0,:,:].values

#plt.plot(ds1.lat,data1.mean(axis=1))



#da=ds1.groupby('time.month').mean('time')
#corr=xr.corr(ds1,ds2)

# data1=ds1['air'][:,0,:,:].values
# data2=ds2['air'][:,0,:,:].values

# nt,nlot,nlon=data1.shape

# ts1=data1.reshape(nt,(nlot*nlon))
# ts2=data2.reshape(nt,(nlot*nlon))


# N=ts1.shape[1]
# st=time.time()
# #@jit()
# def corr(N,ts1,ts2):
#     corr=np.zeros(N)
#     corr[:]=np.nan
#     for i in range(N):
#         rp=pearsonr(ts1[:,i],ts2[:,i])
#         if rp[1] < 0.05:
#             corr[i]= r
#     return corr   


# correlation=corr(N,ts1,ts2)
# en=time.time()
# elapsed_time = en - st
# print('Execution time:', elapsed_time, 'seconds')

# lp=linregress(ts1[:,0],ts2[:,0])
# from sklearn.linear_model import LinearRegression
# x=ts1[:,0].reshape((-1,1))
# y=ts2[:,0]
# model = LinearRegression().fit(x,y)
