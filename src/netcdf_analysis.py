"""
This file contains several functions to perform different kinds of analysis
on netcdf data.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import xarray as xr
import matplotlib.patches as patches


import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER

class netcdf:
    def __init__(self,ds,changetime=False,timescale='monthly',start=2000,timecord="time"):
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

            if timescale=="monthly":
                timelen=len(self.ds[f"{timecord}"])
                end=start+int((timelen/12)-1)
                a="{}-01-01".format(start)  
                b="{}-12-01".format(end)
                a=pd.to_datetime(a)
                b=pd.to_datetime(b)
                user_date_range = pd.date_range(start=a,end=b,freq="MS")
                self.ds[f"{timecord}"]=user_date_range
                if self.timecord!="time":
                    self.ds=self.ds.rename(name_dict={f"{timecord}":"time"})

            if timescale=="daily":

                a="{}-01-01".format(start)
                endyear=start+int(len(self.ds[f"{timecord}"])/365)-1 
                b="{}-12-31".format(endyear)

                df=pd.DataFrame({"Date":pd.date_range(a,b,freq="D")})
                #df.set_index("Date",inplace=True)

                dg = df[~((df.Date.dt.month == 2) & (df.Date.dt.day == 29))]

                self.ds[f"{timecord}"]=dg.Date.values
                if self.timecord!="time":
                    self.ds=self.ds.rename(name_dict={f"{timecord}":"time"})


    def _datadetails(self):
        "This methods provide a comprehensive details of the data"
        print(self.ds)

    def _return_ds(self,pathname="./file.nc",save=False):
        """This method returns and saves the netcdf file.

        Args:
            pathname (str, optional):Provide the path and file name in this format. Defaults to "./file.nc".

        """
        if save==True:
            self.ds.to_netcdf(pathname)
        return self.ds

    def _plotdata(data,lat,lon,central_longitude=180,figsize=(7.5,5.5),size=14,
                  fontfamily="sans-serif",extent=None,cmap="jet",cextend="both",
                  clim=None,clevel=20,title=None,cbar_label=None,cbar_position="vertical",
                  savefig=False,savefigpath=None,savefigname="fig",
                  svformat=".png",dpi=300,nan=False,land=True):
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
        #if fontfamily==None:
        #    plt.rcParams["font.family"]="sans-serif"
        #else:
        plt.rcParams["font.family"]=fontfamily
        plt.rcParams["font.size"]=size
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
        if nan==True:
            if len(np.isnan(data))>=0:
                xmin, xmax = ax.get_xlim()
                ymin, ymax = ax.get_ylim()
                xy = (xmin,ymin)
                width = xmax - xmin
                height = ymax - ymin
                p = patches.Rectangle(xy, width, height, hatch='/', fill=None, zorder=-2)
                ax.add_patch(p)
        ax.coastlines(resolution='110m')
        #ax.add_feature(cfeature.OCEAN.with_scale('110m'),zorder=2)
        ax.add_feature(cfeature.BORDERS.with_scale('50m'))
        ax.add_feature(cfeature.STATES)
        if land==True:
            ax.add_feature(cfeature.LAND,zorder=2)
        gl = ax.gridlines(crs=ccrs.PlateCarree(), draw_labels=True,
                        linewidth=1, color='gray', alpha=0.5, linestyle='--')
        #gl.xlabels_top = False
        gl.top_labels = False
        gl.right_labels = False
        gl.xformatter = LONGITUDE_FORMATTER
        gl.yformatter = LATITUDE_FORMATTER

        im_ratio = data.shape[0]/data.shape[1]
        cb = plt.colorbar(mm, shrink=0.9,orientation=cbar_position, drawedges='True',pad=0.03,fraction=0.04*im_ratio,ticks=lv[::2],format="%3.1f")
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
    def _plot_with_xarray(self,var,level=0,dim=3,timestamp=0,clim=None,clevels=None,cmap='jet'):
        """By calling this method, one can plot the file for a particular date, pressure level

        Args:
            var (str): variable name
            level (int, optional): Pressure level. Defaults to 0.
            dim (int, optional): If the dataset has multiple levels then change dim=4. Defaults to 3.
            timestamp (int, optional): The time we want to visulize. Defaults to 0.
            clim (_type_, optional): colorbar limit, should be a list/array, e.g., [low,high]. Defaults to None.
            clevels (_type_, optional): No of levels in the colorbar. Defaults to None.
            cmap (str, optional): colormap. Defaults to 'jet'.
        """

        ds=self.ds
        if dim==3:
            da=ds[f"{var}"][timestamp,:,:]
        if dim==4:
            da=ds[f"{var}"][timestamp,level,:,:]
        if clevels==None:
            levels=20
        plt.figure(figsize=(7.5,4.5),constrained_layout=True)
        ax = plt.axes(projection=ccrs.PlateCarree())
        ax.coastlines(resolution='110m') 
        #ax.add_feature(cfeature.LAND,zorder=2)
        
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

    def _mean_seasonal_climatology(self,season="DJF"):
        
        ds=self._mon_climatology()
        if season=="DJF":
            season_data=ds.sel(month=ds.month.isin([12,1,2]))
        if season=="MAM":
            season_data=ds.sel(month=ds.month.isin([3,4,5]))
        if season=="JJA":
            season_data=ds.sel(month=ds.month.isin([6,7,8]))
        if season=="SON":
            season_data=ds.sel(month=ds.month.isin([9,10,11]))

        return season_data.mean('month')

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

    # def _daily_climatology(self):
    #     return self.ds.groupby('time.day').mean('time')   


    # def _daily_anomaly(self):
    #     return self.ds.groupby("time.day")-self._daily_climatology()



    def _daily_anomaly(self,var,lat,lon,lv=0,dim=3):

        ds=self.ds
        if dim==3:
            var=ds[f"{var}"][:,0,:,:].values
        
        if dim==4:
            var=ds[f"{var}"][:,lv,:,:].values
        nt,nlat,nlon=var.shape

        if nt%365==0:
            time=pd.DataFrame(ds.time,columns=["Date"])

            TimeSeries=var.reshape((nt,nlat*nlon), order='F')

            df=pd.DataFrame(TimeSeries,index=time["Date"])
            ts=df.values
            var_anomaly= np.zeros(ts.shape) # calculate the anomaly

            time_cycle=365
            for i in range(time_cycle):
                sample = ts[i::time_cycle, :]
                var_anomaly[i::time_cycle, :] = sample - sample.mean(axis=0)

            data=var_anomaly.reshape((ts.shape[0],nlat,nlon), order='F')
            ds_new= xr.Dataset({
                'variable': xr.DataArray(
                            data   = data,   # enter data here
                            dims   = ['time','lat','lon'],
                            coords = {'time': df.index.values,'lat':ds.lat,'lon':ds.lon},
                            attrs  = {
                                '_FillValue': -999.9,
                                'units'     : 'K'
                                }
                            ),})
            
            
            ds_new.rename(name_dict={"variable":f'{var}'})
        else:
            print('We use 365 days as a year to compute the anomaly')

        return ds_new
    def _annual_mean(self):
        """ Compute the annual mean """
        return self.ds.groupby('time.year').mean('time')

    def _plot_annual_mean(self,var,level=0,dim=3,convert="",clim=None,
                          clevels=None,cmap='jet',savefig=False,savefigpath="./",
                          savefigname="fig",svformat=".png",dpi=300):
        
        ds1=self._annual_mean()
        db=ds1.mean('year')

        if dim==3:
            da=db[f'{var}']

        if dim==4:
            da=db[f'{var}'][level,:,:]
        
        if convert=="m2mm":
            print("The unit is converted from m to mm")
            da=da*1000

        if clevels==None:
            levels=20
        plt.figure(figsize=(7.5,4.5),constrained_layout=True)
        ax = plt.axes(projection=ccrs.PlateCarree())
        ax.coastlines(resolution='110m') 
        #ax.add_feature(cfeature.LAND,zorder=2)
        
        plot_kwargs={"orientation": "horizontal","fraction":0.12,
                     'pad':0.03,'aspect':40}
        if clim==None:
            da.plot(levels=30,\
                cbar_kwargs=plot_kwargs,robust=True,cmap=cmap)
        if clim !=None:
            da.plot(levels=30,vmin=clim[0],vmax=clim[1],
                cbar_kwargs=plot_kwargs,robust=True,cmap=cmap)

        if savefig==True:
            plt.savefig(savefigpath+savefigname+svformat,bbox_inches="tight",dpi=dpi)

        plt.show()

    def _mean_annual_difference(self,ds1,var1,var2='',samedata=True,dim=3,level=0,
                                title="Mean annual difference",
                                savefig=False,savefigpath="./",savefigname="fig",
                                    svformat=".png",cmap="RdBu_r",dpi=300):
        
        ds=self._annual_mean()

        damon=ds.mean("year")
        dbmon=ds1.mean("year")
        if samedata==True:
            var2=var1
        
        if dim==4:
            diff=damon[f'{var1}'][level,:,:]-dbmon[f'{var2}'][level,:,:]

        else:
            diff=damon[f'{var1}']-dbmon[f'{var2}']
        plt.figure(figsize=(7.5,4.5),constrained_layout=True)
        ax = plt.axes(projection=ccrs.PlateCarree())
        ax.coastlines(resolution='110m') 
        #ax.add_feature(cfeature.LAND,zorder=2)

        plot_kwargs={"orientation": "horizontal","fraction":0.12,
                        'pad':0.03,'aspect':40}

        diff.plot(levels=30,\
                cbar_kwargs=plot_kwargs,robust=True,cmap=cmap)
        plt.title(title,fontsize=14)
        if savefig==True:
            plt.savefig(savefigpath+savefigname+svformat,bbox_inches="tight",dpi=dpi)

        plt.show()

    def _zonal_mean(self,var,lat,level=0,dim=3,savefig=False,savefigpath="./",savefigname="fig",svformat=".png",dpi=300):
        " This function computes the zonal mean"

        if dim==3:
            da=self.ds[f"{var}"][:,:,:].values
        if dim==4:
            da=self.ds[f"{var}"][:,level,:,:].values

        mean_time=da.mean(axis=0)
        lon_mean=mean_time.mean(axis=1)

        plt.figure(figsize=(5.5,3.5),constrained_layout=True)
        plt.plot(lat,lon_mean)
        plt.grid(linewidth=0.35)
        plt.title("Zonal mean of {}".format(var),fontsize=12)
        if savefig==True:
            plt.savefig(savefigpath+savefigname+svformat,bbox_inches="tight",dpi=dpi)

        plt.show()

    def _vertical_profile(self,var,latitude,longitude,plevel,latrange=[15,-15],exdata=None,savefig=False,savefigpath="./",savefigname="fig",svformat=".png",cmap="jet",dpi=300,title=None):

        
        d=self._annual_mean()

        _range=np.where((latitude<=latrange[0])&(latitude>=latrange[1]))[0]
        var_=d[f"{var}"]
        var_z=var_[:,:,_range[0]:_range[-1]+1,:]

        zonal_mean_time=var_z.mean(axis=0)

        zonal_mean=zonal_mean_time.mean(axis=1)
     
        plt.figure(figsize=(9.5,4.5))
        plt.contourf(longitude,plevel,zonal_mean,20,cmap=cmap)
        plt.gca().invert_yaxis()
        #plt.colorbar(label="CC")
        plt.colorbar()
        plt.xlabel(r"Longitude ($^{o}E$)",fontsize=14)
        plt.ylabel("Pressure levels (hPa)",fontsize=14)
        plt.tick_params(labelsize=12)
        if title ==None:
            plt.title(r"Vertcal profile of {} in lat range {}".format(var,latrange),fontsize=14)
        else:
            plt.title(f"{title}",fontsize=14)
        if savefig==True:
            plt.savefig(savefigpath+savefigname+svformat,bbox_inches="tight",dpi=dpi)

        plt.show()

    def _vertical_profile_from_data(data,var,latitude,longitude,plevel,latrange=[15,-15],
                                    savefig=False,savefigpath="./",savefigname="fig",
                                    svformat=".png",cmap="jet",dpi=300):

        d=data
        _range=np.where((latitude<=latrange[0])&(latitude>=latrange[1]))[0]
        var_=d[f"{var}"]
        var_z=var_[:,:,_range[0]:_range[-1]+1,:]

        zonal_mean_time=var_z.mean(axis=0)

        zonal_mean=zonal_mean_time.mean(axis=1)
     
        plt.figure(figsize=(9.5,4.5))
        plt.contourf(longitude,plevel,zonal_mean,20,cmap=cmap)
        plt.gca().invert_yaxis()
        #plt.colorbar(label="CC")
        plt.colorbar()
        plt.xlabel(r"Longitude ($^{o}E$)",fontsize=14)
        plt.ylabel("Pressure levels (hPa)",fontsize=14)
        plt.tick_params(labelsize=12)
        plt.title(r"Vertcal profile of {} in lat range {}".format(var,latrange),fontsize=14)
        if savefig==True:
            plt.savefig(savefigpath+savefigname+svformat,bbox_inches="tight",dpi=dpi)

        plt.show()
    
    #def _daily_anomaly(ds,var,level=0,dim=3):
        


