#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun  4 16:05:12 2020

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

#This code reads data from the UCAR/NCAR COMET 3D-PAWS system and generates
#    plots on a weekly basis for either the whole dataset given, or within a
#    user-specified time frame.
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
#    Matplotlib
#    Glob
#    Pandas
#    Sys
#
#
#History:
#    August 19, 2020 - First Write
#
#
#Planned Features:
#    1. Create an instance of tkinter that opens a Finder/Explorer window when
#       the user runs the program for the user to select the folder where all
#       subfolder and data reside???
#    2. Use prompts for user input??? This will ensure the options are changed
#       when the program is run for any user, but could also be tedious to
#       have to enter those options every time; perhaps a parameter file is
#       better???
#    3. Add option to compute (and generate a file of) output statistics
#    4. Add ability/option to plot multiple variables on...
#           a)... same plot
#           b)... separate plots, but within same figure
#    5. Add additional automated plotting options...
#           a) daily - DONE!
#           b) monthly - DONE!
#           c) plot_all (plots all variables from the specified sensor; this
#              will mean that ALL figures get saved to the specified directory)
#    6. Consider expanding the "averaging" or smoothing option to also work
#       the wind vane
#    7. Add option for user to set their own y-axis limits (wind direction and 
#       relative humidity can/will be hard-coded)
#    8. Add error/input checker that ensures the averaging window is not
#       greater than or equal to the number of data points in the dataset
#    9. Create an exception to the existence of the 'averaged' variable such
#       that if it is entirely commmented out and does not exist, assume it is
#       False and move on
#    10.Add wind barb plotting ability (this will come with a whole set of 
#       specific conditions, two input directories, for sure)
#
#
#How to Use:
#    1. Setup your folder structure:
#        a) create a parent folder that will contain the subfolders for each
#           station you want to read in
#        b) each station folder should contain the subfolders for each sensor
#           you want to plot; it is critical that each sensor subfolder within
#           each station folder follow the same naming convention (e.g. 'bmp'
#           for the BMP180 or BMP280, 'winddir' for wind direction from the
#           wind vane, etc.)
#    2. Change all variables in "USER OPTIONS" section to desired input
#           sensor: bmp180, bmp280, htu21d, mcp9808, si1145, rain, anemometer, wind_vane
#           directory
#           save_dir
#           wildcard
#           site_ID
#           var_name: temp_C, temp_F, rel_hum, alt, SLP_hPa, SLP_inHg,
#                     station_P, vis, ir, uv, uvi (depends on sensor name)
#           units: mm, inches, mps, kmph, mph, kts (depends on sensor name)
#           averaged: True, static, resampled, False (simply uncomment the
#                     option you want to use)
#           mintime
#           maxtime
#           plot_opt: plotter (default), daily, weekly, monthly, "" (empty string; no plotting)
#           tag
#    3. Run with "python 3D_main.py" in terminal, or open in
#       Spyder and run from there.
#
#
#Example header from files --> no file header(s)!!! (this could change...)
#
#
#Example data from files:
#    
#
#NOTES: the y-axis range for most variables will be site-dependent. These are
#       currently hard-coded in the plotting section for each variable. If you
#       see no data with the first attempt to plot a variable, try commenting
#       out the following line in the 'plotter.py' program for the appropriate
#       varaible:
#
#       #set y-axis limits/range
#       ax.set_ylim(900., 1100.)
#
#       Set the y-axis limits according to your dataset
# ----------------------------------------------------------------------------
#       At the moment, this program reads in all data even if a subset of time
#       is requested for plotting, which is a bit of an overkill
# ----------------------------------------------------------------------------
#       Be mindful of the amount of data you are reading in, as well as your
#       'mintime' and 'maxtime' time frame limits, when using the daily
#       plotter; if reading in a 2-year long dataset with 'mintime' and
#       'maxtime' set to plot the whole thing (i.e. set to empty strings, ""),
#       you will have 730 plots being generated.
# ----------------------------------------------------------------------------
#       Regarding the daily plotter only, this function is setup to begin at
#       00:00 UTC
# ----------------------------------------------------------------------------
#       and 00:00 UTC of the first day of the
#       month for the monthly plotter



##############################################################################
#########################    IMPORTING MODULES    ############################
##############################################################################

import numpy as np
import pandas as pd
import sys
import glob
import reader
from input_checker import input_checker
from time_checker import time_checker
from data_smoother import smoothing
#import quality_assurance as QA
import plotter as pltr



