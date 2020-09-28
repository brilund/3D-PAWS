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
#    vane and anemometor sensors.
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
#    July 22, 2020 - First Write
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
#
#
#How to Use:
#    1. Save copies of the wind_spd_function and wind_dir_function files in
#       the same directory as this program
#    1. Change all variables in "USER OPTIONS" section to desired input
#           dir_directory
#           spd_directory
#           site_ID
#           save_dir
#           wildcard
#           tag
#    2. Run with "python WIND_plotter.py" in terminal, or open in
#       Spyder and run from there.
#
#
#Example header from files --> no file header(s)!!! (this could change...)
#
#Example data from files:
#    
#
#
#NOTES: the y-axis range for most variables will be site-dependent. These are
#       currently hard-coded in the plotting section for each variable. If you
#       see no data with the first attempt to plot a variable, try commenting
#       out the following line for the appropriate varaible:
#
#       #set y-axis limits/range
#       ax.set_ylim(900., 1100.)
#
#       Set the y-axis limits according to your dataset
# ----------------------------------------------------------------------------
#       There is presently no automated way to save figures with a name
#       specifying a subset of time; you may add a time specification manually
#       in the SAVE FIGURE(S) section at the bottom:
#
#       e.g. if var_name == "temp_C":
#                plt.savefig('%s%s_MCP9808_temp-C.png' % (save_dir, site_ID), dpi=500, \
#                bbox_inches='tight')
#
#       ... or by setting the 'tag' user option to something related
# ----------------------------------------------------------------------------
#       At the moment, this program reads in all data even if a subset of time
#       is requested for plotting, which is a bit of an overkill



##############################################################################
#########################    IMPORTING MODULES    ############################
##############################################################################

import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import glob
import pandas as pd
import sys
from wind_dir_function import wind_dir_processor
from wind_spd_function import wind_spd_processor
#import plotly.express as px



##############################################################################
############################    USER OPTIONS    ##############################
##############################################################################

#set the 'dir_directory' variable to the absolute path where your wind
#    DIRECTION data are stored; don't forget the trailing forward slash!
dir_directory = "/Users/blund/Documents/3D-PAWS/Data/CSA_3DPAWS01/wx_stn/winddir/"

#set the 'spd_directory' variable to the absolute path where your wind SPEED 
#    data are stored; don't forget the trailing forward slash!
spd_directory = "/Users/blund/Documents/3D-PAWS/Data/CSA_3DPAWS01/wx_stn/windspd/"

#change this to the name of the site from which data are being plotted; this
#    will be used in the plot title as well as the name of the figure
site_ID = "CSA_3DPAWS01"

#change this to the name of the variable you want to plot; a list of
#    acceptable options can be found in the "How to Use:" section above
units = "mps"

#change this to the desired frequency with which you want to plot wind barbs;
#    this must be an integer; this value equates to minutes (e.g. f=10 means
#    plotting 1 barb every 10th minute); set this to 1 to plot every
#    measurement
freq = 10

#specify the FULL file path to the directory in which to save your figures;
#    don't forget to include the trailing forward slash!
save_dir = "/Users/blund/Documents/Python_Scripts/Figures/CSA_3DPAWS01/WINDS/"

#uncomment this option to read in EVERY file withing the directory you
#    specified above in 'directory'
wildcard = "*"
#uncomment this option to specify your own wildcard to select a subset of data
#    within the directory you specified above in 'directory'
# wildcard = "*2020*"

#set the time frame over which to plot (UTC); you must use the following
#    format: "YYYY-MM-DD HH:mm"; to plot the whole dataset, set 'mintime'
#    and 'maxtime' to empty strings (e.g. mintime = ""), likewise, to plot
#    from the beginning of the time period, set mintime = "" and set 'maxtime'
#    to your end date/time. Vice versa for plotting to the end of the whole
#    time period
mintime = ""
maxtime = ""

#set the naming tag; this will be added to the end of the figure name in the
#    SAVE FIGURE section at the bottom; leave this as an empty string if no
#    tag is desired; (e.g. set 'tag' to "2019-10" if you're plotting the month
#    of October 2019)
tag = "ALL"



##############################################################################
###########################    READ IN FILE(S)    ############################
##############################################################################

#check to see if the user-input variable is from the list provided
if units == "mps" or units == "kmph" or units == "mph" or units == "kts":
    pass
else:
    print("'%s' is not an accepted unit identifier\n" % units)
    print("Accepted unit identifiers are...")
    print("'mps' for meters per second (m/s)")
    print("'kmph' for kilometers per hour (km/h)")
    print("'mph' for miles per hour (mi/h)")
    print("'kts' for knots")
    sys.exit()

