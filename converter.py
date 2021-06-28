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
#NOTES: 
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



##############################################################################
##############################   CONVERT DATA   ##############################
##############################################################################

#here is the equivalent of '3D_main.py' for the data reformatting procedures
def convert(directory, df, mintime, maxtime):
    
    #consider not reading in the SI1145 at all. It's not needed
    
    #if QA is performed then we need not read all that data in again; simply
    #    read in the QA-ed dataframe, remove the flagged data points, and
    #    continue straight to preparation for data format conversion
    
    #saving a copies of the datetimeindex for mintime and maxtime (which 
    #    reference indices of the dataframe associated with an actual
    #    date/time now post-time_checker.py); this is so we can use them to
    #    clip the data at the end per the user-defined time frame
    start_time = df.time[mintime]
    end_time = df.time[maxtime]
    

    #since performing the data conversion requires that all data be read in,
    #    here we loop through
    #    each sensor's subfolder from the parental station folder, calling the
    #    appropriate reader.py function as we go. These data frames will be
    #    aligned by time and joined together into a single dataframe.
    
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
        print("There is more than 1 BMP folder in the parent folder. Combine your BMP folders, or remove one from the parent folder.")
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
        #    dataframes are read into this program. Parameters such as averaging and
        #    averaging window are specified in THIS program and given to the other
        #    program's function so that parameters in the other program do not override
        #    the ones used for THIS program
        
        if "bmp" in sensor.lower() or "bme" in sensor.lower():
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
            call_reader = reader.rain_gauge(full_path, wildcard)
        elif "vane" in sensor.lower() or "dir" in sensor.lower() or "direction" in sensor.lower():
            call_reader = reader.wind_vane(full_path, wildcard)
        elif "speed" in sensor.lower() or "spd" in sensor.lower() or "anemometer" in sensor.lower():
            call_reader = reader.anemometer(full_path, wildcard)
        else:
            print("Cannot determine sensor type in the given folder names. Consider the following naming convention...\n")
            print("'bmp' or 'bme' for the BMP180, BMP280, or BME sensors.")
            print("'htu21d' for the HTU21D sensor.")
            print("'mcp9808' for the MCP9808 sensor.")
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
        
        if sensor.lower() == "bmp180" or sensor.lower() == "bmp280" or sensor.lower() == "bmp" or sensor.lower() == "bme":
            #add sensor name to the all column names except for the 'time'
            #    column
            df_temp = df_temp.rename(columns={'temp_C':'%s_tempC' % sensor,
                                              'temp_F':'%s_tempF' % sensor})
            
        elif sensor.lower() == "htu21d":
            #add sensor name to the all column names except for the 'time'
            #    column
            df_temp = df_temp.rename(columns={'temp_C':'%s_tempC' % sensor,
                                              'rel_hum':'%s_relhum' % sensor,
                                              'temp_F':'%s_tempF' % sensor})
        
        elif sensor.lower() == "mcp9808":
            #add sensor name to the all column names except for the 'time'
            #    column
            df_temp = df_temp.rename(columns={'temp_C':'%s_tempC' % sensor,
                                              'temp_F':'%s_tempF' % sensor})
            
        else:
            #no other sensors share variable names so we don't need to add the
            #    sensor name in front of the rest of the variables
            pass
        
        
        #add the newly-read-in dataframe to the main exisiting dataframe; the
        #    parameters set here create the UNION of the merged datasets, so
        #    that no data is lost from either dataframe; this means that where
        #    there is no overlap, the values are simply NaNs
        df = df.join(df_temp.set_index('time'), on='time', how='outer', sort=True)
        
        #reset the indices so that they are in monotonically increasing order,
        #    beginning with zero
        df = df.set_index('time').sort_index().reset_index()
        
    ### END OF 'subfolder'/'sensor' LOOP ###
    
    
    
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
    #remove the, 'no_rain', all non-SI unit, altitude, and si1145
    df = df.drop(columns=['SLP_hPa', 'SLP_inHg', 'alt', 'htu21d_tempF',
                          'mcp9808_tempF', 'no_rain'])
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
    
    #check whether there are ANY data within the timeframe specified
    if df.notna().any().all() == True:
        pass
    else:
        raise ValueError("No data in the chosen time frame.")

    #


    return df
    


   
if __name__ == "__main__":
    convert()