##############################################################################
############################    USER OPTIONS    ##############################
##############################################################################

#set this to the name of the sensor from which you want to plot (NOT case
#    sensitive)
#sensor = "anemometer"

#set the 'directory' variable to the absolute path where your data are stored;
#    don't forget the trailing forward slash!
directory = "/Users/blund/Documents/3D-PAWS/lake_victoria/data/"

#sensor list should contain the names of the sensors you want to read in; you
#    must use only the valid options as defined in the "How to use:" section
#    above
#subfolder list should contain the names of the data folders within the parent
#    folder (defined by 'directory') with a trailing forward slash
#NOTE: it is critical that 'sensor_list' and 'subfolder_list' contain
#      precisely the same number of elements AND that the order of each is
#      preseved, meaning that if 'anemometer' is the first index of
#      'sensor_list', then 'windspd' should be the first index of 'subfolder_list'
sensor_list = ["anemometer","wind_vane","rain","mcp9808","bmp280","htu21d"]
subfolder_list = ["windspd/","winddir/","rain/","mcp9808/","bmp/","htu21d/"]

#specify the FULL file path to the directory in which to save your figures;
#    don't forget to include the trailing forward slash!
save_dir = "/Users/blund/Documents/3D-PAWS/_my_code/figures/si1145_testing/_monthly_ALL/ultraviolet/"

#set the wildcard option; to read in EVERY file within the directory you
#    specified above in 'directory', set 'wildcard' to "*"; you may specify
#    this to select a subset of data (e.g. "*2020*" to only read in files from
#    2020)
wildcard = "*"

#change this to the name of the site from which data are being plotted; this
#    will be used in the plot title as well as the name of the figure
site_ID = "GLOBE_21"

#change this to the name of the variable you want to plot; a list of
#    acceptable options can be found in the "How to Use:" section above
var_name = "uv"

#change this to the units you want to plot; a list of acceptable options can
#    be found in the "How to Use:" section above*
#NOTE: this only applies to wind speed and precipitation amount from the rain
#    gauge (tipping bucket)
units = "mps"

#plot raw data or averaged data; to plot running-averaged data, uncomment the
#    True option; to plot raw (un-averaged) data, uncomment the False option;
#    to plot every nth data point, uncomment the "resampled" option; to plot
#    static-averaged data, uncomment the "static" option
#NOTE: these options only pertain to the anemometer at present
#averaged = True
#averaged = "static"-
#averaged = "resampled"
averaged = False

#averaging; set this to the time duration (in minutes) that you want to average
#    over; your value (in minutes) should be an integer greater than 1 (i.e.
#    5 for 5 miinutes, 10 for 10 minutes, etc.)
#NOTE: this is only used in conjuction with 'averaged' variable; this means
#      that it only applies to the anemometer at present
avg_window = 30

#set the time frame over which to plot (UTC); you must use the following
#    format: "YYYY-MM-DD HH:mm"; to plot the whole dataset, set 'mintime'
#    and 'maxtime' to empty strings (e.g. mintime = ""), likewise, to plot
#    from the beginning of the time period, set mintime = "" and set 'maxtime'
#    to your end date/time. Vice versa for plotting to the end of the whole
#    time period
mintime = "2019-02-01 00:00"
maxtime = "2019-07-01 00:00"

#set this to reflect the type of plots you want (i.e. daily, weekly, monthly,
#    specified time frame); see the How To Use section for a list of accepted
#    options; to NOT plot, set 'plot_opt' to an empty string, ""
plot_opt = ""

#set the tag for which to add to the end of the figure name for saving in the
#    'save_dir' directory; leave this as an empty string if no tag is desired;
#    (e.g. set 'tag' to "2019-10" if you're plotting the month of October 2019)
#NOTE: this is only used for the default plotting option ("plotter")
tag = ""

#weighting coefficients; these are based on a level of importance for a
#    particular variable; set these as whole numbers, setting the least
#    important variable as 1 and the most important variable as n, where n is
#    the number of varialbes you are considering
ws_coef = 5   #wind speed
wd_coef = 5   #wind direction
rain_coef = 4 #rain gauge / precipitation
t_coef = 3    #temperature
p_coef = 2    #pressure
rh_coef = 1   #relative humidity



##############################################################################
##############################################################################
##############################################################################


