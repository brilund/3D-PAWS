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

#This code reads and plots data from the UCAR/NCAR COMET 3D-PAWS system wind
#    vane sensor.
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
#    Jul 13, 2020 - First Write
#    Jul 15, 2020 - Added user-defined options for averaging and resampling
#    Sep 03, 2020 - Added uptime calculation; this is based solely off of
#                   the amount of data EXPECTED between the first date/time
#                   and the last date/time read in, so if you were interested
#                   in the uptime for the month of Feb '19, but what you
#                   read in started at 2019-02-02 05:37, your percentage
#                   may not be truly representative of the time frame
#                   you are interested in
#
#
#Planned Features:
#    1. Create an instance of tkinter that opens a Finder/Explorer window when
#       the user runs the program for the user to select the folder where all
#       subfolder and data reside???
#    2. More sophistocated Error Catchers that print out useful statements to 
#       the user trhoughout the entire script (having a single section simply
#       will not suffice nor be practical.)
#    3. Include more user options:
#       a. user-defined time frames over which to plot
#       b. ability to add a tag to the end of file names based on user input
#    4. Use prompts for user input??? This will ensure the options are changed
#       when the program is run for any user, but could also be tedious to
#       have to enter those options every time; perhaps a parameter file is
#       better???
#    5. Separate major sections into callable functions: reader, processor,
#       output, plotter, etc.
#    6. Create a list of where out-of-order timestamps occur in an unsorted
#       dataset
#    7. Add the ability to also read in the wind DIRECTION data so users have
#       the option to plot two types: time series line plot, or a time series
#       wind barb plot
#    8. Develop a method to be able to set 'min-' and 'maxtime' to times that
#       may not exist in the raw data that was read in, but if it technically
#       falls within the date range read in, it should be accepted
#    9. Develop a better way to clean up the wind direction data since taking
#       an average will invariably eliminate northerly winds out of the
#       dataset since 0 and 360 represent the extremes
#
#
#How to Use:
#    1. Change all variables in "USER OPTIONS" section to desired input
#           directory
#           site_ID
#           averaged: True, False, "static", "resampled"
#           save_dir
#           wildcard
#           tag
#    2. Run with "python WINDDIR_reader-plotter.py" in terminal, or open in
#       Spyder and run from there.
#
#
#Example header from files --> no file header(s)!!! (this could change...)
#
#Example data from files:
#    
#
#
#NOTES: There is presently no automated way to save figures with a name
#       specifying a subset of time; you may add a time specification manually
#       in the SAVE FIGURE(S) section at the bottom:
#
#       e.g. if averaged == False:
#                plt.savefig('%s%s_wind-dir_%s.png' % (save_dir, site_ID, tag), \
#                            dpi=500, bbox_inches='tight')
#
#       ... or by setting the 'tag' user option to something related
# ----------------------------------------------------------------------------
#       At the moment, this program reads in all data even if a subset of time
#       is requested for plotting, which is a bit of an overkill



##############################################################################
#########################    IMPORTING MODULES    ############################
##############################################################################

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import sys
from wind_dir_function import wind_dir_processor
#import plotly.express as px



##############################################################################
############################    USER OPTIONS    ##############################
##############################################################################

#set the 'directory' variable to the absolute path where your data are stored;
#    don't forget the trailing forward slash!
directory = "/Users/blund/Documents/3D-PAWS/Data/WMO_HIGHWAY_14/data/wind_direction/"

#change this to the name of the site from which data are being plotted; this
#    will be used in the plot title as well as the name of the figure
site_ID = "CSA_3DPAWS01"

#plot raw data or averaged data; to plot averaged data, uncomment the True
#    option; to plot raw data, uncomment the False option

#averaged = True
#averaged = "static"
#averaged = "resampled"
averaged = False


#averaging; set this to the time duration (in minutes) that you want to average
#    over; your value (in minutes) should be an integer greater than 1 (i.e.
#    5 for 5 miinutes, 10 for 10 minutes, etc.)
avg_window = 30

#specify the FULL file path to the directory in which to save your figures;
#    don't forget to include the trailing forward slash!
save_dir = "/Users/blund/Documents/Python_Scripts/Figures/CSA_3DPAWS01/WINDDIR/"

#uncomment this option to read in EVERY file withing the directory you
#    specified above in 'directory'
wildcard = "*"
#uncomment this option to specify your own wildcard to select a subset of data
#    within the directory you specified above in 'directory'
#wildcard = "*2019*"

