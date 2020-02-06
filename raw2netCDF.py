#!/usr/bin/env python3

"""
Command line tool for setting up directory structure and converting .RAW files to netCDF .nc
NOTE: .raw files must be in a folder called 'ek60_raw', just below the cruise directory (e.g., x.../shimada/sh1701/ek60_raw)

example: python raw2netCDF.py /media/paulr/ncei_data/shimada/ sh1707

"""


import os
import sys
from datetime import datetime as dt
import xarray as xr
import csv
import logging
from glob import glob
import echopype

def main():  
   ### Organize files
   basedir = sys.argv[1]
   cruisename = sys.argv[2]

   dirs = ['echogram', 'ek60_convert_error', 'ek60_nc', 'ping_interval', 'ship_track_01day', 'ship_track_10day']
   for subdir in dirs:
      try:
         os.mkdir(os.path.join(basedir, cruisename, subdir))
      except OSError as error:
         print(error)

   rawfiles = sorted(glob(os.path.join(basedir, cruisename, 'ek60_raw', '*raw')))
   ncsdir = os.path.join(basedir, cruisename, 'ek60_nc')
   ### Iterate over all the .RAW files and convert them.
   for rfile in rawfiles:
      try:
         if not os.path.exists(os.path.join(ncsdir, os.path.basename(rfile).split('.')[0] + '.nc')):
            tmp = echopype.convert.ConvertEK60(rfile)
            tmp.raw2nc()
            ### the above may output multiple files in the case of parameter changes
            ncs_created = glob(rfile.split('.')[0]+ '*.nc')
            ### move .nc(s) from ek60_raw to ek60_nc
            for nc in ncs_created:
               os.rename(os.path.join(os.path.dirname(rfile), nc), os.path.join(ncsdir, nc))

            del tmp
         else:
            print(rfile + " has been converted already. Skipping...")       

      except Exception as e:
         for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler)

         logfilename = os.path.basename(rfile).split('.')[0] + '-error-log.txt'
         logging.basicConfig(filename = os.path.join(basedir, cruisename, 'ek60_convert_error', logfilename), filemode='w', level=logging.WARNING)
         print('An error occurred: ' + str(e))
         logging.exception(rfile + "  Conversion Error")  




if __name__ == '__main__':
    main()