#zip up the contents of the sensor and subfolder lists, so that each sensor
#    name given by the 'sensor' variable is matched with its corresponding
#    subfolder containing the data for said sensor (set by 'subfolder_list')
tuple_lst = list(zip(subfolder_list,sensor_list))

#collect all the folders within the parent 'directory'
folder_list = glob.glob(directory + "*")
#sort the folder list
folder_list = sorted(folder_list)

#this counter is equivalent to the number of stations multiplied by the number
#    of sensors for each station
counter = 0

#loop through each station folder that was collected via 'folder_list'
for station in folder_list:
    #count the number of characters within the parent directory
    dir_len = len(directory)
    
    #this gets us into a specific station's folder within the parent folder as
    #    previously set by the 'directory' varialbe in USER OPTIONS
    station_folder = station + "/"
    
    #collect the station name here while the filepath has a consistent number
    #    of elements from which to collect the station's name
    station_name = station_folder[dir_len:-1]
    
    #within each station folder loop through each sensor's data folder
    for subfolder,sensor in tuple_lst:
        full_path = station_folder + subfolder + "*"
        
        #small condition to get around the input checker and some reader
        #    function requirements that do not matter to us here
        if sensor.lower() == "anemometer":
            units = "mps"
        elif sensor.lower() == "rain":
            units = "mm"
        elif sensor.lower() == "si1145":
            var_name = "vis"
        else:
            var_name = "temp_C"
        
        #if this is the first iteration of both loops, the very first dataframe
        #    generated by this first iteration will be called 'df' and all
        #    others will be joined with that dataframe
        if counter == 0:

            ##############################################################################
            ############################    VERIFY INPUT    ##############################
            ##############################################################################
            
            #call the input checker function to verify a number of user inputs, namely,
            check_inputs = input_checker(sensor, var_name, units, averaged, avg_window)
            
            #'averaged' is the only variable that has the potential to change when sent to
            #    the input checker so it gets redefined here, even if is does not change
            #    in the input checker
            averaged = check_inputs
            
            
            
            ##############################################################################
            ###########################    READ IN FILE(S)    ############################
            ##############################################################################
            
            #call the appropriate function based on the sensor/variable name; need a bunch
            #    'if' statments here
            
            #read in the dataframe(s) by calling the function designed to read the data;
            #    this is pre-processed data being read in so any sorting, removal of
            #    duplicate timestamps, data conversions, etc. is done before these
            #    dataframes are read into this program. Parameters such as averaging and
            #    averaging window are specified in THIS program and given to the other
            #    program's function so that parameters in the other program do not override
            #    the ones used for THIS program
            
            if sensor.lower() == "bmp180" or sensor.lower() == "bmp280":
                call_reader = reader.bmp(full_path, wildcard)
            elif sensor.lower() == "htu21d":
                call_reader = reader.htu21d(full_path, wildcard)
            elif sensor.lower() == "mcp9808":
                call_reader = reader.mcp9808(full_path, wildcard)
            elif sensor.lower() == "si1145":
                call_reader = reader.si1145(full_path, wildcard)
            elif sensor.lower() == "rain":
                call_reader = reader.rain_gauge(full_path, units, wildcard)
            elif sensor.lower() == "wind_vane":
                call_reader = reader.wind_vane(full_path, wildcard)
            elif sensor.lower() == "anemometer":
                call_reader = reader.anemometer(full_path, units, wildcard)
            else:
                #redundant, given that this parameter gets checked with the input checker
                print("Sensor name not recognized. Program exited...")
                sys.exit()
            
            #df = reader."%s"(directory, wildcard) % sensor
            df = call_reader[0]
            missing_reports_times = call_reader[1]
            
            
            ##############################################################################
            ######################    VERIFYING MINTIME/MAXTIME    #######################
            ##############################################################################
            
            #this must be done AFTER the data is read in and cleansed since the dataset is
            #    used to determine the validity of the user-input 'mintime' and 'maxtime'
            check_time = time_checker(mintime, maxtime, plot_opt, df)
            
            #the following variables are output from the time_checker function called above;
            #    separate them by their respective, appropriate variable names since they
            #    will get used again below
            
            #mintime
            mintime = check_time[0]
            
            #maxtime
            maxtime = check_time[1]
            
            #plotting option
            plot_opt = check_time[2]
            
            #dataframe, if 'mintime' and/or 'maxtime' were not in the dataset
            df = check_time[3]
            
            #time_checker will only spit out a list of missing report times within the
            #    user-defined time frame, if the time frame is set as anything other than
            #    the entire dataset
            if mintime != 0 or maxtime != df.index[-1]:
                #timestamps for missing reports WITHIN THE USER-DEFINED TIME FRAME
                tf_missing_report_times = check_time[3]
            
            
            
            ##############################################################################
            ##########################    QUALITY ASSURANCE    ###########################
            ##############################################################################
            
            # #call the quality assurance function
            # call_QA = qa(sensor, mintime, maxtime, df)
            
            
            
            ##############################################################################
            ###########################    DATA PROCESSING    ############################
            ##############################################################################
            
            #create a 'time' variable from the 'time' column in the DataFrame as a
            #   DatetimeIndex array; this will be used for other calculations/test below
            time = pd.to_datetime(np.array(df.time))
            
            ''' Don't compute analytics on averaged / smoothed data, and don't smooth
                analytic products '''
            
            #right now, the anemometer is the only sensor that has the ability for
            #    smoothing/averaging
            if sensor == "anemometer":
                df = smoothing(averaged, avg_window, df)
            
            #data conversions are computed in the reader functions for wind speed and rain
            
            ##############################################################################
            #compute any statistical analytics here; this is a place holder and will call
            #    a function that does all the work for us; some, if not all, this
            #    information will get plugged into the creation of the output file
            
            
            #change the column names to include the station name  as well as sensor
            #    for the HTU, BMP, and MCP (e.g. vis --> WMO_HIGHWAY01_vis, or temp_C
            #    ---> WMO_HIGHWAY01_BMP_temp_C)
            
            if sensor.lower() == "bmp180" or sensor.lower() == "bmp280":
                #add sensor name to the all column names except for the 'time'
                #    column
                df = df.rename(columns={'temp_C':'%s_%s_temp' % (station_name,sensor),
                                        'station_P':'%s_station_P' % station_name})
                #drop extraneous columns from the dataframe
                df = df.drop(columns=['temp_F', 'SLP_hPa', 'SLP_inHg', 'alt'])
                
            elif sensor.lower() == "htu21d":
                #add sensor name to the all column names except for the 'time'
                #    column
                df = df.rename(columns={'temp_C':'%s_%s_temp' % (station_name,sensor),
                                        'rel_hum':'%s_relhum' % station_name})
                #drop extraneous columns from the dataframe
                df = df.drop(columns=['temp_F'])
            
            elif sensor.lower() == "mcp9808":
                #add sensor name to the all column names except for the 'time'
                #    column
                df = df.rename(columns={'temp_C':'%s_%s_temp' % (station_name,sensor)})
                #drop extraneous columns from the dataframe
                df = df.drop(columns=['temp_F'])
                
            else:
                #for all other sensors, we need only add the station name to each
                #    variable
                for col_name in df.columns:
                    if col_name == df.columns[0]:
                        pass #don't change the name of the 'time' column; this is
                             #    used as the key to join each dataframe with the
                             #    previous one
                    else:
                        df = df.rename(columns={col_name:"%s_%s" % (station_name,col_name)})
            
            
            #if this is the very first iteration of both loops, there is no need
            #    join this dataframe with a previous one because there is no
            #    previous one
            
            
            #resetting 'mintime' and 'maxtime' for the next iteration of the loop
            mintime = "2019-02-01 00:00"
            maxtime = "2019-07-01 00:00"
            
            #update the counter
            counter += 1
            
        else:
            
            ##############################################################################
            ############################    VERIFY INPUT    ##############################
            ##############################################################################
            
            #call the input checker function to verify a number of user inputs, namely,
            check_inputs = input_checker(sensor, var_name, units, averaged, avg_window)
            
            #'averaged' is the only variable that has the potential to change when sent to
            #    the input checker so it gets redefined here, even if is does not change
            #    in the input checker
            averaged = check_inputs
            
            
            
            ##############################################################################
            ###########################    READ IN FILE(S)    ############################
            ##############################################################################
            
            #call the appropriate function based on the sensor/variable name; need a bunch
            #    'if' statments here
            
            
            #read in the dataframe(s) by calling the function designed to read the data;
            #    this is pre-processed data being read in so any sorting, removal of
            #    duplicate timestamps, data conversions, etc. is done before these
            #    dataframes are read into this program. Parameters such as averaging and
            #    averaging window are specified in THIS program and given to the other
            #    program's function so that parameters in the other program do not override
            #    the ones used for THIS program
            
            if sensor.lower() == "bmp180" or sensor.lower() == "bmp280":
                call_reader = reader.bmp(full_path, wildcard)
            elif sensor.lower() == "htu21d":
                call_reader = reader.htu21d(full_path, wildcard)
            elif sensor.lower() == "mcp9808":
                call_reader = reader.mcp9808(full_path, wildcard)
            elif sensor.lower() == "si1145":
                call_reader = reader.si1145(full_path, wildcard)
            elif sensor.lower() == "rain":
                call_reader = reader.rain_gauge(full_path, units, wildcard)
            elif sensor.lower() == "wind_vane":
                call_reader = reader.wind_vane(full_path, wildcard)
            elif sensor.lower() == "anemometer":
                call_reader = reader.anemometer(full_path, units, wildcard)
            else:
                #redundant, given that this parameter gets checked with the input checker
                print("Sensor name not recognized. Program exited...")
                sys.exit()
            
            #df = reader."%s"(directory, wildcard) % sensor
            df_temp = call_reader[0]
            missing_reports_times = call_reader[1]
            
            
            ##############################################################################
            ######################    VERIFYING MINTIME/MAXTIME    #######################
            ##############################################################################
            
            #this must be done AFTER the data is read in and cleansed since the dataset is
            #    used to determine the validity of the user-input 'mintime' and 'maxtime'
            check_time = time_checker(mintime, maxtime, plot_opt, df_temp)
            
            #the following variables are output from the time_checker function called above;
            #    separate them by their respective, appropriate variable names since they
            #    will get used again below
            
            #mintime
            mintime = check_time[0]
            
            #maxtime
            maxtime = check_time[1]
            
            #plotting option
            plot_opt = check_time[2]
            
            #dataframe, if 'mintime' and/or 'maxtime' were not in the dataset
            df_temp = check_time[3]
            
            # #time_checker will only spit out a list of missing report times within the
            # #    user-defined time frame, if the time frame is set as anything other than
            # #    the entire dataset
            # if mintime != 0 or maxtime != df_temp.index[-1]:
            #     #timestamps for missing reports WITHIN THE USER-DEFINED TIME FRAME
            #     tf_missing_report_times = check_time[3]
            
            
            
            ##############################################################################
            ##########################    QUALITY ASSURANCE    ###########################
            ##############################################################################
            
            # #call the quality assurance function
            # call_QA = qa(sensor, mintime, maxtime, df)
            
            
            
            ##############################################################################
            ###########################    DATA PROCESSING    ############################
            ##############################################################################
            
            #create a 'time' variable from the 'time' column in the DataFrame as a
            #   DatetimeIndex array; this will be used for other calculations/test below
            time = pd.to_datetime(np.array(df_temp.time))
            
            ''' Don't compute analytics on averaged / smoothed data, and don't smooth
                analytic products '''
            
            #right now, the anemometer is the only sensor that has the ability for
            #    smoothing/averaging
            if sensor == "anemometer":
                df_temp = smoothing(averaged, avg_window, df_temp)
            
            #data conversions are computed in the reader functions for wind speed and rain
            
            ##############################################################################
            #compute any statistical analytics here; this is a place holder and will call
            #    a function that does all the work for us; some, if not all, this
            #    information will get plugged into the creation of the output file
            
            
            #change the column names to include the station name  as well as sensor
            #    for the HTU, BMP, and MCP (e.g. vis --> WMO_HIGHWAY01_vis, or temp_C
            #    ---> WMO_HIGHWAY01_BMP_temp_C)
            
            if sensor.lower() == "bmp180" or sensor.lower() == "bmp280":
                #add sensor name to the all column names except for the 'time'
                #    column
                df_temp = df_temp.rename(columns={'temp_C':'%s_%s_temp' % (station_name,sensor),
                                        'station_P':'%s_station_P' % station_name})
                #drop extraneous columns from the dataframe
                df_temp = df_temp.drop(columns=['temp_F', 'SLP_hPa', 'SLP_inHg', 'alt'])
                
            elif sensor.lower() == "htu21d":
                #add sensor name to the all column names except for the 'time'
                #    column
                df_temp = df_temp.rename(columns={'temp_C':'%s_%s_temp' % (station_name,sensor),
                                        'rel_hum':'%s_relhum' % station_name})
                #drop extraneous columns from the dataframe
                df_temp = df_temp.drop(columns=['temp_F'])
            
            elif sensor.lower() == "mcp9808":
                #add sensor name to the all column names except for the 'time'
                #    column
                df_temp = df_temp.rename(columns={'temp_C':'%s_%s_temp' % (station_name,sensor)})
                #drop extraneous columns from the dataframe
                df_temp = df_temp.drop(columns=['temp_F'])
                
            else:
                #for all other sensors, we need only add the station name to each
                #    variable
                for col_name in df_temp.columns:
                    if col_name == df_temp.columns[0]:
                        pass #don't change the name of the 'time' column; this is
                             #    used as the key to join each dataframe with the
                             #    previous one
                    else:
                        df_temp = df_temp.rename(columns={col_name:"%s_%s" % (station_name,col_name)})
            
            
            #if this is the very first iteration of both loops, there is no need
            #    join this dataframe with a previous one because there is no
            #    previous one
            
            
            #resetting 'mintime' and 'maxtime' for the next iteration of the loop
            mintime = "2019-02-01 00:00"
            maxtime = "2019-07-01 00:00"
            
            #update the counter
            counter += 1
            
            df = df.join(df_temp.set_index('time'), on='time')
        
    ### END OF 'subfolder'/'sensor' LOOP ###
    

