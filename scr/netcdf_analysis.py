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
    def __init__(self,data,lat,lon,extent=None,fontfamily=None):
        """This is a class to analyze/plot netcdf file
        Args:
            data (array): provide the 2D array
            lat (array): latitude of the dataset
            lon (array): longitude of the dataset_
            cextend (str, optional): extension of the colorbar. Defaults to "both".
            cmap (str, optional): colormap of the contourf. Defaults to "jet".
            size (int, optional): size of the lables . Defaults to 14.
            extent (array, optional): extent of the map [lon1,lon2,lat1,lat2]. Defaults to None.
            clim (array, optional): colorbar limit (default 25/75 percentile). Defaults to None.
            ticks (int, optional): gap between the ticks in the colorbar. Defaults to None.
            fontfamily (str, optional): setting the font-family of the system
        """

        self.data=data
        self.lat=lat
        self.lon=lon
        self.extent=extent
        self.fontfamily=fontfamily
        
    def _plotdata(self,figsize=(7.5,5.5),size=14,cmap="jet",central_longitude=180,cextend="both",
                  clim=None,title=None,cbar_label=None,savefig=False,savefigpath=None,format=None):
        """This function plots the netcdf file

        Args:
            figsize (tuple, optional): _description_. Defaults to (7.5,5.5).
            title (str, optional): set the title of the plot . Defaults to None.
            cbar_label (str, optional): set the label of the colorbar. Defaults to None.
            savefig (bool, optional): to save the figure. Defaults to False.
            savefigpath (str, optional): destination of the plot to save. Defaults to None.
            format(str,optional): The format of the plot to be saved. Defaults to .png
        """

        latitude=self.lat
        longitude=self.lon
        ticksize=size
        fontsize=size+2

        if clim==None:
            lv=np.linspace(np.percentile(self.data,25),np.percentile(self.data,75),15)
        else:
            lv=clim
        
        fig, ax = plt.subplots(subplot_kw={'projection': ccrs.PlateCarree(central_longitude)},figsize=figsize)

        if self.extent ==None:
            ax.set_extent([min(longitude),max(longitude),min(latitude),max(latitude)],crs=ccrs.PlateCarree())
        if self.extent!=None:
            ax.set_extent(self.extent,crs=ccrs.PlateCarree())

        mm = ax.contourf(longitude,latitude,self.data,transform=ccrs.PlateCarree(),\
                 levels=lv,\
                 cmap=cmap,extend=cextend)

        ax.coastlines(resolution='110m')
        ax.add_feature(cfeature.OCEAN.with_scale('110m'),zorder=2)
        ax.add_feature(cfeature.BORDERS.with_scale('50m'))
        ax.add_feature(cfeature.STATES)
        gl = ax.gridlines(crs=ccrs.PlateCarree(), draw_labels=True,
                        linewidth=1, color='gray', alpha=0.5, linestyle='--')
        #gl.xlabels_top = False
        gl.top_labels = False
        gl.right_labels = False
        gl.xformatter = LONGITUDE_FORMATTER
        gl.yformatter = LATITUDE_FORMATTER

        im_ratio = self.data.shape[0]/self.data.shape[1]
        cb = plt.colorbar(mm, shrink=0.9, drawedges='True',pad=0.03,fraction=0.04*im_ratio,ticks=lv[::2],format="%3.1f")
        cb.ax.tick_params(size=10,labelsize=ticksize-2)
        if cbar_label!=None:
            cb.set_label(label=cbar_label,size=size-2)

        if title!=None:
            ax.set_title(title,fontsize=size)
        plt.show()

    def _plot_with_xarray(ds,clim=None,colormap=None,levels=None):

        if colormap==None:
            c="jet"
        else:
            c=colormap
        if levels==None:
            levels=20
        plt.figure(figsize=(7.5,4.5),constrained_layout=True)
        ax = plt.axes(projection=ccrs.PlateCarree(central_longitude=180))
        ax.coastlines(resolution='110m') 
        ax.add_feature(cfeature.LAND,zorder=2)
        
        plot_kwargs={"orientation": "horizontal","fraction":0.12,
                     'pad':0.03,'aspect':40}
        if clim==None:
            ds.plot(levels=30,\
                cbar_kwargs=plot_kwargs,robust=True)
        if clim !=None:
            ds.plot(levels=30,vmin=clim[0],vmax=clim[1],
                cbar_kwargs=plot_kwargs,robust=True)
    
        plt.show()