#read in the dataframes for wind speed and wind direction from their respective
#    programs; this is pre-processed data being read in so any sorting,
#    removal of duplicate timestamps, data conversions, etc. is done
#    before these data frames are read into this program (averaging is NOT
#    computed externally; that is done within THIS program since we need to
#    first ensure that we collect data with like timestamps) Those parameters
#    are specified in THIS program and given to the other programs' functions
#    so that parameters in the wind speed only and wind direction only programs
#    do not override the ones used for THIS program

speed_df = wind_spd_processor(spd_directory, units, wildcard)
direction_df = wind_dir_processor(dir_directory, wildcard)



##############################################################################
###########################    DATA PROCESSING    ############################
##############################################################################

#find all records from both wind SPEED and DIRECTION such that the timestamps
#    for both are equal and create a NEW dataframe with that data.

#collect the indices of both speed and direction dataframes such that the times
#    in 'speed_df' ('direction_df) do NOT match any element of 'direction_df'
#    ('speed_df'); reminder that this is not a index by like index comparison.
#    The indices in the variables below will not be equal, but the length of
#    each variable should be the same
spd_drop_indices = np.nonzero(np.in1d(speed_df.time,direction_df.time, invert=True))[0]
dir_drop_indices = np.nonzero(np.in1d(direction_df.time,speed_df.time, invert=True))[0]

#remove the rows from both 'speed' and 'direction' data frames such that the
#    times in each do not have a matching partner in the other (i.e. if a time
#    in 'speed_df' does not have a match in 'direction_df', remove that row
#    entirely)
speed_df = speed_df.drop(spd_drop_indices)
direction_df = direction_df.drop(dir_drop_indices)

#the following two lines ensure that if rows were dropped, the indices now
#    begin at zero and monotonically increase according the new dataset
direction_df = pd.DataFrame({'time':pd.to_datetime(np.array(direction_df.time)),
                                 'wind_dir':np.array(direction_df.wind_dir)})
speed_df = pd.DataFrame({'time':pd.to_datetime(np.array(speed_df.time)),
                                 'wind_speed':np.array(speed_df.wind_speed)})

#check that the lengths of both these newly trimmed data frames are the same
if len(speed_df) != len(direction_df):
    raise ValueError ("Wind speed and direction data frames do not contain the same number of records.")

#check also that the times in both speed and direction data frames are the same
#first check if their time column lengths are equal
if len(speed_df.time) == len(direction_df.time):
    
    #create an array of booleans (all 'True') the same length as one of the
    #    time columns --> we need only use one of the time columns because we
    #    know the length of both are the same by the preceding condition
    boolean = np.full(len(speed_df.time), True, dtype=bool)
    
    #check each like index from both arrays; if the timestamps for a given
    #    index are not equal, flip the truth of the boolean value in 'boolean'
    #    for the same index (i.e. 'True' becomes 'False')
    for i in range(len(speed_df.time)):
        if speed_df.time[i] != direction_df.time[i]:
            boolean[i] = False
    
    #if any element of 'boolean' is not 'True', meaning that at least one pair
    #    or timestamps in each set of times do not match, then this condition
    #    will return 'False' and exit the program/
    if np.all(boolean) != True:
        raise TypeError ("Timestamps in wind speed and direction data frames are not equal.")
    
    else:
        #if they are equal, we can simply use one of the sets of times from here
        #    on out, and put the data back into a new data frame
        df = pd.DataFrame({'time':speed_df.time, 'wind_speed':speed_df.wind_speed,
                            'wind_dir':direction_df.wind_dir})
else:
    raise ValueError("Number of times in 'speed_df' is NOT equal to number of times in 'direction_df.'")


########################### Filling Gaps with NaNs ###########################

#Now we check to see if there are any missing report times after aligning the
#    wind speed timestamps with the wind direction timestamps. This quantity
#    should be greater than or equal to that calculated from only wind speed
#    data or only wind direction data, independently. Measurement reporting
#    times are not always perfectly coincident between the two datasets so
#    those that do not match up are removed from the dataset.
#NOTE: because of the rounding of timestamps to the nearest minute in the
#      functions that read in the data, it is entirely possible that even the
#      timestamps that we aligned above are not TECHNICALLY perfectly
#      coincident, however, the most a wind speed and direction record would
#      differ by is 30 seconds
num_data_gaps = (df.time.diff() > pd.Timedelta(minutes=1)).sum()
#NOTE: the value contained in 'num_data_gaps' is not necessarily representative
#      of the number of missing reports because each data gap could contain
#      multiple missing reports (e.g. a time gap from 14:10 UTC to 14:15 UTC
#      counts as only 1 data gap but accounts for 4 missing minutely reports
#      {14:11, 14:12, 14:13, and 14:14 UTC})