### END OF  'folder_list' LOOP ###


##############################################################################
################################   OUTPUT   ##################################
##############################################################################

#this is the total raw value count for each row (timestamp)
row_count = df.set_index('time').count(axis='columns').reset_index()

#initialize the individual variable-type dataframes with the 'time' column
#    from the original dataframe
df_spd = pd.DataFrame({'time':df.time})
df_dir = pd.DataFrame({'time':df.time})
df_rain = pd.DataFrame({'time':df.time})
df_tmp = pd.DataFrame({'time':df.time})
df_P = pd.DataFrame({'time':df.time})
df_rh = pd.DataFrame({'time':df.time})

#loop by column, collecting like variables for each station into its respective
#    dataframe
for col in df.columns:
    if "wind_speed" in col:
        df_spd[col] = df[col]
    elif "wind_dir" in col:
        df_dir[col] = df[col]
    elif "rain" in col:
        df_rain[col] = df[col]
    elif "temp" in col:
        df_tmp[col] = df[col]
    elif "station_P" in col:
        df_P[col] = df[col]
    elif "relhum" in col:
        df_rh[col] = df[col]
    else:
        pass

#remove the "no_rain" columns from the rain dataframe; we don't want these 
for col in df_rain.columns:
    if "no_rain" in col:
        df_rain = df_rain.drop(columns=col)