#set the time frame over which to plot (UTC); you must use the following
#    format: "YYYY-MM-DD HH:mm"; to plot the whole dataset, set 'mintime'
#    and 'maxtime' to empty strings (e.g. mintime = ""), likewise, to plot
#    from the beginning of the time period, set mintime = "" and set 'maxtime'
#    to your end date/time. Vice versa for plotting to the end of the whole
#    time period
mintime = "2019-02-01 00:00"
maxtime = "2019-07-01 00:00"

#set the tag for which to add to the end of the figure name in the SAVE FIGURE
#    section at the bottom; leave this as an empty string if no tag is desired;
#    (e.g. set 'tag' to "2019-10" if you're plotting the month of October 2019)
tag = "2019_Feb-Jun"



##############################################################################
###########################    READ IN FILE(S)    ############################
##############################################################################

#if plotting averaged data, check that the averaging window is valid
if averaged == True or averaged == "static" or averaged == "resampled":
    if avg_window < 1:
        raise ValueError("Averaging window must be greater than or equal to 1.")
    elif avg_window == 1:
        #setting the averaging window to 1 is equivalent to plotting raw data,
        #    so set 'averaged' to False and inform the user
        print("Averaging window set to 1. Plotting raw data...")
        averaged = False
    else:
        #All other conditions are accepted
        pass
elif averaged != "static" and averaged != "resampled" and averaged != False:
    #if "averaged" is not equal to any of the other three accepted conditions,
    #    then raise an error
    raise ValueError("'averaged' option not recognized.")
else:
    pass



##############################################################################
###########################    DATA PROCESSING    ############################
##############################################################################

#read in the dataframes for wind speed and wind direction from their respective
#    programs; this is pre-processed data being read in so any sorting,
#    removal of duplicate timestamps, data conversions, etc. is done
#    before these data frames are read into this program (averaging is NOT
#    computed externally; that is done within THIS program since we need to
#    first ensure that we collect data with like timestamps) Those parameters
#    are specified in THIS program and given to the other programs' functions
#    so that parameters in the wind speed only and wind direction only programs
#    do not override the ones used for THIS program
df = wind_dir_processor(directory, wildcard)


##############################################################################


#separate each column in the DataFrame back into numpy.arrays (DatetimeIndex for
#    the 'time' column)
time = pd.to_datetime(np.array(df.time))
wind_dir = np.array(df.wind_dir, dtype=float)


################## Checking 'mintime' / 'maxtime' Validity ###################

#check to see if the user input the 'mintime' and 'maxtime' in the proper format.
#    This will account for occurrences with 'mintime' and/or 'maxtime' being
#    empty strings (to indicate the beginning or ending of the time frame,
#    respectively) and requires the string length be 16 characters long. Pandas
#    datetimeindex has the ability to read in multiple formats, but this length
#    requirement helps weed out a number of potentially incompatible formats,
#    making the creation of the following error checkers more manageable!
if mintime == "" and len(maxtime) == 16:
        try:
            pd.to_datetime(maxtime, format='%Y-%m-%d %H:%M')
        except ValueError:
            raise ValueError("Incorrect format for 'maxtime'; should be YYYY-MM-DD HH:mm")
        
elif maxtime == "" and len(mintime) == 16:
        try:
            pd.to_datetime(mintime, format='%Y-%m-%d %H:%M')
        except ValueError:
            raise ValueError("Incorrect format for 'mintime'; should be YYYY-MM-DD HH:mm")
    
elif len(mintime) == 16 and len(mintime) == 16: #they should include 16 characters
        try:
            pd.to_datetime(mintime, format='%Y-%m-%d %H:%M')
            pd.to_datetime(maxtime, format='%Y-%m-%d %H:%M')
        except ValueError:
            raise ValueError("Incorrect format for 'mintime'/'maxtime'; should be YYYY-MM-DD HH:mm")  
            
elif mintime == "" and maxtime == "":
    pass
            
else:
    #anything that is not an empty string or 16 characters in length
    #    automatically fails the checks
    raise TypeError("Incorrect format for 'mintime'; should be YYYY-MM-DD HH:mm")
    
#then check to see if 'mintime' and 'maxtime' are within the dataset that was
#    read in
#Note: the method min() and max() are functions of both DataFrames and
#      datetimeindex, so if we wanted, we could also do this: df.time.min()
if pd.to_datetime(mintime) < df.time.min() or pd.to_datetime(maxtime) > df.time.max():
    print("'mintime'/'maxtime' are outside the range of time.")
    print("The minimum start time is %s." % str(time.min()))
    print("The maximum end time is %s.\n" % str(time.max()))
    #remind the user what their start/end time limits are^
    sys.exit()