if num_data_gaps > 0: #NaTs are not included in 'num_data_gaps' (i.e. the very
                      #    first [zeroeth index] value will be NaT because
                      #    there is no value prior to it to compute a
                      #    difference)
    print("There are %s data gaps. Filling data gaps with NaNs...\n" % num_data_gaps)
    
    # fill in the gaps #
    #create a DatetimeIndex ranging from the oldest time in the 'time' column
    #    to the newest time using an interval of 1 minute
    time_full = pd.date_range(start=df.time.min(), end=df.time.max(),freq='min')
    
    #create a DatetimeIndex using the full list of times above to serve as the
    #    new time array and index
    new_index = pd.Index(time_full, name="time")
    
    #set the index as 'time' for reindexing below
    df = df.set_index('time')
    
    #re-index the DataFrame using the new list of times, then reset the index.
    #    This will replace the original, incomplete list of timestamps while
    #    simultaneously filling in the elements for all other variables as
    #    NaNs where there were previously no records
    df = df.reindex(new_index).reset_index()
    
    #calculate the total downtime/uptime based on the number of missing reports


#Now we need to go through the records with a second pass, replacing wind
#    direction (wind speed) values for which the corresponding wind speed
#    (wind direction) value is a NaN, with a NaN. This is because we cannot
#    plot a wind barb for a given record without both wind speed AND direction.
for idx in range(len(df)):
    
    #where wind speed is NaN...
    if np.isnan(df.wind_speed[idx]) == True:
        #...wind direction must be NaN
        df.wind_dir[idx] = np.nan
    
    #where wind direction is NaN...
    elif np.isnan(df.wind_dir[idx]) == True:
        #...wind speed must be NaN
        df.wind_speed[idx] = np.nan
        
    else:
        pass

#now, count the column (any column except 'time') sum of NaNs; THIS will
#    tell you explicitly how many reports are missing and a better representation
#    of uptime/downtime
if np.all(df.notna()) == False:
    missing_reports = df.wind_dir.isna().sum()
    print("\nThere are %s missing reports in the dataset read in.\n" % missing_reports)

else:
    print("\nThere are no missing reports!\n")

##############################################################################


#separate each column in the DataFrame back into numpy.arrays (DatetimeIndex for
#    the 'time' column)
time = pd.to_datetime(np.array(df.time))
wind_spd = np.array(df.wind_speed, dtype=float)
wind_dir = np.array(df.wind_dir, dtype=float)


################ Checking 'mintime' / 'maxtime' Validity #################

#check to see if the user input the 'mintime' and 'maxtime' in the proper
#    format. This will account for occurrences with 'mintime' and/or
#    'maxtime' being empty strings (to indicate the beginning or ending of
#    the time frame, respectively) and requires the string length be 19
#    characters long. Pandas datetimeindex has the ability to read in
#    multiple formats, but this length requirement helps weed out a number
#    of potentially incompatible formats, making the creation of the
#    following error checkers more manageable!
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
    
#then check to see if 'mintime' and 'maxtime' are within the dataset that
#    was read in
#NOTE: the method min() and max() are functions of both DataFrames and
#      datetimeindex, so if we wanted, we could also do this: df.time.min()
if pd.to_datetime(mintime) < df.time.min() or pd.to_datetime(maxtime) > df.time.max():
    print("'mintime'/'maxtime' are outside the range of time.")
    
    #remind the user what their start/end time limits are
    print("The minimum start time is %s." % str(time.min()))
    print("The maximum end time is %s.\n" % str(time.max()))
    
    sys.exit()

#check that 'mintime' is explicitly less than 'maxtime'
if pd.to_datetime(mintime) >= pd.to_datetime(maxtime):
    print("'mintime' is greater than or equal to 'maxtime'.\n")
    sys.exit()    


######################## Setting the Time Frame ##########################

#set up the user-defined time frame
#Note: the method .get_loc() used below is a function of datetimeindex, NOT
#      DataFrames, so we must resort to using the datetimeindex array 'time'
#      that was created from the 'time' column in the dataframe
if mintime == "" and maxtime == "":
    #if 'mintime' and 'maxtime are empty strings, then the user must want to
    #    plot the entire dataset
    print("Plotting entire data set...\n")
    mintime = 0 #set 'mintime' to the first index in 'df' 
    maxtime = df.index[-1] #set 'maxtime' to the last index in 'df'