#count the number of datum per timestamp for each variable dataframe
row_count_spd = df_spd.set_index('time').count(axis='columns').reset_index().rename(columns={0:'count'})
row_count_dir = df_dir.set_index('time').count(axis='columns').reset_index().rename(columns={0:'count'})
row_count_rain = df_rain.set_index('time').count(axis='columns').reset_index().rename(columns={0:'count'})
row_count_P = df_P.set_index('time').count(axis='columns').reset_index().rename(columns={0:'count'})
row_count_rh = df_rh.set_index('time').count(axis='columns').reset_index().rename(columns={0:'count'})

#must loop through each row of the temperature dataframe because there are
#    3 distinct temperature readings, but we must only count it once, even if
#    all 3 exist            
#initialize the list to house each timestamp's temperature count (only 1 for
#    each station, if one exists)            
row_count_tmp = []
for i in range(len(df_tmp)):
    
    #this will be the count of temperature measurements for all stations for
    #    each given timestamp, but will only count each station once; it must
    #    be within the loop above so that it resets to zero for each row
    temp_count = 0
    
    #now must loop via each set of station temperature columns; there should
    #    be 3 columns per station; we set the starting value as 1 so that we
    #    do not count the 'time' column
    for j in range(1,len(df_tmp.columns),3):
        #when 'j' is out of range, break out of this loop and move on to the
        #    next iteration of the loop that goes through each timestamp
        if j > len(df_tmp.columns):
            break
        
        #whether there is one, two, or three valid temperatures for a given
        #    station...
        if df_tmp.iloc[i,j:j+3].count() > 0:
            #....count it once
            temp_count += 1
        else: #if there are no valid values, do not increase the count
            pass
    
    #once the counting of valid temperartures has concluded, add the final
    #    count to the list of row counts
    row_count_tmp.append(temp_count)
    
