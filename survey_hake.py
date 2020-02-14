#!/usr/bin/env python3

"""
Command line tool for setting up directory structure, converting .RAW files to netCDF .nc, plotting ping intervals, and generating  a .csvfile of Hake survey data.

example: python survey_hake.py /media/paulr/ncei_data/shimada/ sh1707

"""


import os
import sys
from datetime import datetime as dt
import xarray as xr
import matplotlib.pyplot as plt
import csv
import logging
from glob import glob
import numpy as np
import echopype

def main():  
   ### Organize files
   basedir = sys.argv[1]
   cruisename = sys.argv[2]
  
   ncsdir = os.path.join(basedir, cruisename, 'ek60_nc')
   errsdir = os.path.join(basedir, cruisename, 'ek60_convert_error')
   plotsdir = os.path.join(basedir, cruisename, 'ping_interval')

   ### Check if a data survey .csv file exists in the folder already, and, if not, create one.
   csvfile = os.path.join(basedir, cruisename, cruisename + '_summary.csv')
   if os.path.exists(csvfile) == False:
      with open(csvfile, 'w', newline='') as csvfiletowrite:
         csvwriter = csv.writer(csvfiletowrite, lineterminator='\n', delimiter=',')
         csvwriter.writerow(['File_name','Start_ping_time', 'End_ping_time', 'Pinging_interval', 'Sonar_freq', 'Sample_Interval', 'Transmit_duration', 'Transmit_power', 'Sound_speed', 'Absorption'])

   
   ### Iterate over all the nc files (AND error files), extract info for the survey (or generate 'NA' on error), write to csv, and log any errors along the way
   ncfiles = sorted(glob(os.path.join(ncsdir, '*[0-9].nc')))
   errFiles = sorted(glob(os.path.join(errsdir, '*')))
   ### Let's get the list of all timestamps on which to sort
   ncefiles = [ncfiles, errFiles]
   ncefiles_flat = [item for sublist in ncefiles for item in sublist]
   timestamps = []
   for ncefile in ncefiles_flat:
      timestamps.append(os.path.basename(ncefile).split('.')[0].split('-error')[0])

   timestamps_sorted = sorted(timestamps)
   for timestamp in timestamps_sorted:
      try:
         if os.path.exists(os.path.join(ncsdir, timestamp + '.nc')):
            ncfile = os.path.join(ncsdir, timestamp + '.nc')
            print("Working on " + ncfile)
            filebase = os.path.basename(ncfile).split('.')[0]
            ncfile_beam = xr.open_dataset(ncfile, group = 'Beam')
            start_ping_time = ncfile_beam.ping_time.min().values
            end_ping_time = ncfile_beam.ping_time.max().values
            ### calc and plot ping intervals. 
            pings = ncfile_beam.ping_time.values
            ### First, let's just look at the intervals for any anomalies
            ping_ints = np.diff(pings)
            plt.plot(ping_ints)
            plt.ylabel('Ping Intervals (s)')
            plt.xlabel('Ping Interval Index')
            plt.title(ncfile)
            plt.savefig(os.path.join(plotsdir, (filebase + '_ping_diffs.png')), dpi=120)
            plt.close()
            ### If there are any significant 2nd order differences record their indicies
            pings_2nd = np.diff(np.diff(pings))
            pinging_interval = np.where(pings_2nd > np.timedelta64(100,'ms'))[0] + 2
            sonar_freq = ncfile_beam.frequency.values
            sample_interval = ncfile_beam.sample_interval.values
            transmit_duration = ncfile_beam.transmit_duration_nominal.values
            transmit_power = ncfile_beam.transmit_power.values
            ncfile_env = xr.open_dataset(ncfile, group = 'Environment')
            sound_speed = ncfile_env.sound_speed_indicative.values
            absorption = ncfile_env.absorption_indicative.values
      
            #TODO csvwriter puts carriage returns in the pinging_interval array. Suppress it!
            with open(csvfile, 'a', newline='') as csvfiletowrite:
               csvwriter = csv.writer(csvfiletowrite, lineterminator='\n', delimiter=',')
               csvwriter.writerow([os.path.join(ncsdir, timestamp + '.nc'), start_ping_time, end_ping_time, pinging_interval, sonar_freq, sample_interval, transmit_duration, transmit_power, sound_speed, absorption])
 
         elif os.path.exists(os.path.join(errsdir, timestamp + '-error-log.txt')):
            print("Working on " + errsdir, timestamp + '-error-log.txt')
            with open(csvfile, 'a', newline='') as csvfiletowrite:
               csvwriter = csv.writer(csvfiletowrite, lineterminator='\n', delimiter=',')
               csvwriter.writerow([os.path.join(errsdir, timestamp + '-error-log.txt'), 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA'])
          
         
      except Exception as e:
         for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler)
         
         logfilename = timestamp + 'survey-error-log.txt'
         logging.basicConfig(filename = os.path.join(basedir, cruisename, 'ek60_convert_error', logfilename), filemode='w', level=logging.WARNING)
         print('An error occurred: ' + str(e))
         logging.exception(str(e))
      




if __name__ == '__main__':
    main()
