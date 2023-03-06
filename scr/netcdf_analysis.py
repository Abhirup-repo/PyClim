"""
This file contains several functions to perform different kinds of analysis
on netcdf data.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import xarray as xr

import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER

class netcdf:
    def __init__(self,ds,changetime=False,start=2000,timecord=None):
        """We initialize the module

        Args:
            ds (xarray data): Here we pass the data opened by xarray.
            changetime (bool): Sometimes we need to format the datetime of the netcdf to make to suitable for xarray operation.
            Default is False.
        """

        self.ds=ds
        self.changetime=changetime
        self.start=start
        self.timecord=timecord

        if changetime ==True:
            timelen=len(self.ds[f"{timecord}"])
            end=start+int((timelen/12)-1)
            a="{}-01-01".format(start)  
            b="{}-12-01".format(end)
            a=pd.to_datetime(a)
            b=pd.to_datetime(b)
            user_date_range = pd.date_range(start=a,end=b,freq="MS")
            self.ds[f"{timecord}"]=user_date_range
            self.ds=self.ds.rename(name_dict={f"{timecord}":"time"})
    def _plotdata(data,lat,lon,central_longitude=180,figsize=(7.5,5.5),size=14,fontfamily=None,extent=None,cmap="jet",cextend="both",
                  clim=None,clevel=20,title=None,cbar_label=None,savefig=False,savefigpath=None,savefigname="fig",svformat=".png",dpi=300):
        """This function plots the netcdf file

        Args:
            figsize (tuple, optional): _description_. Defaults to (7.5,5.5).
            title (str, optional): set the title of the plot . Defaults to None.
            cbar_label (str, optional): set the label of the colorbar. Defaults to None.
            savefig (bool, optional): to save the figure. Defaults to False.
            savefigpath (str, optional): destination of the plot to save. Defaults to None.
            format(str,optional): The format of the plot to be saved. Defaults to .png
        """

        latitude=lat
        longitude=lon
        ticksize=size
        fontsize=size+2
        #data=self.ds.values
        if fontfamily==None:
            plt.rcParams["font.family"]="sans-serif"
        else:
            plt.rcParams["font.family"]=fontfamily

        if clim==None:
            lv=np.linspace(np.percentile(data,25),np.percentile(data,75),15)
        else:
            lv=np.linspace(clim[0],clim[1],clevel)
        
        fig, ax = plt.subplots(subplot_kw={'projection': ccrs.PlateCarree(central_longitude)},figsize=figsize)

        if extent ==None:
            ax.set_extent([min(longitude),max(longitude),min(latitude),max(latitude)],crs=ccrs.PlateCarree())
        if extent!=None:
            ax.set_extent(extent,crs=ccrs.PlateCarree())

        mm = ax.contourf(longitude,latitude,data,transform=ccrs.PlateCarree(),\
                 levels=lv,\
                 cmap=cmap,extend=cextend)

        ax.coastlines(resolution='110m')
        #ax.add_feature(cfeature.OCEAN.with_scale('110m'),zorder=2)
        ax.add_feature(cfeature.BORDERS.with_scale('50m'))
        ax.add_feature(cfeature.STATES)
        ax.add_feature(cfeature.LAND,zorder=2)
        gl = ax.gridlines(crs=ccrs.PlateCarree(), draw_labels=True,
                        linewidth=1, color='gray', alpha=0.5, linestyle='--')
        #gl.xlabels_top = False
        gl.top_labels = False
        gl.right_labels = False
        gl.xformatter = LONGITUDE_FORMATTER
        gl.yformatter = LATITUDE_FORMATTER

        im_ratio = data.shape[0]/data.shape[1]
        cb = plt.colorbar(mm, shrink=0.9, drawedges='True',pad=0.03,fraction=0.04*im_ratio,ticks=lv[::2],format="%3.1f")
        cb.ax.tick_params(size=10,labelsize=ticksize-2)
        if cbar_label!=None:
            cb.set_label(label=cbar_label,size=size-2)

        if title!=None:
            ax.set_title(title,fontsize=size)
        
        if savefig==True:
            
            #print("As the savefigname is not given, so it saves as fig")
            #plt.savefig(savefigpath+savefigname+svformat,dpi=dpi,bbox_inches="tight")
            plt.savefig(savefigpath+savefigname+svformat,dpi=dpi,bbox_inches="tight")
        plt.show()

## We plot the data using xarray inbuilt function
    def _plot_with_xarray(self,var,level=0,dim=3,timestamp=0,clim=None,levels=None,cmap='jet'):

        ds=self.ds
        if dim==3:
            da=ds[f"{var}"][timestamp,:,:]
        if dim==4:
            da=ds[f"{var}"][timestamp,level,:,:]
        if levels==None:
            levels=20
        plt.figure(figsize=(7.5,4.5),constrained_layout=True)
        ax = plt.axes(projection=ccrs.PlateCarree())
        ax.coastlines(resolution='110m') 
        ax.add_feature(cfeature.LAND,zorder=2)
        
        plot_kwargs={"orientation": "horizontal","fraction":0.12,
                     'pad':0.03,'aspect':40}
        if clim==None:
            da.plot(levels=30,\
                cbar_kwargs=plot_kwargs,robust=True,cmap=cmap)
        if clim !=None:
            da.plot(levels=30,vmin=clim[0],vmax=clim[1],
                cbar_kwargs=plot_kwargs,robust=True,cmap=cmap)
    
        plt.show()

    def _mon_climatology(self):
        " This code computes the monthly climatology of the dataset"
        return self.ds.groupby('time.month').mean('time')
    
    def _plot_monthly_climatology(self,var,level=0,dim=3,mon=0,clim=None,levels=None,cmap='jet'):
        " We plot the monthly climatology"
        dm=self._mon_climatology()
        if dim==3:
            da=dm[f"{var}"][mon-1,:,:]
        if dim==4:
            da=dm[f"{var}"][mon-1,level,:,:]
        
        if levels==None:
            levels=20
        months=["Jan","Feb","March","April","May","June","July","Aug","Sep","Oct","Nov","Dec"]
        plt.figure(figsize=(7.5,4.5),constrained_layout=True)
        ax = plt.axes(projection=ccrs.PlateCarree())
        ax.coastlines(resolution='110m') 
        ax.add_feature(cfeature.LAND,zorder=2)
        
        plot_kwargs={"orientation": "horizontal","fraction":0.12,
                     'pad':0.03,'aspect':40}
        if clim==None:
            da.plot(levels=30,\
                cbar_kwargs=plot_kwargs,robust=True,cmap=cmap)
        if clim !=None:
            da.plot(levels=30,vmin=clim[0],vmax=clim[1],
                cbar_kwargs=plot_kwargs,robust=True,cmap=cmap)

        ax.set_title("Monthly climatology of {} for month {}".format(var,months[mon-1]),fontsize=16)
        plt.show()


    def _monthly_anomaly (self):
        return self.ds.groupby('time.month') - self._mon_climatology()

    def _plot_monthly_anomaly(self,var,level=0,dim=3,timestamp=0,clim=None,levels=None,cmap='jet'):

        dm=self._monthly_anomaly()
        if dim==3:
            da=dm[f"{var}"][timestamp,:,:]
        if dim==4:
            da=dm[f"{var}"][timestamp,level,:,:]
        
        if levels==None:
            levels=20
        plt.figure(figsize=(7.5,4.5),constrained_layout=True)
        ax = plt.axes(projection=ccrs.PlateCarree())
        ax.coastlines(resolution='110m') 
        ax.add_feature(cfeature.LAND,zorder=2)
        
        plot_kwargs={"orientation": "horizontal","fraction":0.12,
                     'pad':0.03,'aspect':40}
        if clim==None:
            da.plot(levels=30,\
                cbar_kwargs=plot_kwargs,robust=True,cmap=cmap)
        if clim !=None:
            da.plot(levels=30,vmin=clim[0],vmax=clim[1],
                cbar_kwargs=plot_kwargs,robust=True,cmap=cmap)

        ax.set_title("Monthly anomaly of {}".format(var),fontsize=14)
        plt.show()