#add the modified row count of temperatures to the temperature dataframe
row_count_tmp = pd.DataFrame({'time':df_tmp.time,'count':row_count_tmp}) 

#put all the individual row-count dataframes into a single dataframe
df_count = pd.DataFrame({'time':df.time,'spd_count':row_count_spd['count'],
                         'dir_count':row_count_dir['count'],
                         'rain_count':row_count_rain['count'],
                         'tmp_count':row_count_tmp['count'],
                         'press_count':row_count_P['count'],
                         'rh_count':row_count_rh['count']})

#the window of time we will consider counter non-NaNs
window = 1440 #equivalent to the number of minutes (the 3D-PAWS report
               #    frequency is 1 minute) in a 24-hour period
#how often we want to consider the above window of time (60 --> every hour)
interval = 60 #equivalent to the number of minutes in 1 hour, which is how
               #    often we want to compute the sum of non-NaNs per 24-hour
               #    period (doing a rolling computation every single minute is
               #    computationally expensive and not likely very informative)
               
#start time of loop
start = 0
#end time of loop (add 1 because the range function is right-exclusive)
end = df.index[-1] + 1


dictionary = {}
#loop through each running 24-hour period but only for each hour (not each
#    minute)
for i in range(start,end,interval):
    #when the iterator is out of range, simply break out of the loop
    if i > end or i+interval > end or i+window > end:
        break
    
    #for each column (except 'time'), compute the sum of all values within
    #    the given 24-hour period, then, apply the weighting coefficients to
    #    their respective variable sums (e.g. 'ws_coef' to the sum for
    #    'spd_count', 'wd_coef' to the sum for 'dir_count', and so on)
    ws = df_count.spd_count[i:i+window+1].sum() * ws_coef
    wd = df_count.dir_count[i:i+window+1].sum() * wd_coef
    r = df_count.rain_count[i:i+window+1].sum() * rain_coef
    t = df_count.tmp_count[i:i+window+1].sum() * t_coef
    P = df_count.press_count[i:i+window+1].sum() * p_coef
    rh = df_count.rh_count[i:i+window+1].sum() * rh_coef
    
    #compute the sum of the weighted sums from above; this represents the
    #    total amount of data available for the given 24-hour period, weighted
    #    by measurand
    weighted_sum = ws + wd + r + t + P + rh
    
    #append this value and the timestamps defining the timeframe said value is
    #    valid for to a dictionary
    dictionary.update({str(df.time[i]) + " - " + str(df.time[i+window]):weighted_sum})
    