#check that 'mintime' is explicitly less than 'maxtime'
if pd.to_datetime(mintime) >= pd.to_datetime(maxtime):
    print("'mintime' is greater than or equal to 'maxtime'.\n")
    sys.exit()    


########################## Setting the Time Frame ############################

#set up the user-defined time frame
#Note: the method .get_loc() used below is a function of datetimeindex, NOT
#      DataFrames, so we must resort to using the datetimeindex array 'time'
#      that was created from the 'time' column in the dataframe
if mintime == "" and maxtime == "":
    #if 'mintime' and 'maxtime are empty strings, then the user must want to
    #    plot the entire dataset
    print("Plotting entire data set...\n")
    mintime = 0 #set 'mintime' to the index of the first time in 'time' 
    maxtime = -1 #set 'maxtime' to the index of the last time in 'time'
elif mintime == "" and maxtime != "":
    #if 'mintime' is an empty string, but 'maxtime' is not, then plot from the
    #    beginning of the dataset to the specified endtime (i.e. 'maxtime')
    mintime = 0
    maxtime = time.get_loc(pd.to_datetime(maxtime))
elif mintime != "" and maxtime == "":
    #if 'mintime' is not an empty string, but 'maxtime' is, then plot from the
    #    start time specified by 'mintime' to the end of the dataset
    mintime = time.get_loc(pd.to_datetime(mintime))
    maxtime = -1
elif mintime != "" and maxtime != "":
    #if setting a user-defined time frame over which to plot, first convert
    #    the 'mintime' and 'maxtime' strings to pandas Timestamps
    mintime = time.get_loc(pd.to_datetime(mintime))
    maxtime = time.get_loc(pd.to_datetime(maxtime)) 
    

######################### Uptime within Time Frame ########################### 

#calculate the total uptime based on the number of missing reports,
#    but within the time frame ('mintime' and 'maxtime') set by the user
missing_reports = df.wind_dir[mintime:maxtime].isna().sum()
total = pd.Timedelta(len(df.index[mintime:maxtime]), unit='m')
uptime = pd.Timedelta((len(df.index[mintime:maxtime]) - missing_reports), unit='m')
uptime_percent = round((1 - (float(missing_reports) / float(len(df[mintime:maxtime])))) * 100., 1)
print("Uptime during the time frame is %s out of %s (%s%%).\n" % (uptime,total,uptime_percent))


################################# Averaging ##################################
#to average or not to average???
#This section will compute any user-defined specifics for averaging the data.
#    The options here include "do nothing" i.e. raw data, computing a running
#    average based on a user-defined averaging window (e.g. 5 minutes, 10
#    minutes 13 minutes, etc.), plotting static-averaged data (useful for
#    longer time series), or plotting a lower density of data (useful for
#    longer time series)
if averaged == True:
    #computing the running average of wind direction based on the user-defined
    #    averaging window; add this as a new column in the existing dataframe
    #    and shift the computed values back in time X-1 minutes where X is the
    #    user-defined averaging window, so that the value computed over that
    #    duration is now valid for the beginning of the time frame (i.e. a 10-
    #    min running average beginning at 08:00 will be valid [plotted] for
    #    [at] 08:00)
    print("Plotting %s-min running averaged data..." % avg_window)
    df['winddir_avg'] = df.iloc[:,1].rolling(window=avg_window).mean().shift(-(avg_window-1))
    
elif averaged == False:
    #if averaging is set to False, then do nothing and continue on your merry
    #    way
    print("Plotting raw data...")
    pass

elif averaged == "static":
    #"static" average based on the user-defined averaging window but with a
    #    temporal resolution equivalent to the averaging window; this line is
    #    exactly the same as with the running average, but we will select every
    #    nth data point (beginning with the first) when plotting since that is
    #    equivalent to computing the static average
    print("Plotting %s-min static averaged data..." % avg_window)
    df['winddir_avg'] = df.iloc[:,1].rolling(window=avg_window).mean().shift(-(avg_window-1))

elif averaged == "resampled":
    #resampling; there is no need to do anything here, but the "resampled"
    #    option will plot every nth raw data point where 'n' is the averaging
    #    window ("avg_window") set by the user
    print("Plotting every %s data points (minutes)..." % avg_window)

#NOTE: we need not account for the potential of "averaged" being an unaccepted
#      option because the error checker above at the beginning of the DATA
#      PROCESSING section will handle that exception by raising an error



##############################################################################
#################################   OUTPUT   #################################
##############################################################################

#placeholder section for generating a file that will store all kinds of stats,
#    metrics and other metadata for analysis



##############################################################################
###############################   PLOTTING   #################################
##############################################################################