elif mintime == "" and maxtime != "":
    #if 'mintime' is an empty string, but 'maxtime' is not, then plot from the
    #    beginning of the dataset to the specified endtime (i.e. 'maxtime')
    mintime = 0
    maxtime = time.get_loc(pd.to_datetime(maxtime))
elif mintime != "" and maxtime == "":
    #if 'mintime' is not an empty string, but 'maxtime' is, then plot from the
    #    start time specified by 'mintime' to the end of the dataset
    mintime = time.get_loc(pd.to_datetime(mintime))
    maxtime = df.index[-1]
elif mintime != "" and maxtime != "":
    #if setting a user-defined time frame over which to plot, first convert
    #    the 'mintime' and 'maxtime' strings to pandas Timestamps
    mintime = time.get_loc(pd.to_datetime(mintime))
    maxtime = time.get_loc(pd.to_datetime(maxtime)) 


############################ Converting Data #############################

#convert wind speed to knots for barb plotting; color will be based on the
#    user-defined units

#converting wind speed for color purposes to user-defined units
if units == "mps":
    #save these units for the coloring of the barbs...
    spd_color = wind_spd
    #...but convert to knots for the barbs/flags
    wind_spd = 1.94384 * wind_spd
    
elif units == "kmph":
    #save these units for the coloring of the barbs...
    spd_color = wind_spd
    #...but convert to knots for the barbs/flags
    wind_spd = 0.53996 * wind_spd
elif units == "mph":
    #save these units for the coloring of the barbs...
    spd_color = wind_spd
    #...but convert to knots for the barbs/flags
    wind_spd = 0.868976 * wind_spd
elif units == "kts":
    #if plotting in knots, no need to convert anything
    spd_color = wind_spd
else:
    #on the off-chance the unit name checker does not catch an unaccepted name...
    print("Unit identifier not recognized. Check 'units' in USER OPTIONS.\n")
    sys.exit()


#convert to u and v components (matplotlib.pyplot.barbs requirement)
uwnd = -(wind_spd) * np.sin(np.deg2rad(wind_dir))
vwnd = -(wind_spd) * np.cos(np.deg2rad(wind_dir))



##############################################################################
###############################   OUTPUT   #################################
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

#not sure what this does, but supposedly it is necessary for larger datasets;
#    this will not plot without it
mpl.rcParams['agg.path.chunksize'] = 10000

plt.figure(figsize=(30,5))

#set the color map for the color bar
cmap = plt.cm.nipy_spectral

#set the y-axis label and range based on the user-defined units
if units == "mps": #plot wind speed in meters per second
    #set the range for the color bar
    #bounds = np.arange(0.,28,2)
    bounds = np.arange(0.,18.,2)
    
    #split the color bar levels by the range and interval
    norm = mpl.colors.BoundaryNorm(bounds,cmap.N)
        
    #plot
    ax = plt.barbs(time[::freq], wind_spd[::freq], uwnd[::freq], vwnd[::freq],
                   spd_color[::freq], length=7.5, cmap=cmap, norm=norm, lw=1,
                   pivot='middle', label='winds')
    
    ax.cmap.set_over('w')
    #ax.cmap.set_under('w')
    ax.set_clim(0., 25.)
    
    #plotting color bar
    cbar = plt.colorbar(ax,cmap=cmap,norm=norm,boundaries=bounds,ticks=bounds,extend='max',pad=0.015)
    
    #color bar label
    cbar.set_label("Wind Speed (m s$^-1$)", rotation=90)
    
elif units == "kmph": #plot wind speed in kilometers per hour
    #set the range for the color bar
    bounds = np.arange(0,110,10)
    
    #split the color bar levels by the range and interval
    norm = mpl.colors.BoundaryNorm(bounds,cmap.N)
        
    #plot
    ax = plt.barbs(time[::freq], wind_spd[::freq], uwnd[::freq], vwnd[::freq],
                   spd_color[::freq], length=7.5, cmap=cmap, norm=norm, lw=1,
                   pivot='middle', label='winds')
    
    ax.cmap.set_over('k')
    ax.set_clim(0., 90.)
    
    #plotting color bar
    cbar = plt.colorbar(ax,cmap=cmap,norm=norm,boundaries=bounds,ticks=bounds,extend='max',pad=0.015)
    
    #color bar label
    cbar.set_label("Wind Speed (km h$^-1$)", rotation=90)
    
