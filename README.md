This repo hosts scripts that use [echopype](https://github.com/OSOceanAcoustics/echopype) to batch process echosounder files from the NWFSC hake survey.
==========================================================

Typical workflow
---------------------------------

These scripts only assume you have some .raw files in a folder called *ek60_raw* just below the main cruise directory. Then, the following steps convert the .raw files to netCDF, generate a .csv file with one row per file, and create echograms and ship tracks:

1. raw2netCDF.py --  `python raw2netCDF.py /media/paul/ncei_data/shimada/ sh1707`
2. survey\_hake.py --  `python survey\_hake.py /media/paulr/ncei_data/shimada/ sh1707`
3. plot\_hake\_daily.py -- this just plots a single day, so you may wish to run it in a loop:
    ```
     for day in ${days[*]}; do
      python plot\_hake\_daily.py /media/paulr/ncei_data/shimada/sh1701/ ${day}
    done
    ```
4. plot\_hake\_10days.py -- this will do ten days per plot,but goes over the entire cruise `python plot_hake_10days.py /media/paulr/ncei_data/shimada/sh1701/`
