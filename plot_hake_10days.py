#!/usr/bin/env python3

"""
10 day ship track plot
       
e.g., python plot_hake_10days.py /media/paulr/ncei_data/shimada/sh1701/
"""


import os
import sys
from datetime import datetime as dt
from glob import glob
import xarray as xr
import csv
import logging
from echopype.model.ek60 import ModelEK60
import matplotlib.pyplot as plt
import matplotlib.figure as figure
from topomaps import add_etopo2
import cartopy.crs as ccrs
import cartopy
import cartopy.feature as cfeature
from cartopy.mpl.gridliner import LATITUDE_FORMATTER, LONGITUDE_FORMATTER
import gc
import numpy as np


allncs = sorted(glob(os.path.join(sys.argv[1], "ek60_nc/*[0-9].nc")))

alldates = []

for i in range(0, len(allncs)):
    alldates.append(allncs[i].split('-')[-2])

uniqueDates = sorted(set(alldates))


dx = dy = 0.25

for i in range(0, len(uniqueDates), 10):
   ### just someplace from which to start
   extent = np.array([-124.74383666666667, -123.798, 43.99783333333333, 44.8765])
   tenDates = uniqueDates[i:i+10]
   print(tenDates)
   for date in tenDates:
      try:
         nc_files = [j for j in allncs if date in j]
         nc_plat = xr.open_mfdataset(nc_files, group='Platform', concat_dim='location_time')
         extent_new = [nc_plat.longitude.values.min() - dx, nc_plat.longitude.values.max() + dx, nc_plat.latitude.values.min() - dy, nc_plat.latitude.values.max() + dy]
         nc_plat.close()
         print(extent_new)
         for i in [0,2]:
            if extent_new[i] <= extent[i]:
               extent[i] = extent_new[i]
         for i in [1,3]:
            if extent_new[i] >= extent[i]:
               extent[i] = extent_new[i]

      except Exception as e:
         print('An error occurred: ' + str(e))
     
   
   ### constrain extent to West Coast lat/ons in case lat/long values are missing, improperly set, or otherwise suspect
   if extent[0] <= -135:
      extent[0] = -135    

   if extent[1] >= -117:
      extent[1] = -117   

   if extent[2] <= 32:
      extent[2] = 32    

   if extent[3] >= 49:
      extent[3] = 49 

   # City locations
   SanDiego = [32.7157, -117.1611]
   SanMiguelIsland = [34.0376, -120.3724]
   SanFrancisco = [37.7749, -122.4194]
   CapeMendocino = [40.4401, -124.4095]
   CapeBlanco = [42.8376, -124.5640]
   YaquinaHead = [44.6737, -124.0774]
   Astoria = [46.1879, -123.8313]
   NeahBay = [48.3681, -124.6250]
  

   plt.figure(figsize=[11, 8.5])
   ax = plt.axes(projection=ccrs.PlateCarree())
   ax.set_extent(extent, crs=ccrs.PlateCarree())
   ax.coastlines(resolution='50m')

   add_etopo2(extent, ax)

   gl = ax.gridlines(crs=ccrs.PlateCarree(), linewidth=1, color='black', alpha=0.2, linestyle='-', draw_labels=True)
   gl.xlabels_top = False
   gl.ylabels_right= False
   gl.xlabel_style = {'rotation': 45}
   gl.xformatter = LONGITUDE_FORMATTER
   gl.yformatter = LATITUDE_FORMATTER

   ### different color every day
   color_list = [
         "#A6CEE3",
         "#1F78B4",
         "#B2DF8A",
         "#33A02C",
         "#FB9A99",
         "#E31A1C",
         "#FDBF6F",
         "#FF7F00",
         "#CAB2D6",
         "#6A3D9A"
   ]

   leglist = []
   i =0
  
   for date in tenDates:
      try:
         nc_files = [i for i in allncs if date in i]
         ncs = xr.open_mfdataset(nc_files, group='Platform', concat_dim='location_time')
         ax.plot(ncs.longitude.values, ncs.latitude.values, linewidth=3, color=color_list[i])
         leglist.append(date)
         i = i+1

      except Exception as e:
         print('An error occurred: ' + str(e))
     
      
   tt_SanDiego = ax.text(x=SanDiego[1], y=SanDiego[0], s='San Diego', fontsize=18)
   tt_SanMiguelIsland = ax.text(x=SanMiguelIsland[1], y=SanMiguelIsland[0], s='San Miguel Island', fontsize=18)
   tt_SanFrancisco = ax.text(x=SanFrancisco[1], y=SanFrancisco[0], s='San Francisco', fontsize=18)
   tt_CapeMendocino = ax.text(x=CapeMendocino[1], y=CapeMendocino[0], s='Cape Mendocino', fontsize=18)
   tt_CapeBlanco = ax.text(x=CapeBlanco[1], y=CapeBlanco[0], s='Cape Blanco', fontsize=18)
   tt_YaquinaHead = ax.text(x=YaquinaHead[1], y=YaquinaHead[0], s='Yaquina Head', fontsize=18)
   tt_Astoria = ax.text(x=Astoria[1], y=Astoria[0], s='Columbia River', fontsize=18)
   tt_NeahBay = ax.text(x=NeahBay[1], y=NeahBay[0], s='Neah Bay', fontsize=18)

   ax.legend(leglist, bbox_to_anchor=(1.05, 1), loc='upper left')
   pngname = os.path.join(sys.argv[1], 'ship_track_10day/') + tenDates[0] + "-" + tenDates[-1] + '_shiptrack.png'
   print("Saving " + pngname)
   plt.savefig(pngname, dpi=120)
   plt.clf() 
   plt.close()
   gc.collect()

