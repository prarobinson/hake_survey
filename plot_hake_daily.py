#!/usr/bin/env python3

"""
Command line tool for generating "daily" plots of Hake survey data.

NOTE: THIS SCRIPT ASSUMES THE FOLLOWING SUBDIRECTORIES (see raw2netCDF.py):
   .../shimada/[cruise]/ek60_raw/
                       /ek60_nc/
                       /echogram/
                       /ship_track_01day/
                       /ship_track_10day/

example usage: python plot_hake_daily.py [/path/to/data/basedir] D[YearMonthDay] 
example usage: python plot_hake_daily.py /media/paulr/ncei_data/shimada/sh1701/ D20170720

To generate a list of unique days in BASH:
   $ cd /media/paulr/ncei_data/shimada/sh1701/ek60_nc/
   $ days=(`ls | awk -F"-" '{print $2}' | sort | uniq`)
   $ cd ~/Programming/echopype

Then just wrap this in a loop:
   $ for day in ${days[*]}; do
   $   python plot_hake_daily.py /media/paulr/ncei_data/shimada/sh1701/ ${day}   
   $ done


This script will automagically determine if there are more than 10 files for a day and create a plot per 10 files, or all if fewer.
               
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

def main():
   basedir = sys.argv[1]
   path_to_files = os.path.join(basedir, 'ek60_nc')
   files_date = sys.argv[2]

   ###### Echograms
   ### must calibrate
   nc_files = sorted(glob(os.path.join(path_to_files, '*' + files_date + '*[0-9].nc')))
   for nc_file in nc_files:
      if os.path.exists(nc_file.split('.')[0] + '_Sv.nc'):
         print("Calibration already completed for" + nc_file)
      else:
         nc = ModelEK60(nc_file)
         nc.calibrate(save=True)
 
   Sv_files = sorted(glob(os.path.join(path_to_files, '*' + files_date + '*Sv.nc')))
   print("Plotting echograms...")
   for i in range(0, len(Sv_files), 10):
      Sv_chunk = Sv_files[i:i+10]
      lastfile = os.path.basename(Sv_chunk[-1]).split('-')[2].split('_')[0]
      pngname = os.path.join(basedir, 'echogram', os.path.basename(Sv_chunk[0]).split('_')[0] + '-' + lastfile + '-echo.png')
      Sv = xr.open_mfdataset(Sv_files[i:i+10], combine='by_coords')
      plt.figure(figsize=[11, 8.5])
      plt.subplot(3, 1, 1)
      Sv.Sv.sel(frequency=18000).plot(vmax=-40, vmin=-100, cmap='Spectral_r', x='ping_time')
      plt.gca().invert_yaxis()
      plt.title(files_date + '  (frequency=18000)')
      plt.subplot(3, 1, 2)
      Sv.Sv.sel(frequency=38000).plot(vmax=-40, vmin=-100, cmap='Spectral_r', x='ping_time')
      plt.gca().invert_yaxis()
      plt.title(files_date + '  (frequency=38000)')
      plt.subplot(3, 1, 3)
      Sv.Sv.sel(frequency=120000).plot(vmax=-40, vmin=-100, cmap='Spectral_r', x='ping_time')
      plt.gca().invert_yaxis()
      plt.title(files_date + '  (frequency=120000)')
      plt.tight_layout() 
      plt.savefig(pngname, dpi=120)
      plt.clf()
      plt.close()
      gc.collect()
 

   ##### Ship tracks
   print("Plotting ship tracks for " + files_date)
   for i in range(0, len(nc_files), 10):
      nc_plat = xr.open_mfdataset(nc_files, group='Platform', concat_dim='location_time')
      dx = dy = 0.25
      extent = [nc_plat.longitude.values.min() - dx, nc_plat.longitude.values.max() + dx, nc_plat.latitude.values.min() - dy, nc_plat.latitude.values.max() + dy]
      nc_plat.close() 
      ### constrain extent to West Coast lat/lons in case lat/long values are missing, improperly set, or otherwise suspect
      if extent[0] <= -135:
         extent[0] = -135    

      if extent[1] >= -117:
         extent[1] = -117   

      if extent[2] <= 25:
         extent[2] = 25   

      if extent[3] >= 70:
         extent[3] = 70 

      # City locations
      SanDiego = [32.7157, -117.1611]
      SanMiguelIsland = [34.0376, -120.3724]
      SanFrancisco = [37.7749, -122.4194]
      CapeMendocino = [40.4401, -124.4095]
      CapeBlanco = [42.8376, -124.5640]
      YaquinaHead = [44.6737, -124.0774]
      Astoria = [46.1879, -123.8313]
      NeahBay = [48.3681, -124.6250]
      
      plt.figure(figsize=[8.5, 11], tight_layout=True)

      ### Use PlateCarree projection (see https://scitools.org.uk/cartopy/docs/latest/crs/projections.html for details)
      ax = plt.axes(projection=ccrs.PlateCarree())
      ax.set_extent(extent, crs=ccrs.PlateCarree())
      ax.coastlines(resolution='50m')
      #ax.add_feature(cartopy.feature.OCEAN)
      add_etopo2(extent, ax)

      gl = ax.gridlines(crs=ccrs.PlateCarree(), linewidth=1, color='black', alpha=0.2, linestyle='-', draw_labels=True)
      gl.xlabels_top = False
      gl.ylabels_right= False
      gl.xlabel_style = {'rotation': 45}
      gl.xformatter = LONGITUDE_FORMATTER
      gl.yformatter = LATITUDE_FORMATTER
 
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

      ncs_chunk = nc_files[i:i+10]
      leglist = []
      for i in range(0, len(ncs_chunk)):
         ncs = xr.open_dataset(ncs_chunk[i], group='Platform')
         ax.plot(ncs.longitude.values, ncs.latitude.values, linewidth=3, color=color_list[i])
         leglist.append(os.path.basename(ncs_chunk[i]))

      if (extent[2] <= SanDiego[0] <= extent[3]) and (extent[0] <= SanDiego[1] <= extent[1]):
         tt_SanDiego = ax.plot(SanDiego[1], SanDiego[0], marker='o', color='k')
         tt_SanDiego = ax.text(x=SanDiego[1] + 0.03, y=SanDiego[0], s='San Diego', fontsize=18)

      if (extent[2] <= SanMiguelIsland[0] <= extent[3]) and (extent[0] <= SanMiguelIsland[1] <= extent[1]):
         tt_SanMiguelIsland = ax.plot(SanMiguelIsland[1], SanMiguelIsland[0], marker='o', color='k')
         tt_SanMiguelIsland = ax.text(x=SanMiguelIsland[1] + 0.03, y=SanMiguelIsland[0], s='San Miguel Island', fontsize=18)

      if (extent[2] <= SanFrancisco[0] <= extent[3]) and (extent[0] <= SanFrancisco[1] <= extent[1]):
         tt_SanFrancisco = ax.plot(SanFrancisco[1], SanFrancisco[0], marker='o', color='k')
         tt_SanFrancisco = ax.text(x=SanFrancisco[1] + 0.03, y=SanFrancisco[0], s='San Francisco', fontsize=18)

      if (extent[2] <= CapeMendocino[0] <= extent[3]) and (extent[0] <= CapeMendocino[1] <= extent[1]):
         tt_CapeMendocino = ax.plot(CapeMendocino[1], CapeMendocino[0], marker='o', color='k')
         tt_CapeMendocino = ax.text(x=CapeMendocino[1] + 0.03, y=CapeMendocino[0], s='Cape Mendocino', fontsize=18)

      if (extent[2] <= CapeBlanco[0] <= extent[3]) and (extent[0] <= CapeBlanco[1] <= extent[1]):
         tt_CapeBlanco = ax.plot(CapeBlanco[1], CapeBlanco[0], marker='o', color='k')
         tt_CapeBlanco = ax.text(x=CapeBlanco[1] + 0.03, y=CapeBlanco[0], s='Cape Blanco', fontsize=18)

      if (extent[2] <= YaquinaHead[0] <= extent[3]) and (extent[0] <= YaquinaHead[1] <= extent[1]):
         tt_YaquinaHead = ax.plot(YaquinaHead[1], YaquinaHead[0], marker='o', color='k')
         tt_YaquinaHead = ax.text(x=YaquinaHead[1] + 0.03, y=YaquinaHead[0], s='Yaquina Head', fontsize=18)

      if (extent[2] <= Astoria[0] <= extent[3]) and (extent[0] <= Astoria[1] <= extent[1]):
         tt_Astoria = ax.plot(Astoria[1], Astoria[0], marker='o', color='k')
         tt_Astoria = ax.text(x=Astoria[1] + 0.03, y=Astoria[0], s='Columbia River', fontsize=18)

      if (extent[2] <= NeahBay[0] <= extent[3]) and (extent[0] <= NeahBay[1] <= extent[1]):
          tt_NeahBay = ax.plot(NeahBay[1], NeahBay[0], marker='o', color='k')
          tt_NeahBay = ax.text(x=NeahBay[1] + 0.03, y=NeahBay[0], s='Neah Bay', fontsize=18)
      
      ax.legend(leglist, bbox_to_anchor=(.22, -.2), loc='upper left')
      lastfile = os.path.basename(ncs_chunk[-1]).split('-')[2].split('.')[0]
      pngname = os.path.join(basedir, 'ship_track_01day', os.path.basename(ncs_chunk[i]).split('.')[0] + '-' + lastfile + '_shiptrack.png')
      plt.title(os.path.basename(pngname))
      plt.tight_layout(pad=.25)
      print("Saving " + pngname)
      plt.savefig(pngname, dpi=120, bbox_inches='tight', pad_inches=.25)
      plt.clf() 
      plt.close()
      gc.collect()

if __name__ == '__main__':
    main()