#finally, give a list of the top 10 most data-rich 24-hour periods
top_10 = sorted(dictionary, key=dictionary.get, reverse=True)[:10]


##############################################################################
###############################   PLOTTING   #################################
##############################################################################

#NOTE: plot_opt is not sent to the input checker because we have set it up
#      such that even if an incorrect/unacceptable option is provided (e.g. a
#      misspelling), the program will simply default to the regular "plotter"

#based on the user-input plotting option, call the appropriate plotting
#    function
if plot_opt == "plotter":
    #call the regular plotting function; reminder: this simply plots the time
    #    frame set by the user on one figure
    pltr.plotter(sensor, save_dir, site_ID, var_name, units, averaged,
                 avg_window, mintime, maxtime, plot_opt, tag, df)

elif plot_opt == "daily":
    #call the daily-plotting function
    pltr.daily_plotter(sensor, save_dir, site_ID, var_name, units, averaged,
                 avg_window, mintime, maxtime, plot_opt, tag, df)
    
elif plot_opt == "weekly":
    #call the weekly-plotting function
    pltr.weekly_plotter(sensor, save_dir, site_ID, var_name, units, averaged,
                        avg_window, mintime, maxtime, plot_opt, tag, df)

elif plot_opt == "monthly":
    #call the monthly-plotting function
    pltr.monthly_plotter(sensor, save_dir, site_ID, var_name, units, averaged,
                        avg_window, mintime, maxtime, plot_opt, tag, df)
    
elif plot_opt == "":
    #don't plot if 'plot_opt' set to an empty string
    pass

else:
    #if any other option besides the specific options listed in the READ ME
    #    section, assume the calling of the regular plotting function (e.g. in
    #    the event of a misspelling, the program will still run but will
    #    default to this option)
    print("plot option not recognized...\n")
    pltr.plotter(sensor, save_dir, site_ID, var_name, units, averaged,
                 avg_window, mintime, maxtime, plot_opt, tag, df)







