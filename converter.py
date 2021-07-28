#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May 17 15:16:55 2021

@author: blund
"""

###############################################################################
'''
           _____   _____     _     ____        ___    ___   _____
           |    \  |        / \    |   \       |  \  /  |   |
           |____/  |__     /___\   |    |      |   \/   |   |__
           | \     |      /     \  |    |      |        |   |
           |  \    |____ /       \ |___/       |        |   |____
'''

#This code reads data from the UCAR/NCAR COMET 3D-PAWS system and converts the
#    data to little_R format for WRFDA after some QC and decision-tree
#    processes
#
#Written by Brianna Lund
#
#Questions?
#Email me at blund@ucar.edu
#
#License:
#This code may be used and distributed freely, provided
#proper attribution is given to UCAR and the author.
#
#
#Requirements:
#    Python 3
#    Numpy
#    Glob
#    Pandas
#    Sys
#
#
#History:
#    May 17, 2021 - First Write
#
#
#Planned Features:
#    1. Adapt to the integration of QA-procedures (which adds columns with
#       data flags)
#
#
#How to Use:
#    1. 
#
#
#    
#
#NOTES: you must select a filepath in 3D_main.py (the 'directory' variable)
#       that has data for the time period chosen by 'mintime' and 'maxtime' in
#       3D_main.py. After that, even if no other sensor folder has data, the
#       program should run normally.
#       Even if other sensor folders (other than the first one read in as set
#       by 'directory' in 3D_main.py) do not have data for the selected
#       timeframe, BUT there is data in the sensor folder, the program will
#       function as normal. However, if there is zero data within any sensor
#       folder, the program will break and you should simply remove that
#       sensor folder from the parent folder.
#       If you have two BMP sensor folders (whether both have data or only one
#       has data), you must eliminate one folder, or combine data from both
#       folders into one BMP folder. Know that if you combine data into one
#       folder and there are any overlapping timestamps, the second set of
#       data read in with identical timestamps as the first set will be
#       discarded. This will depend on your file naming convention.
# ----------------------------------------------------------------------------



##############################################################################
#########################    IMPORTING MODULES    ############################
##############################################################################

import numpy as np
import pandas as pd
import sys
import os
import glob
import reader
from scipy import stats



##############################################################################
##############################   CONVERT DATA   ##############################
##############################################################################

#here is the equivalent of '3D_main.py' for the data reformatting procedures
def convert(sensor, directory, site_ID, elev, lat, lon, df, mintime, maxtime, save_dir):
    
    #if the sensor specified in 3D_main.py is any of the temperature or
    #    humidity sensors (i.e. the first sensor data read in) we must
    #    rename the necessary columns accordingly so they are properly dealt
    #    with below in the merge and purge sections
    if "bmp" in sensor.lower() or "bme" in sensor.lower() or "mcp" in sensor.lower() or "htu" in sensor.lower():
        if "bmp" in sensor.lower():
            sensor = "bmp"
        elif "bme" in sensor.lower():
            sensor = "bme"
            
        df = df.rename(columns={'temp_C':'%s_tempC' % sensor,
                                'temp_F':'%s_tempF' % sensor})
        if "htu" in sensor.lower() or "bme" in sensor.lower():
            df = df.rename(columns={'rel_hum':'%s_relhum' % sensor})

    
    #if QA is performed then we need not read all that data in again; simply
    #    read in the QA-ed dataframe, remove the flagged data points, and
    #    continue straight to preparation for data format conversion
    
    #saving copies of the datetimeindex for mintime and maxtime (which 
    #    reference indices of the dataframe associated with an actual
    #    date/time now post-time_checker.py); this is so we can use them to
    #    clip the data at the end per the user-defined time frame
    start_time = df.time[mintime]
    end_time = df.time[maxtime-1]
    

    #since performing the data conversion requires that all data be read in,
    #    here we loop through each sensor's subfolder from the parental
    #    station folder, calling the appropriate reader.py function as we go.
    #    These data frames will bemaligned by time and joined together into a
    #    single dataframe.
    
    #this is the parent/station directory; it should be only one level up from
    #    the directory given in '3D_main.py' for the 'directory' variable; the
    #    "...[:-1]" removes the trailing forward slash, allowing for the
    #    os.path.dirname to collect the folder path one level above
    parent_dir = os.path.dirname(directory[:-1])
    
    #collect all the folders within the parent/station folder 'parent_dir' and
    #    sort them
    folder_list = sorted(glob.glob(parent_dir + "/*"))
    
    #check to see if there is more than 1 'bmp' folder in the parent/station
    #    folder
    if len(['bmp' for folder in folder_list if 'bmp' in folder.lower()]) > 1:
        print("There is more than 1 BMP folder in the parent folder.\nCombine your BMP folders, or remove one from the parent folder.\nIf you combine them, know that if there are identical timestamps, the second set of duplicate timestamps read in will be discarded.\nWhich dataset gets discarded will depend on your file naming convention.")
        sys.exit()
        
    #remove the sensor folder that was already read in via '3D_main.py'
    folder_list.remove(directory[:-1])
    
    #initiate the sensor list
    sensor_list = []
    #collect the sensor name from each folder path in folder_list
    for folder in folder_list:
        sensor_list.append(folder[len(parent_dir)+1:]) 
        
    #check to see if there are the same number of sensor folders in the parent
    #    folder as there are sensors in the 'sensor_list'
    #NOTE: the odds of this condition ever arising should be next to none
    #    since the sensor_list is generated from the folder_list, but this
    #    checker is here just in case.
    if len(sensor_list) != len(folder_list):
        raise ValueError("Number of sensors is not equal to the number of folders.")
        
    else:
        pass

    
    #zip up the contents of the sensor and folder lists, so that each sensor
    #    name given by the 'sensor' variable is matched with its corresponding
    #    folder containing the data for said sensor (set by 'folder_list')
    tuple_lst = list(zip(folder_list,sensor_list))
    
    #need this because it is an input for the 'reader.py'
    wildcard = "*"
    
    #check/ensure that the order of file paths matches that of the
    #    sensor list?????
    #REPLY: don't need to check this with the current method I have because
    #    the sensor list is generated from the folder_list so by default, they
    #    they will be in the same
    
    #within the parent station folder, loop through each sensor's data folder
    for folder,sensor in tuple_lst:
        #quickly check whether or not the SI1145 sensor is the one set in
        #    3D_main.py; if it is, we remove those columns because we do not
        #    need them for Little_R
        if "vis" in df.columns:
            df = df.drop(columns=['vis', 'ir', 'uv', 'uvi'])
        
        #add a forward slash and wildcard character to the directory path
        full_path = folder + "/*"
           
            
        #--------------------------------------------------------------------#
        #-----------------------    READ IN FILE(S)   -----------------------#
        #--------------------------------------------------------------------#
        
        #call the appropriate function based on the sensor/variable name; need a bunch
        #    'if' statments here
        
        
        #read in the dataframe(s) by calling the function designed to read the data;
        #    this is pre-processed data being read in so any sorting, removal of
        #    duplicate timestamps, data conversions, etc. is done before these
        #    dataframes are read into this program.
        
        if "bmp" in sensor.lower():
            sensor = 'bmp'
            call_reader = reader.bmp(full_path, wildcard)
        elif "bme" in sensor.lower():
            sensor = 'bme'
            call_reader = reader.bmp(full_path, wildcard)
        elif "htu" in sensor.lower():
            sensor = "htu21d"
            call_reader = reader.htu21d(full_path, wildcard)
        elif "mcp" in sensor.lower():
            sensor = "mcp9808"
            call_reader = reader.mcp9808(full_path, wildcard)
        elif "1145"  in sensor.lower() or "radiation" in sensor.lower():
            print("Little_R does not require radiation data. Skipping SI1145 read...")
            pass #we don't use any SI1145 data for Little_R so just move along here
            #call_reader = reader.si1145(full_path, wildcard)
        elif "rain" in sensor.lower() or "tip" in sensor.lower() or "bucket" in sensor.lower() or "gauge" in sensor.lower():
            sensor = "rain"
            call_reader = reader.rain_gauge(full_path, wildcard)
        elif "vane" in sensor.lower() or "dir" in sensor.lower() or "direction" in sensor.lower():
            sensor = "wind_vane"
            call_reader = reader.wind_vane(full_path, wildcard)
        elif "speed" in sensor.lower() or "spd" in sensor.lower() or "anemometer" in sensor.lower():
            senso = "anemometer"
            call_reader = reader.anemometer(full_path, wildcard)
        else:
            print("Cannot determine sensor type in the given folder names. Consider the following naming convention...\n")
            print("'bmp' or 'bme' for the pressure sensors.")
            print("'htu21d' for the humidity sensor.")
            print("'mcp9808' for the temperature sensor.")
            print("'si1145' for the light / radiation sensor.")
            print("'rain' for the rain gauge / tipping bucket.")
            print("'winddir' for the wind vane")
            print("'windspd' for the anemometer.")
            print("Program exited...\n")
            sys.exit()
        
        #df = reader."%s"(directory, wildcard) % sensor
        df_temp = call_reader[0]
        missing_reports_times = call_reader[1]
        
        
        
        #--------------------------------------------------------------------#
        #----------------    ADJUST COLUMN NAMES & MERGE    -----------------#
        #--------------------------------------------------------------------#
        
        ''' For QA procedures requiring more than one sensor's dataset,
            consider how you might handle instances such that there is no data'''
        
        
        #change the column names to include the sensor name for the HTU, BMP,
        #    and MCP so that we can distinguish between the 3 temperatures
        #    and 2 humidities
        
        if "bmp" in sensor.lower() or "bme" in sensor.lower() or "mcp" in sensor.lower() or "htu" in sensor.lower():
            df_temp = df_temp.rename(columns={'temp_C':'%s_tempC' % sensor,
                                              'temp_F':'%s_tempF' % sensor})
            if "htu" in sensor.lower() or "bme" in sensor.lower():
                df_temp = df_temp.rename(columns={'rel_hum':'%s_relhum' % sensor})
            
        else:
            #no other sensors share variable names so we don't need to add the
            #    sensor name in front of the rest of the variables
            pass

        
        #add the newly-read-in dataframe to the main exisiting dataframe; the
        #    parameters set here create the UNION of the merged datasets, so
        #    that no data is lost from either dataframe; this means that where
        #    there is no overlap, the values are simply NaNs
        if "1145"  in sensor.lower() or "radiation" in sensor.lower():
            pass
        else:
            df = df.join(df_temp.set_index('time'), on='time', how='outer', sort=True)
        
        #reset the indices so that they are in monotonically increasing order,
        #    beginning with zero
        df = df.set_index('time').sort_index().reset_index()
        
    ### END OF 'subfolder'/'sensor' LOOP ###
    
    ''' Consider turning everything above this line into a function because
        the quality assurance procedure will also need this'''
        
        
    #check that every column you would expect to exist if the station had data
    #    for every single sensor does indeed exist; if it does not, create one
    #    and fill it with NaNs. Then you do not need a zillion 'if' statements
    #    or loops checking that a columns exists when you need to perform
    #    something on it if it does
    columns_lst = ['bmp_tempC','bmp_tempF','SLP_hPa','SLP_inHg','station_P',
                   'alt', 'htu21d_tempC','htu21d_tempF','htu21d_relhum',
                   'mcp9808_tempC','mcp9808_tempF','rain','no_rain','wind_dir',
                   'wind_speed']
    for col in columns_lst:
        if col not in df.columns:
            df[col] = np.empty(len(df)) * np.nan
    
    #------------------------------------------------------------------------#
    #---------------------    PURGING NON-ESSENTIALS    ---------------------#
    #------------------------------------------------------------------------#
    
    #here we remove extraneous columns from the dataframe (i.e those that are
    #    not used in Little_R format, or those that are simply duplicates in
    #    non-SI units), and clip the dataset by the 'mintime' and 'maxtime'
    #    set by the user, so that we are not performing calculations and other
    #    computationally expensive tasks on more data than is necessary
    
    #might want to check whether there are even any data in the parent folder
    #    otherwise, if there is no BMP data folder PERIOD, for example, then
    #    the 'drop' line will break the code
    
    #remove columns that we do not use/need for Little_R
    #NOTE: will need to have an exception for QA-ed data which will contain
    #      the SI1145 data
    #remove the, 'no_rain', all non-SI unit, altitude, and si1145
    df = df.drop(columns=['SLP_hPa', 'SLP_inHg', 'alt', 'no_rain'])

    #do something a little different here to account for possible BMP/BME
    #    naming differences
    for col in df.columns: #for each column name in the dataframe...
        if 'tempF' in col: #...if refers to temperature in Fahrenheit...
            df = df.drop(columns=col) #...discard that entire column from dataframe
        else: #...otherwise...
            pass #...keep it        
    
    #truncate/clip the dataset by the 'mintime' and 'maxtime' set by the user
    
    #Because not all sensors have the same amount of data, and the
    #    dataframe gets re-indexed to accommodate this fact, we must keep a
    #    record of the specific datetimeindices (not just the indices associated
    #    with those datetimeindices) associated with 'mintime' and 'maxtime'
    #    in order to accurately clip the dataset where intended by the
    #    user-defined 'mintime' and 'maxtime'
    #because the specific datetimeindices associated with mintime and maxtime
    #    for the first sensor read in will be accurate, simply save copies of
    #    the datetimeindices to new variable names using mintime and maxtime
    #    immediately after the first dataframe gets read in
    
    #truncate the dataframe based on the user-defined time frame; this
    #    conversion procedure takes place after all other procedures, so it is
    #    safe to redefine the dataframe ('df') with the clipped version of the
    #    dataframe
    df = df.set_index('time').loc[start_time:end_time].reset_index()
    #df = df.set_index('time').truncate(start_time:end_time)
    
    ''' There will ALWAYS be data somewhere in the timeframe because the reader
    programs for the first sensor read in require it '''
    # #check whether there are ANY data within the timeframe specified
    # if df.notna().any().all() == True:
    #     pass
    # else:
    #     raise ValueError("No data in the chosen time frame.")

    ''' WILL NEED TO ACCOUNT FOR LACK OF HTU AND INCLUSION OF BME IN THE FUTURE
        WHEN THERE ARE TWO STANDARD CONFIGURATIONS OF 3D-PAWS '''
        
    
    
    #------------------------------------------------------------------------#
    #-----------------    NEED ANY QUALITY ASSURANCE???    ------------------#
    #------------------------------------------------------------------------#
    
    ''' Need some QA in here if none is performed prior to this point '''
    
    #find the number of temperature columns in the dataframe (this could vary
    #    if, for example, there was no "bmp280" folder and subsequently, no
    #    bmp column for temperature)
    T_count = 0
    for col in df.columns:
        T_count += col.count('temp')
        
    #if there are any temperature sensors at all, then proceed
    
    #might need to account for whether QA was performed or not
    
    #will need to do some similar QA if an HTU and BME are present
    
    
    
    #first check if a value falls within an acceptable climatological range,
    #    if yes, then check if it is within the z-score threshold, if yes,
    #    then this value may be used for computing a mean temperature; if one
    #    or both conditions is not met, then the value is set to a NaN so that
    #    it does not get used for computing the mean temperature
    
    #how to account for missing bmp values that make the z-score for the two
    #    remaining temperatures equal to 1? Or the fact that the locations are
    #    based on a subset of the main dataframe, therefore, when applying to
    #    the whole dataframe, non-temp columns get affected?...
    
    #reassign temperatures that are outside the sensor specifications /
    #    climatological limits as NaNs; we use the sensor limits of the BMP
    #    because it has the lowest maximum acceptable temperature
    bmp_t_min = -40.
    bmp_t_max = 85.
    
    for col in df.columns[[x for x in range(len(df.columns)) if 'tempC' in df.columns[x]]]:
        df[col][df[col] < bmp_t_min] = np.nan
        df[col][df[col] > bmp_t_max] = np.nan
        
        
    #if the value spread is too large, eliminate all temperatures for further
    #    use
    for col in df[[x for x in df.columns if 'tempC' in x]].columns:
        for i in range(len(df[col])):
            if df[[x for x in df.columns if 'tempC' in x]].std(axis=1)[i] > 1.:
                df[col][i] = np.nan
    
    #compute the z-score for the temperatures only, but don't include NaNs
    #NOTE: this may break in the event of only one valid (non-NaN) temperature
    #      available for a given timestamp --> it turns that last
    z = np.abs(stats.zscore(df[[x for x in df.columns if 'tempC' in x]],axis=1, ddof=1, nan_policy='omit'))
    
    #these are the locations of values that exceed that maximum acceptable
    #    z-score value (i.e. outliers)
    locs = np.where(z > 1.1)
    
    #reassign the outliers as NaNs so they aren't used in computations
    for col in df[[x for x in df.columns if 'tempC' in x]].columns:
        for i in range(len(df[col])):
            if z[col][i] > 1.1:
                df[col][i] = np.nan
                
    ### This unfortunately does not work... ###
    # df = df.set_index('time')
    # df[z.columns].iloc[locs] = np.nan
    # df = df.reset_index()
    ###########################################
    
    #if even one temperature value exists...
    if T_count > 0:
        #...take the mean of any and all temperatures available for each
        #    timestamp and store them in a new 'tempC' column
        df['temp_C'] = df[[x for x in df.columns if 'tempC' in x]].mean(skipna=True, axis=1)
        
        #...then drop the original temperature columns
        df = df.drop(columns=[x for x in df.columns if 'tempC' in x])
    
    #check that pressure is within logical limits; may need to compare with
    #    MSLP, altitude (determined by GPS coordinates), and limits determined
    #    by 0 m AGL and 8900 m AGL (height of Mt. Everest)
    
    #check that RH is withing climatological limits
    df.htu21d_relhum[df.htu21d_relhum < 0.] = np.nan
    df.htu21d_relhum[df.htu21d_relhum > 100.] = np.nan
    
    #check that wind speed and direction are within logical limits
    df.wind_speed[df.wind_speed < 0.] = np.nan
    df.wind_dir[df.wind_dir < 0.] = np.nan
    df.wind_dir[df.wind_dir > 360.] = np.nan
        
    
    
    #------------------------------------------------------------------------#
    #-----------------    INTEGRATING OVER PRECIPITATION    -----------------#
    #------------------------------------------------------------------------#
    
    #integrate over a 1-hour period to get a cumulative sum of precipitation
    #    valid at the top of the hour, calculated from the previous 60 minutes
    #NOTE: the line below is a rolling sum so for each row/timestamp, there is
    #    a value calculated from the previous 60 minutes, but when ready, we
    #    will simply pluck the timestamps we need for the data conversion
    #    process from the dataframe, just like for all other variables.
    df['rain'] = pd.DataFrame(df.set_index('time').rain.rolling('60T').sum()).reset_index()['rain']
    
    
    
    #------------------------------------------------------------------------#
    #-----------------    COLLECTING HOURLY OBSERVATIONS    -----------------#
    #------------------------------------------------------------------------#
    ''' What to do in the event of not a full 24-hour period '''
    
    #we only need 1-hour observations, so remove all others from the dataset
    df = df[::60].set_index('time').reset_index()
    
    
    
    #------------------------------------------------------------------------#
    #--------------------------    COMPUTE MSLP    --------------------------#
    #------------------------------------------------------------------------#
    
    #mean sea-level pressure is computed from the station pressure, the
    #    user-input elevation and the QC-ed temperature data
    
    df['mslp'] = df.station_P*pow(1-(0.0065*elev)/(df.temp_C+0.0065*elev+273.15),-5.257)
    
    
    
    #------------------------------------------------------------------------#
    #----------------------    CONVERT TO SI UNITS    -----------------------#
    #------------------------------------------------------------------------#
    
    #little_R formate requires data fields to be in a particular set of units
    #    depending on the field; the following fields must be converted
    
    #station pressure and MSLP [hPa --> Pa]
    df.station_P *= 100.
    df.mslp *= 100.
    
    #temperature [C --> K]
    df.temp_C += 273.15
    
    #precipitation [mm --> cm]
    df.rain /= 10.
    
    
    #------------------------------------------------------------------------#
    
    #default missing values
    missing_val = -888888.00000
    missing_QC = -888888
    default_QC = 0
          
    #replace all NaNs within the dataset with the missing value flag (-888888.00000)
    df = df.where(df.notna(), other=missing_val)
    #df = df.fillna(missing_val)

    
    #loop through each row of the dataframe to generate the header, data,
    #    ending record, and tail integer lines from said row, then write it to
    #    a file
    for i in range(len(df)):
    
        #------------------------------------------------------------------------#
        #-----------------------------    HEADER    -----------------------------#
        #------------------------------------------------------------------------#
        
        #each station's file output (for which, but a single hourly record is
        #    written) will contain the crazy-long header line, followed by the
        #    data record line (there will only be one), followed by the
        #    ending-record line, followed by the 'tail integers' line (just 3
        #    integer fields indicating the number of valid fields for the
        #    observation, the number of errors, and the number of warnings,
        #    respectively); both the ending-record line and tail-integers lines
        #    are fairly meaningless, but required to achieve the appropriate
        #    data format
         
        #Latitude [float]; retrieve from 3D_main.py
        lat = lat
        #Longitude [float]; retrieve from 3D_main.py
        lon = lon
        #ID [string]; need only be human-readable for this obs type
        ID = '3D-PAWS'
        #Name [string]; retrieve from station name in 3D_main.py
        name = site_ID
        #Platform (FM‑Code) [string]; should remain constant for each station
        platform = 'FM-12 SYNOP'
        #Source [string]; should remain constant for each station; can be any text
        source = 'SOURCE'
        #Elevation [float]; retrieve from 3D_main.py
        elevation = elev
        #Valid fields [integer]; should remain constant for each station
        valid_fields = 1
        #Num. errors [integer]; should remain constant for each station
        num_errors = 0
        #Num. warnings [integer]; should remain constant for each station
        num_warnings = 0
        #Sequence number [integer]; *should* always be zero
        seq_num = 0
        #Num. duplicates [integer]; *should* always be zero because duplicates are removed
        num_dups = 0
        #Is sounding? [string]; should remain constant for each station
        is_sounding = 'F'
        #Is bogus? [string]; should remain constant for each station
        is_bogus = 'F'
        #Discard? [string]; should remain constant for each station
        to_discard = 'F'
        #Unix time [integer]; should remain constant for each station
        unix_time = missing_QC
        #Julian day [integer]; should remain constant for each station
        julian_day = missing_QC
        #Date [string]; retrieved from the dataframe, converted to a string, and removed of
        #    any whitespace, colons, and dashes
        date = str(df.time[i]).replace(" ","").replace(":","").replace("-","")
        #SLP [float; Pa], QC; retrieve from dataframe
        slp = df.mslp[i]
        slp_QC = default_QC
        #Ref Pressure [float; Pa], QC; should remain constant for each station; don't need
        ref_P = missing_val
        ref_P_QC = default_QC
        #Ground Temp [float; K], QC; should remain constant foe each station
        ground_T = missing_val
        ground_T_QC = default_QC
        #SST [float; K], QC; should remain constant for each station; don't need
        sst = missing_val
        sst_QC = default_QC
        #SFC Pressure [float; Pa], QC; should remain constant for each station; don't need
        sfc_P = missing_val
        sfc_P_QC = default_QC
        #Precip [float; cm], QC; retrieve from dataframe; don't need
        precip = df.rain[i]
        precip_QC = default_QC
        #Daily Max T [float; K], QC; should remain constant for each station; don't need
        max_T = missing_val
        max_T_QC = default_QC
        #Daily Min T [float; K], QC; should remain constant for each station; don't need
        day_min_T = missing_val
        day_min_T_QC = default_QC
        #Night Min T [float; K], QC; should remain constant for each station; don't need
        night_min_T = missing_val
        night_min_T_QC = default_QC
        #3hr Pres Change [float; Pa], QC; should remain constant for each station; don't need
        three_hr_P = missing_val
        three_hr_P_QC = default_QC
        #24hr Pres Change [float; Pa], QC; should remain constant for each station; don't need
        twofour_P = missing_val
        twofour_P_QC = default_QC
        #Cloud cover [float], QC; should remain constant for each station; don't need
        clouds = missing_val
        clouds_QC = default_QC
        #Ceiling [float; m], QC; should remain constant for each station; don't need
        ceiling = missing_val
        ceiling_QC = default_QC
        #Precipitable water [float; cm], QC; should remain constant for each station; don't need
        precip_W = missing_val
        precip_W_QC = default_QC
        
         
        #the formatted line containing the header fields
        header = "{:20.5f}{:20.5f}{:40s}{:>40s}{:>40s}{:>40s}{:20.5f}{:10d}{:10d}{:10d}{:10d}{:10d}{:>10s}{:>10s}{:>10s}{:10d}{:10d}{:>20s}{:13.5f}{:7d}{:13.5f}{:7d}{:13.5f}{:7d}{:13.5f}{:7d}{:13.5f}{:7d}{:13.5f}{:7d}{:13.5f}{:7d}{:13.5f}{:7d}{:13.5f}{:7d}{:13.5f}{:7d}{:13.5f}{:7d}{:13.5f}{:7d}{:13.5f}{:7d}{:13.5f}{:7d}".format(lat,lon,ID,name,platform,source,elevation,valid_fields,num_errors,num_warnings,seq_num,num_dups,is_sounding,is_bogus,to_discard,unix_time,julian_day,date,slp,slp_QC,ref_P,ref_P_QC,ground_T,ground_T_QC,sst,sst_QC,sfc_P,sfc_P_QC,precip,precip_QC,max_T,max_T_QC,day_min_T,day_min_T_QC,night_min_T,night_min_T_QC,three_hr_P,three_hr_P_QC,twofour_P,twofour_P_QC,clouds,clouds_QC,ceiling,ceiling_QC,precip_W,precip_W_QC)    
        header = header + '\n'
          
         
        #------------------------------------------------------------------------#
        #--------------------------    DATA RECORD    ---------------------------#
        #------------------------------------------------------------------------#
         
        #Pressure (Pa) QC
        pressure = df.station_P[i]
        press_QC = default_QC
        #Height (m) QC; should always be the same as the elevation of the stations
        height = elev
        height_QC = default_QC
        #Temperature (K) QC
        temperature = df.temp_C[i]
        temp_QC = default_QC
        #Dewpoint (K) QC	
        dewpoint = missing_val
        dewpoint_QC = default_QC
        #Wind speed (m/s) QC
        wind_speed = df.wind_speed[i]
        windspeed_QC = default_QC
        #Winddirection (deg) QC
        wind_dir = df.wind_dir[i]
        winddir_QC = default_QC
        #WindU (m/s) QC
        windU = missing_val
        windU_QC = default_QC
        #WindV (m/s) QC
        windV = missing_val
        windV_QC = default_QC
        #Relativehumidity (%) QC
        humidity = df.htu21d_relhum[i]
        humidity_QC = default_QC
        #Thickness (m) QC
        thickness = missing_val
        thickness_QC = default_QC
          
        #the formatted line containing the data fields
        data = "{:13.5f}{:7d}{:13.5f}{:7d}{:13.5f}{:7d}{:13.5f}{:7d}{:13.5f}{:7d}{:13.5f}{:7d}{:13.5f}{:7d}{:13.5f}{:7d}{:13.5f}{:7d}{:13.5f}{:7d}".format(pressure,press_QC,height,height_QC,temperature,temp_QC,dewpoint,dewpoint_QC,wind_speed,windspeed_QC,wind_dir,winddir_QC,windU,windU_QC,windV,windV_QC,humidity,humidity_QC,thickness,thickness_QC)
        data = data + "\n"
         
         
         
        #------------------------------------------------------------------------#
        #-------------------------    ENDING RECORD    --------------------------#
        #------------------------------------------------------------------------#
         
        #this line signifies the end of the data record and will go immediately
        #    below the last data record
         
        end_flag = -777777.00000
        
        end_record = "{:13.5f}{:7d}{:13.5f}{:7d}{:13.5f}{:7d}{:13.5f}{:7d}{:13.5f}{:7d}{:13.5f}{:7d}{:13.5f}{:7d}{:13.5f}{:7d}{:13.5f}{:7d}{:13.5f}{:7d}".format(end_flag,default_QC,end_flag,default_QC,missing_val,default_QC,missing_val,default_QC,missing_val,default_QC,missing_val,default_QC,missing_val,default_QC,missing_val,default_QC,missing_val,default_QC,missing_val,default_QC)
        end_record = end_record + "\n"
         
         
        #------------------------------------------------------------------------#
        #-------------------------    TAIL INTEGERS    --------------------------#
        #------------------------------------------------------------------------#
        
        #this is the 'tail integer' line that signifies the end of the entire
        #    observation
        tail_integers = "      1      0      0\n"
        
        
        
        #------------------------------------------------------------------------#
        #-------------------------    WRITE TO FILE    --------------------------#
        #------------------------------------------------------------------------#
        
        #the name of the file that will be created; this includes the directory
        #    in which the file(s) will be saved ('save_dir' from 3D_main.py); it
        #    includes the ID, name of the station, and the date/time in the file
        #    name; there is no file extension
        filename = "{}{}_{}_{}".format(save_dir,ID,name,date)
        
        #create the file by opening it in write mode; this means that previous
        #    files with this name will be completely overwritten
        #NOTE: because time is included in 'date' to the minute, there should be a
        #    single, uniquely-named file for each observation from every station
        file = open(filename, 'w')
        #write the header, the data, the ending record, and tail integers lines to
        #    the file, in that specific order!
        file.write(header + data + end_record + tail_integers)
        #close the file when finished
        file.close()
    
    
    ''' DON'T NEED TO RETURN THE DATAFRAME WITH THIS FUNCTION; HERE IT IS ONLY
        NECESSARY FOR EVALUATING THE PROCEDURES WITHIN'''
    #return df
    




   
if __name__ == "__main__":
    convert()