''' Include an option for one variable to be plotted or to plot all variables
    in their own separate figures '''
#size of plot
#plt.figure(figsize=(30,5))

# ######################
# #Use this section for plotting two variables on the same plot with different axes:
# #    incorporate it into your plotter function as an option for users 
# color = 'b'
# fig, ax1 = plt.subplots(figsize=(30,5))
# ax1.set_xlabel('Time (UTC)')
# ax1.set_ylabel('Temperature ($^o$C)', color=color)
# ax1.plot(time[:], temp_C[:], color=color)
# ax1.tick_params(axis='y', labelcolor=color)
# plt.ylim(-20., 40)
# plt.grid(linestyle='--')

# ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis

# # ax.yaxis.set_label_position("right")
# # ax.yaxis.tick_right()

# color = 'r'
# ax2.set_ylabel('Temperature ($^o$F)', color=color)  # we already handled the x-label with ax1
# ax2.plot(time[:], temp_F[:], color=color, linestyle='--', alpha=0.65)
# ax2.tick_params(axis='y', labelcolor=color)
# plt.ylim(-4., 104.)

#######################
#pandas plotting

#not sure what this does, but supposedly it is necessary for larger datasets;
#    this will not plot without it
#mpl.rcParams['agg.path.chunksize'] = 10000

#plot
if averaged == False:
    #plotting all raw data
    ax = df.plot(x='time', y='wind_dir', color='b', label='wind_dir',
                 figsize=(30,5))
elif averaged == True:
    #plotting running averaged data
    ax = df.plot(x='time', y='winddir_avg', color='b', label='wind_dir_%s-min' % avg_window,
                 figsize=(30,5))
elif averaged == "static":
    #plotting static averaged data (fewer data points)
    ax = df[::avg_window].plot(x='time', y='winddir_avg', color='b',label='wind_dir_%s-min-%s' % (avg_window, averaged),
                 figsize=(30,5))
elif averaged == "resampled":
    #plotting every nth raw data point (fewer data points)
    ax = df[::avg_window].plot(x='time', y='wind_dir', color='b', label='wind_dir_%s' % averaged,
                 figsize=(30,5))
else:
    #plotting all raw data
    ax = df.plot(x='time', y='wind_dir', color='b', label='wind_dir',
                 figsize=(30,5))

#set y-axis limits/range
ax.set_ylim(0., 360.)

#set the y-axis label
plt.ylabel("Wind Direction (degrees)")

### UNIVERSAL PLOTTING PARAMETERS ###
#ax.xaxis.set_major_locator(mdates.MonthLocator())
    
#add dashed grid lines
plt.grid(which='major', linestyle='--', color='dimgray')
plt.grid(which='minor', linestyle=':',color='gray')
#plt.gca().yaxis.grid(linestyle='--')

# #Set x-axis major ticks to weekly interval, on Mondays
# ax.xaxis.set_major_locator(mdates.WeekdayLocator(byweekday=mdates.MONDAY))
# #Format x-tick labels as 3-letter month name and day number
# ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))

#set x-axis limits/range
ax.set_xlim(time[mintime], time[maxtime])

#set the plot's title
plt.title("%s : Wind Vane" % site_ID, fontsize=14)

#set the x-axis label
plt.xlabel("Date / Time (UTC)")

#set the plot legend
plt.legend(loc='upper left', bbox_to_anchor=(1, 1), framealpha=0.95,
            fancybox=True, shadow=True, fontsize=10)



##############################################################################
##############################   SAVE FIGURE    ##############################
##############################################################################

# #save the figure
# if averaged == False:
#     plt.savefig('%s%s_wind-dir_%s.png' % (save_dir, site_ID, tag), \
#                 dpi=500, bbox_inches='tight')
# elif averaged == True:
#     plt.savefig('%s%s_wind-dir_%s-min_%s.png' % (save_dir, site_ID, avg_window, tag), \
#                 dpi=500, bbox_inches='tight')
# elif averaged == "static":
#     plt.savefig('%s%s_wind-dir_%s-min-%s_%s.png' % (save_dir, site_ID, avg_window, averaged, tag), \
#                 dpi=500, bbox_inches='tight')
# elif averaged == "resampled":
#     plt.savefig('%s%s_wind-dir_%s-min-%s_%s.png' % (save_dir, site_ID, avg_window, averaged, tag), \
#                 dpi=500, bbox_inches='tight')
# else:
#     plt.savefig('%s%s_wind-dir_%s.png' % (save_dir, site_ID, tag), \
#                 dpi=500, bbox_inches='tight')

#show the figure that was generated
plt.show()