elif units == "mph":    
    #set the range for the color bar
    bounds = np.arange(0,60,5)
    
    #split the color bar levels by the range and interval
    norm = mpl.colors.BoundaryNorm(bounds,cmap.N)
        
    #plot
    ax = plt.barbs(time[::freq], wind_spd[::freq], uwnd[::freq], vwnd[::freq],
                   spd_color[::freq], length=7.5, cmap=cmap, norm=norm, lw=1,
                   pivot='middle', label='winds')
    
    ax.cmap.set_over('k')
    ax.set_clim(0., 50.)
    
    #plotting color bar
    cbar = plt.colorbar(ax,cmap=cmap,norm=norm,boundaries=bounds,ticks=bounds,extend='max',pad=0.015)
    
    #color bar label
    cbar.set_label("Wind Speed (mi h$^-1$)", rotation=90)

elif units == "kts": #plot wind speed in knots
    #set the range for the color bar
    bounds = np.arange(0,60,5)
    
    #split the color bar levels by the range and interval
    norm = mpl.colors.BoundaryNorm(bounds,cmap.N)
        
    #plot
    ax = plt.barbs(time[::freq], wind_spd[::freq], uwnd[::freq], vwnd[::freq],
                   spd_color[::freq], length=7.5, cmap=cmap, norm=norm, lw=1,
                   pivot='middle', label='winds')
    
    ax.cmap.set_over('k')
    ax.set_clim(0., 51.)
    
    #plotting color bar
    cbar = plt.colorbar(ax,cmap=cmap,norm=norm,boundaries=bounds,ticks=bounds,extend='max',pad=0.015)
    
    #color bar label
    cbar.set_label("Wind Speed (kts)", rotation=90)
    
else:
    #if none of the conditions above are met, print an error statement
    #    pointing the user to the potential cause (i.e. spelling)
    raise ValueError("'units' not recognized. Check the spelling of 'units'.")


### UNIVERSAL PLOTTING PARAMETERS ###

#set y-axis limits/range
#plt.ylim(0., 50.)
plt.ylim(0., 20.)

#set the y-axis label
plt.ylabel("Wind Speed (kts)")

#set x-axis limits/range
plt.xlim(time[mintime], time[maxtime])

#add dashed grid lines
plt.grid(which='major', linestyle='--', color='dimgray')
plt.grid(which='minor', linestyle=':',color='gray')
#plt.gca().yaxis.grid(linestyle='--')

#setting up the tick mark locations and labels using an automatic locator and
#    formatter: Method #1...
# locator = mdates.AutoDateLocator(tz=None, minticks=5, maxticks=10,
#                                  interval_multiples=True)
# formatter = mdates.AutoDateFormatter(locator, tz=None, defaultfmt='%b %d %Y')
# plt.gca().xaxis.set_major_locator(locator)
# plt.gca().xaxis.set_major_formatter(formatter)

#... Method #2
locator = mdates.AutoDateLocator()
formatter = mdates.ConciseDateFormatter(locator)
plt.gca().xaxis.set_major_locator(locator)
plt.gca().xaxis.set_major_formatter(formatter)

#keep for archive purposes; no other use here for now
#plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%b %d %Y'))

#keep for archive purposes; no other use here for now    
# #Set x-axis major ticks to monthly interval
# plt.gca().xaxis.set_major_locator(mdates.MonthLocator())
# #ax.xaxis.set_major_locator(mdates.WeekdayLocator(byweekday=mdates.MONDAY))
# #Format x-tick labels as 3-letter month name and day number
# plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))

#set the plot's title
plt.title("%s : Winds" % site_ID, fontsize=14)

#set the x-axis label
plt.xlabel("Date / Time (UTC)")

# #set the plot legend
# plt.legend(loc='upper left', bbox_to_anchor=(1, 1), framealpha=0.95,
#            fancybox=True, shadow=True, fontsize=10)



##############################################################################
##############################   SAVE FIGURE    ##############################
##############################################################################

#save the figure
if units == "mps":
    plt.savefig('%s%s_winds-%s_%s.png' % (save_dir, site_ID, units, tag), \
                dpi=500, bbox_inches='tight')
elif units == "kmph":
    plt.savefig('%s%s_winds-%s_%s.png' % (save_dir, site_ID, units, tag), \
                dpi=500, bbox_inches='tight')
elif units == "mph":
    plt.savefig('%s%s_winds-%s_%s.png' % (save_dir, site_ID, units, tag), \
                dpi=500, bbox_inches='tight')
elif units == "kts":
    plt.savefig('%s%s_winds-%s_%s.png' % (save_dir, site_ID, units, tag), \
                dpi=500, bbox_inches='tight')

#show the figure that was generated
plt.show()


