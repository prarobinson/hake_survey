**This repo hosts scripts that use [echopype](https://github.com/OSOceanAcoustics/echopype) to batch process echosounder files from the NWFSC hake survey.**



Typical workflow
---------------------------------

These scripts only assume you have some .raw files in a folder called ***ek60_raw*** just below the main cruise directory. Then, the following steps convert the .raw files to netCDF, generate a .csv file with one row per file, and create echograms and ship tracks:

1. raw2netCDF.py --  `python raw2netCDF.py /media/paul/ncei_data/shimada/ sh1707`
2. survey_hake.py --  `python survey_hake.py /media/paulr/ncei_data/shimada/ sh1707`
3. plot\_hake\_daily.py -- this just plots a single day, so you may wish to run it in a loop:
    ```
     for day in ${days[*]}; do
      python plot_hake_daily.py /media/paulr/ncei_data/shimada/sh1701/ ${day}
    done
    ```
4. plot\_hake\_10days.py -- this will do ten days per plot, but goes over the entire cruise `python plot_hake_10days.py /media/paulr/ncei_data/shimada/sh1701/`


The result of running the above will be a collection of new folders:
- ek60\_nc/ -- Contains all the converted netCDF files.
- ping_interval/ -- These are plots of the 1st difference in pinging\_interval, just to get a visual on any changes in this parameter.
- echogram/ -- echograms! These are daily, but if a day has more than 10 files' worth of data, then there are 10 files to a plot (plus remainders).
- ship\_track\_01day/ -- these plots show the ship's track for a day, also broken down into 10-file segments. 
- ship\_track\_10day/ -- and these are the entire cruise, broken into 10-_day_ chunks

