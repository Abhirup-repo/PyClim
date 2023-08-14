"""
In this file, we  download the data using request package 
"""

import numpy as np
import requests
from tqdm import tqdm



#hgt_data_source=

def _getdata(ystart,yend,path=None,Outfilename=None):
    """We can retrive the climate data
    using request module.
    Args:
        ystart (int): starting year
        yend (int): ending year
        path (string): The path, where the data will be downloaded
        Outfilename (string): Name of the output file
    """

    for yr in tqdm(range(ystart,yend+1)):
        link="https://downloads.psl.noaa.gov/Datasets/ncep.reanalysis2/Dailies/pressure/hgt.{}.nc".format(yr)
        r=requests.get(link,allow_redirects=True)
        if Outfilename==None:
            outfile=str(yr)+"xx"
        if Outfilename!=None:
            outfile=Outfilename+str(yr)
        if path!=None:
            open(path+outfile+".nc",'wb').write(r.content)
        else:
            open(outfile+".nc",'wb').write(r.content)



_getdata(1990,1999,path="/Volumes/Abhirup_HD/CEN/Data/NOAA/Daily/Hgt/metadata/",Outfilename="hgt_")

