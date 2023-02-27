import numpy as np
import sys

sys.path.insert(0,"../scr/")
from get_data import _getdata
#import _getdata 

s=1980
e=1983
path="../scrap/"
output="2m_air"

_getdata(s,e,path)