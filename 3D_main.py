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
#    1. Change all variables in "USER OPTIONS" section to desired input
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
#    2. Run with "python 3D_main.py" in terminal, or open in
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
import reader
from input_checker import input_checker
from time_checker import time_checker
from data_smoother import smoothing
import plotter as pltr



##############################################################################
############################    USER OPTIONS    ##############################
##############################################################################

#set this to the name of the sensor from which you want to plot (NOT case
#    sensitive)
sensor = "BMP280"

#set the 'directory' variable to the absolute path where your data are stored;
#    don't forget the trailing forward slash!
directory = "/Users/blund/Documents/3D-PAWS/Data/3DPAWS_FrederickCO/data/bmp/"

#specify the FULL file path to the directory in which to save your figures;
#    don't forget to include the trailing forward slash!
save_dir = "/Users/blund/Documents/Python_Scripts/Figures/Frederick_CO/BMP280/"

#set the wildcard option; to read in EVERY file within the directory you
#    specified above in 'directory', set 'wildcard' to "*"; you may specify
#    this to select a subset of data (e.g. "*2020*" to only read in files from
#    2020)
wildcard = "*"

#change this to the name of the site from which data are being plotted; this
#    will be used in the plot title as well as the name of the figure
site_ID = "Frederick_CO"

#change this to the name of the variable you want to plot; a list of
#    acceptable options can be found in the "How to Use:" section above
var_name = "temp_C"

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
#averaged = "static"
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
mintime = ""
maxtime = ""

#set this to reflect the type of plots you want (i.e. daily, weekly, monthly,
#    specified time frame); see the How To Use section for a list of accepted
#    options; to NOT plot, set 'plot_opt' to an empty string, ""
plot_opt = ""

#set the tag for which to add to the end of the figure name for saving in the
#    'save_dir' directory; leave this as an empty string if no tag is desired;
#    (e.g. set 'tag' to "2019-10" if you're plotting the month of October 2019)
#NOTE: this is only used for the default plotting option ("plotter")
tag = "network-time"



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
    call_reader = reader.bmp(directory, wildcard)
elif sensor.lower() == "htu21d":
    call_reader = reader.htu21d(directory, wildcard)
elif sensor.lower() == "mcp9808":
    call_reader = reader.mcp9808(directory, wildcard)
elif sensor.lower() == "si1145":
    call_reader = reader.si1145(directory, wildcard)
elif sensor.lower() == "rain":
    call_reader = reader.rain_gauge(directory, units, wildcard)
elif sensor.lower() == "wind_vane":
    call_reader = reader.wind_vane(directory, wildcard)
elif sensor.lower() == "anemometer":
    call_reader = reader.anemometer(directory, units, wildcard)
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



##############################################################################
################################   OUTPUT   ##################################
##############################################################################

# #placeholder section for generating a file that will store all kinds of stats,
# #    metrics and other metadata for analysis
# call_output = output.



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





