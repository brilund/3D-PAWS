#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug  7 16:56:56 2020

@author: blund
"""


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

#This code reads and plots data from the UCAR/NCAR COMET 3D-PAWS system
#    anemometer.
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
#    July 7, 2020 - First Write
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
#    1. Change all variables in "USER OPTIONS" section to desired input
#           directory
#           site_ID
#           units: mps, kmph, mph, kts
#           save_dir
#           wildcard
#           tag
#    2. Run with "python WINDSPD_reader-plotter.py" in terminal, or open in
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
#import matplotlib.dates as mdates
import numpy as np
import glob
import pandas as pd
import sys
#import plotly.express as px
#from plotly.offline import plot



##############################################################################
############################    USER OPTIONS    ##############################
##############################################################################

#set the 'directory' variable to the absolute path where your data are stored;
#    don't forget the trailing forward slash!
directory = "/Users/blund/Documents/3D-PAWS/Data/CSA_3DPAWS01/wx_stn/windspd/"

#change this to the name of the site from which data are being plotted; this
#    will be used in the plot title as well as the name of the figure
site_ID = "CSA_3DPAWS01"

#change this to the name of the variable you want to plot; a list of
#    acceptable options can be found in the "How to Use:" section above
units = "mps"

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
save_dir = "/Users/blund/Documents/Python_Scripts/Figures/CSA_3DPAWS01/WINDSPD/"

#uncomment this option to read in EVERY file withing the directory you
#    specified above in 'directory'
wildcard = "*"
#uncomment this option to specify your own wildcard to select a subset of data
#    within the directory you specified above in 'directory'
# wildcard = "*2020*"

#set the time frame over which to plot (UTC); you must use the following
#    format: "YYYY-MM-DD HH:mm:ss"; to plot the whole dataset, set 'mintime'
#    and 'maxtime' to empty strings (e.g. mintime = ""), likewise, to plot
#    from the beginning of the time period, set mintime = "" and set 'maxtime'
#    to your end date/time. Vice versa for plotting to the end of the whole
#    time period
mintime = "2017-09-16 00:00:00"
maxtime = "2017-09-17 00:00:00"

#set the tag for which to add to the end of the figure name in the SAVE FIGURE
#    section at the bottom; leave this as an empty string if no tag is desired;
#    (e.g. set 'tag' to "2019-10" if you're plotting the month of October 2019)
tag = "20170916_raw-unsorted"



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

#find all data files within the specified directory
file_list = glob.glob(directory + wildcard)
#sort the list of files
file_list = sorted(file_list)

# you'll need to think about how to account for the different types of data
#    files here. This will be the place to begin, perhaps with some 'if'
#    statements

#Read in the data file(s) from the file_list
#Begin by initializing the lists that will store the data from each file for
#    each variable
month = []#calendar day
day = [] #calendar month
year = [] #calendar year
hour = [] #hour of day [UTC]
minute = [] #minutes after the hour [UTC]
second = [] #seconds after the minute [UTC]
wind_speed = [] #wind speed [m/s]

#loop through the list of files, collecting values from each file and
#    appending them to the appropriate list; each list will contain the data
#    for a single variable from all files
#set a counter for the number of lines with erroneous characters encountered
counter = 0
problem_files = [] #initialize a list to house files with erroneous characters
                   #    and partially overwritten lines
for file in file_list:
    with open(file, mode = "r") as f: #open the current file in read mode
        for line in f: #read each line of the file
            l = line.strip('\n').split() #remove carriage returns and whitespace
            if len(l) == 7: #this simple condition ought to weed out
                #    instances of erroneous characters at the end of a file or
                #    lines that were partially overwritten; the length, or # of
                #    elements in this variable 'l' should be equivalent to the
                #    # of columns in your data file; if not, the data line in
                #    question is likely a partially overwritten line or the
                #    last line in a file that did not record to 23:59 UTC and
                #    contains erroneous characters (\@\@\@\@\@\@\)
                month.append(l[0])
                day.append(l[1])
                year.append(l[2])
                hour.append(l[3])
                minute.append(l[4])
                second.append(l[5])
                wind_speed.append(l[6])
                
            else: #if the above condition of 8 elements is not met, then 
                #    count the occurrence and skip to the next line/iteration
                counter += 1
                
                #append the problematic filename to a list
                problem_files.append(file)
                continue
    f.close() #always close opened files

#print the number of files read in
print("%s files read" % len(file_list))

#print the number of lines skipped due to erroneous characters or partially
#    overwritten data lines
print("%s lines skipped\n" % counter)



##############################################################################
###########################    DATA PROCESSING    ############################
##############################################################################

############################ Checking Array Size #############################

#check that the number of elements in each array are the same
if len(month) == len(day) == len(year) == len(hour) == len(minute) == len(second) \
    == len(wind_speed):
    #if all arrays have the same number of elements, then the read/append
    #    conditions above were met and everything is good.
    print("Number of elements in each variable array are equal. Continue...\n")
else:
    #if all arrays do not have the same number of elements...
    print("Number of elements in each variable array are not equal. Program exited.\n")
    sys.exit() #... kill the program
    #consider telling the user where (i.e. what file) the above conditions was
    #    not met; this could pinpoint an otherwise unknown issue that needs
    #    addressing

##############################################################################
    

#convert variable lists to numpy arrays for simpler processing
month = np.array(month) #this is a string
day = np.array(day) #this is a string
year = np.array(year) #this is a string
hour = np.array(hour) #this is a string
minute = np.array(minute) #this is a string
second = np.array(second) #this is a string
wind_speed = np.array(wind_speed, dtype=float) #this is a float


############################ Converting Data #############################

#converting wind speed to user-defined units
if units == "mps":
    #if plotting in meters per second, no need to convert anything
    pass
elif units == "kmph":
    #convert to kilometers per hour
    wind_speed = 3.6 * wind_speed
elif units == "mph":
    #convert to miles per hous
    wind_speed = 2.23694 * wind_speed
elif units == "kts":
    #convert to knots
    wind_speed = 1.94384 * wind_speed
else:
    #on the off-chance the unit name checker does not catch an unaccepted name...
    print("Unit identifier not recognized. Check 'units' in USER OPTIONS.\n")
    sys.exit()


############################ Creating Timestamps #############################

#create an array containing the dates/times using the arrays above
#initialize the empty list to store these timestamps
time = []
for i in range(len(month)): #the variable could be any of the time variables
    #    (i.e. 'month', 'day', 'year', 'hour', 'minute') since each should be
    #    the same length. This is to include every time from every file.
    time.append('%s%s%s %s:%s:%s' % (year[i],month[i],day[i],hour[i],minute[i],second[i]))
    #the format above is one of many that pandas will accept

#convert the 'time' list to pandas DatetimeIndex
#    NOTE: time is not reported to the second in these files, but the line the
#    below will output the date-time elements in HH:MM:SS format so the
#    assumption is that records are reported at the top of the minute, though
#    not explicitly true. (Can I change the output format?)
#time = pd.to_datetime(time)

##############################################################################


#put all the data/time arrays into a DataFrame and set the index as the 'time'
#    column
df = pd.DataFrame({'time':time, 'wind_speed':wind_speed})


# ####################### Collect out-of-order timestamps #######################

# ''' This section has no bearing on plotting and data cleansing. It is intended
#     for catalogging and analysis of raw data purposes only.                 '''

# #find where out-of-order timestamps occur; this will only catch the first
# #    occurrence of a timestamp out of order, is essence, indicating the
# #    beginning of a section of data within the file such that time reset X
# #    number of minutes in the past
# #indices of times in the dataFrame where the difference between i+1 and i is
# #    negative (i.e. out of chronological order)
# idx = np.where(df.time.diff() < pd.Timedelta(minutes=0))

# #list of actual times in the dataFrame according to the indices above
# times_out_of_order = pd.to_datetime(np.array(df.time[pd.Index(idx[0])]))

# #the number of occurrences such that timestamps are out of chronological order
# num_out_of_order = len(times_out_of_order)

# #tell the user the absolute frequency of which timestamps are out of order
# print("Time reset %s times." % num_out_of_order)


# ##############################################################################


# #sort rows chronologically by 'time' (aka. the index variable)
# df = df.set_index('time').sort_index().reset_index()


# ########################## Massaging the timestamps ##########################

# #function for ensuring proper rounding of timestamps; the round() function
# #    operates such that when a timestamp falls half-way between two whole
# #    minutes, it chooses the even minute (e.g. 15:30 rounds to 16:00, but
# #    16:30 rounds to 16:00); we need every occurrence of a half-minute to round
# #    up. The function(s) below does that
# def half_up_minute(x):
#     m = (x - x.dt.floor('1T')).dt.total_seconds() < 30   # Round True Down, False Up
#     return x.where(m).dt.floor('1T').fillna(x.dt.ceil('1T'))

# # For indices:
# def half_up_minute_idx(idx):
#     m = (idx - idx.floor('1T')).total_seconds() < 30   # Round True Down, False Up
#     return pd.Index(np.select([m], [idx.floor('1T')], default=idx.ceil('1T')))

# #round each timestamp to the nearest minute
# df.time = half_up_minute(df.time)


# ####################### Handling Duplicate Timestamps ########################

# #check for duplicated timestamps
# if pd.Index(df.time).has_duplicates == True:
    
#     #keep a list of each duplicated timestamp; the method below will give ALL
#     #    instances of a duplicated timestamp, so if there are 3 occurrences
#     #    for the same time, two will appear in the list; by default the first
#     #    occurrence of a duplicated timestamp is False
#     duplicate_times = pd.to_datetime(np.array(df.time[pd.Index(df.time).duplicated()]))
    
#     #convert the list of duplicated times to strings to later be output to a
#     #    text file
#     duplicate_times = [str(t) for t in duplicate_times]
    
#     #get the number of duplicated times; might also be useful to output
#     num_duplicate_times = len(duplicate_times)
    
#     #print the number of duplicate timestamps to the user
#     print("There are %s duplicate timestamps. Removing duplicated timestamps and associated data, but preserving the first occurrence.\n" % num_duplicate_times)
    
#     #remove any and all rows that have the same timestamp (i.e. where there are
#     #    duplicated times), but preserve the first occurrence; the following line
#     #    first resets the index variable such that 'time' is a regular column like
#     #    the rest of the data, then drops rows based solely on duplicates in 'time'
#     #    (i.e. subset='time'), but keeps the first occurrence of any duplications
#     #    (i.e. keep='first'), then sets the index back to the 'time' column (this
#     #    will be necessary later on)
#     df = df.drop_duplicates(subset='time', keep='first')
#     #    NOTE: the above method assumes the first occurrence of a duplicated timestamp
#     #          contains the correct/valid data, which is not necessarily true. To
#     #          be handled later...
    
# else:
#     print("There are no duplicated timestamps.\n")

# #by now, data should be sorted chronologically and rid of any duplicated
# #    timestamps.

    
# ########################### Filling Gaps with NaNs ###########################
    
# #Now we check to see if there are any missing report times. Timestamps should
# #    be monotonically increasing by 1 minute intervals. Since the interval is
# #    not exactly 1 minute (sometimes it is 61 seconds), the total number of
# #    data gaps is not perfectly representative of the exact number of data
# #    gaps. Due to the sublte inconsistencies in time reporting intervals and
# #    the time rounding method, the line below will consider instances such as...
# #    2:55:29, 2:56:29, 2:57:30 rounding to 2:55:00, 2:56:00, 2:58:00...
# #    the line below will include 2:57 as a data gap when in fact, this is not
# #    necessarily true
# num_data_gaps = (df.time.diff() > pd.Timedelta(minutes=1)).sum()
# #NOTE: the value contained in 'num_data_gaps' is not necessarily representative
# #      of the number of missing reports because each data gap could contain
# #      multiple missing reports (e.g. a time gap from 14:10 UTC to 14:15 UTC
# #      counts as only 1 data gap but accounts for 4 missing minutely reports
# #      {14:11, 14:12, 14:13, and 14:14 UTC})

# if num_data_gaps > 0: #NaNs are not included in 'num_data_gaps'
#     print("There are %s data gaps. Filling data gaps with NaNs...\n" % num_data_gaps)
    
#     # fill in the gaps #
#     #create a DatetimeIndex ranging from the oldest time in the 'time' column
#     #    to the newest time using an interval of 1 minute
#     time_full = pd.date_range(start=df.time.min(), end=df.time.max(),freq='min')
    
#     #create a DatetimeIndex using the full list of times above to serve as the
#     #    new time array and index
#     new_index = pd.Index(time_full, name="time")
    
#     #set the index as 'time' for reindexing below
#     df = df.set_index('time')
    
#     #re-index the DataFrame using the new list of times, then reset the index.
#     #    This will replace the original, incomplete list of timestamps while
#     #    simultaneously filling in the elements for all other variables as
#     #    NaNs where there were previously no records
#     df = df.reindex(new_index).reset_index()
    
#     #now, count the column (any column) sum of NaNs; THIS will tell you
#     #    explicitly how many reports are missing and a better representation
#     #    of uptime/downtime
#     missing_reports = df.wind_speed.isna().sum()
#     print("There are %s missing reports in the dataset read in.\n" % missing_reports)
    
#     #calculate the total downtime/uptime based on the number of missing reports
    
# else:
#     print("There are no missing reports!\n")

# ##############################################################################
    

#separate each column in the DataFrame back into numpy.arrays (DatetimeIndex for
#    the 'time' column)
time = np.array(df.time, dtype=str)
wind_speed = np.array(df.wind_speed, dtype=float)


# ################## Checking 'mintime' / 'maxtime' Validity ###################

# #check to see if the user input the 'mintime' and 'maxtime' in the proper format.
# #    This will account for occurrences with 'mintime' and/or 'maxtime' being
# #    empty strings (to indicate the beginning or ending of the time frame,
# #    respectively) and requires the string length be 19 characters long. Pandas
# #    datetimeindex has the ability to read in multiple formats, but this length
# #    requirement helps weed out a number of potentially incompatible formats,
# #    making the creation of the following error checkers more manageable!
# if mintime == "" and len(maxtime) == 19:
#     try:
#         pd.to_datetime(maxtime, format='%Y-%m-%d %H:%M:%S')
#     except ValueError:
#         raise ValueError("Incorrect format for 'maxtime'; should be YYYY-MM-DD HH:mm:ss")
#     except TypeError:
#         raise TypeError("Incorrect format for 'maxtime'; should be YYYY-MM-DD HH:mm:ss")
    
# elif maxtime == "" and len(mintime) == 19:
#     try:
#         pd.to_datetime(mintime, format='%Y-%m-%d %H:%M:%S')
#     except ValueError:
#         raise ValueError("Incorrect format for 'mintime'; should be YYYY-MM-DD HH:mm:ss")
#     except TypeError:
#         raise TypeError("Incorrect format for 'mintime'; should be YYYY-MM-DD HH:mm:ss")
    
# elif len(mintime) == 19 and len(mintime) == 19: #they should include 19 characters
#         try:
#             pd.to_datetime(mintime, format='%Y-%m-%d %H:%M:%S')
#             pd.to_datetime(maxtime, format='%Y-%m-%d %H:%M:%S')
#         except ValueError:
#             raise ValueError("Incorrect format for 'mintime'/'maxtime'; should be YYYY-MM-DD HH:mm:ss")
#         except TypeError:
#             raise TypeError("Incorrect format for 'mintime'/'maxtime'; should be YYYY-MM-DD HH:mm:ss")
            
# elif mintime == "" and maxtime == "":
#     pass

# else:
#     #anything that is not an empty string or 19 characters in length
#     #    automatically fails the checks
#     raise TypeError("Incorrect format for 'mintime'; should be YYYY-MM-DD HH:mm:ss")
    
# #then check to see if 'mintime' and 'maxtime' are within the dataset that was
# #    read in
# #Note: the method min() and max() are functions of both DataFrames and
# #      datetimeindex, so if we wanted, we could also do this: df.time.min()
# if pd.to_datetime(mintime) < df.time.min() or pd.to_datetime(maxtime) > df.time.max():
#     print("'mintime'/'maxtime' are outside the range of time.")
#     print("The minimum start time is %s." % str(time.min()))
#     print("The maximum end time is %s.\n" % str(time.max()))
#     #remind the user what their start/end time limits are^
#     sys.exit()

# #check that 'mintime' is explicitly less than 'maxtime'
# if pd.to_datetime(mintime) >= pd.to_datetime(maxtime):
#     print("'mintime' is greater than or equal to 'maxtime'.\n")
#     sys.exit()    


# ########################## Setting the Time Frame ############################

# #set up the user-defined time frame
# #Note: the method .get_loc() used below is a function of datetimeindex, NOT
# #      DataFrames, so we must resort to using the datetimeindex array 'time'
# #      that was created from the 'time' column in the dataframe
# if mintime == "" and maxtime == "":
#     #if 'mintime' and 'maxtime are empty strings, then the user must want to
#     #    plot the entire dataset
#     print("Plotting entire data set...\n")
#     mintime = 0 #set 'mintime' to the index of the first time in 'time' 
#     maxtime = -1 #set 'maxtime' to the index of the last time in 'time'
# elif mintime == "" and maxtime != "":
#     #if 'mintime' is an empty string, but 'maxtime' is not, then plot from the
#     #    beginning of the dataset to the specified endtime (i.e. 'maxtime')
#     mintime = 0
#     maxtime = time.get_loc(pd.to_datetime(maxtime))
# elif mintime != "" and maxtime == "":
#     #if 'mintime' is not an empty string, but 'maxtime' is, then plot from the
#     #    start time specified by 'mintime' to the end of the dataset
#     mintime = time.get_loc(pd.to_datetime(mintime))
#     maxtime = -1
# elif mintime != "" and maxtime != "":
#     #if setting a user-defined time frame over which to plot, first convert
#     #    the 'mintime' and 'maxtime' strings to pandas Timestamps
#     mintime = time.get_loc(pd.to_datetime(mintime))
#     maxtime = time.get_loc(pd.to_datetime(maxtime))   


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
    df['windspd_avg'] = df.iloc[:,1].rolling(window=avg_window).mean().shift(-(avg_window-1))
    
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
    df['windspd_avg'] = df.iloc[:,1].rolling(window=avg_window).mean().shift(-(avg_window-1))

elif averaged == "resampled":
    #resampling; there is no need to do anything here, but the "resampled"
    #    option will plot every nth raw data point where 'n' is the averaging
    #    window ("avg_window") set by the user
    print("Plotting every %s data points (minutes)..." % avg_window)

#NOTE: we need not account for the potential of "averaged" being an unaccepted
#      option because the error checker above at the beginning of the DATA
#      PROCESSING section will handle that exception by raising an error



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
#pandas plotting

#not sure what this does, but supposedly it is necessary for larger datasets;
#    this will not plot without it
mpl.rcParams['agg.path.chunksize'] = 10000

#plot data based on the user-selected varible; plot parameters within these
#    'if' statements are those specific to each variable
if units == "mps": #plot wind speed in meters per second
    #plot
    if averaged == False:
        #plotting all raw data
        ax = df[25327:26590].plot(x='time', y='wind_speed', color='b', label='wind_%s' % units,
                     figsize=(30,5))
    elif averaged == True:
        #plotting running averaged data
        ax = df.plot(x='time', y='windspd_avg', color='b', label='%s_%s-min' % (units, avg_window),
                     figsize=(30,5))
    elif averaged == "static":
        #plotting static averaged data (fewer data points)
        ax = df[::avg_window].plot(x='time', y='windspd_avg', color='b',label='%s_%s-min-%s' % (units, avg_window, averaged),
                     figsize=(30,5))
    elif averaged == "resampled":
        #plotting every nth raw data point (fewer data points)
        ax = df[::avg_window].plot(x='time', y='wind_speed', color='b', label='wind_%s_%s' % (units, averaged),
                     figsize=(30,5))
    else:
        #plotting all raw data
        ax = df.plot(x='time', y='wind_speed', color='b', label='wind_%s' % units,
                     figsize=(30,5))
    
    #set y-axis limits/range
    ax.set_ylim(0., 10.)
    
    #set the y-axis label
    plt.ylabel("Wind Speed (m s$^-1$)")
    
elif units == "kmph": #plot wind speed in kilometers per hour
    if averaged == False:
        #plotting all raw data
        ax = df.plot(x='time', y='wind_speed', color='b', label='wind_%s' % units,
                     figsize=(30,5))
    elif averaged == True:
        #plotting running averaged data
        ax = df.plot(x='time', y='windspd_avg', color='b', label='%s_%s-min' % (units, avg_window),
                     figsize=(30,5))
    elif averaged == "static":
        #plotting static averaged data (fewer data points)
        ax = df[::avg_window].plot(x='time', y='windspd_avg', color='b',label='%s_%s-min-%s' % (units, avg_window, averaged),
                     figsize=(30,5))
    elif averaged == "resampled":
        #plotting every nth raw data point (fewer data points)
        ax = df[::avg_window].plot(x='time', y='wind_speed', color='b', label='wind_%s_%s' % (units, averaged),
                     figsize=(30,5))
    else:
        #plotting all raw data
        ax = df.plot(x='time', y='wind_speed', color='b', label='wind_%s' % units,
                     figsize=(30,5))
    
    #set y-axis limits/range
    ax.set_ylim(0., 90.)
    
    #set the y-axis label
    plt.ylabel("Wind Speed (km h$^-1$)")
    
elif units == "mph":
    if averaged == False:
        #plotting all raw data
        ax = df.plot(x='time', y='wind_speed', color='b', label='wind_%s' % units,
                     figsize=(30,5))
    elif averaged == True:
        #plotting running averaged data
        ax = df.plot(x='time', y='windspd_avg', color='b', label='%s_%s-min' % (units, avg_window),
                     figsize=(30,5))
    elif averaged == "static":
        #plotting static averaged data (fewer data points)
        ax = df[::avg_window].plot(x='time', y='windspd_avg', color='b',label='%s_%s-min-%s' % (units, avg_window, averaged),
                     figsize=(30,5))
    elif averaged == "resampled":
        #plotting every nth raw data point (fewer data points)
        ax = df[::avg_window].plot(x='time', y='wind_speed', color='b', label='wind_%s_%s' % (units, averaged),
                     figsize=(30,5))
    else:
        #plotting all raw data
        ax = df.plot(x='time', y='wind_speed', color='b', label='wind_%s' % units,
                     figsize=(30,5))
    
    #set y-axis limits/range
    ax.set_ylim(0., 50.)
    
    #set the y-axis label
    plt.ylabel("Wind Speed (m h$^-1$)")

elif units == "kts": #plot wind speed in knots
    if averaged == False:
        #plotting all raw data
        ax = df.plot(x='time', y='wind_speed', color='b', label='wind_%s' % units,
                     figsize=(30,5))
    elif averaged == True:
        #plotting running averaged data
        ax = df.plot(x='time', y='windspd_avg', color='b', label='%s_%s-min' % (units, avg_window),
                     figsize=(30,5))
    elif averaged == "static":
        #plotting static averaged data (fewer data points)
        ax = df[::avg_window].plot(x='time', y='windspd_avg', color='b',label='%s_%s-min-%s' % (units, avg_window, averaged),
                     figsize=(30,5))
    elif averaged == "resampled":
        #plotting every nth raw data point (fewer data points)
        ax = df[::avg_window].plot(x='time', y='wind_speed', color='b', label='wind_%s_%s' % (units, averaged),
                     figsize=(30,5))
    else:
        #plotting all raw data
        ax = df.plot(x='time', y='wind_speed', color='b', label='wind_%s' % units,
                     figsize=(30,5))
    
    #set y-axis limits/range
    ax.set_ylim(0., 50.)
    
    #set the y-axis label
    plt.ylabel("Wind Speed (kts)")
    
else:
    #if none of the conditions above are met, print an error statement
    #    pointing the user to the potential cause (i.e. spelling)
    print("'units' not recognized. Check the spelling of 'units'. Program exiting...")
    sys.exit()



#############################
#plotly plotting attempt

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
#ax.set_xlim(time[mintime], time[maxtime])

#set the plot's title
plt.title("%s : Anemometer" % site_ID, fontsize=14)

#set the x-axis label
plt.xlabel("Date / Time (UTC)")

#set the plot legend
plt.legend(loc='upper left', bbox_to_anchor=(1, 1), framealpha=0.95,
            fancybox=True, shadow=True, fontsize=10)



##############################################################################
##############################   SAVE FIGURE    ##############################
##############################################################################

#save the figure with a name based on the user-selected variable
if units == "mps":
    if averaged == False:
        plt.savefig('%s%s_wind-speed-%s_%s.png' % (save_dir, site_ID, units, tag), \
                    dpi=500, bbox_inches='tight')
    elif averaged == True:
        plt.savefig('%s%s_wind-speed-%s_%s-min_%s.png' % (save_dir, site_ID, units, avg_window, tag), \
                    dpi=500, bbox_inches='tight')
    elif averaged == "static":
        plt.savefig('%s%s_wind-speed-%s_%s-min-%s_%s.png' % (save_dir, site_ID, units, avg_window, averaged, tag), \
                    dpi=500, bbox_inches='tight')
    elif averaged == "resampled":
        plt.savefig('%s%s_wind-speed-%s_%s-min-%s_%s.png' % (save_dir, site_ID, units, avg_window, averaged, tag), \
                    dpi=500, bbox_inches='tight')
    else:
        plt.savefig('%s%s_wind-speed-%s_%s.png' % (save_dir, site_ID, units, tag), \
                    dpi=500, bbox_inches='tight')

elif units == "kmph":
    if averaged == False:
        plt.savefig('%s%s_wind-speed-%s_%s.png' % (save_dir, site_ID, units, tag), \
                    dpi=500, bbox_inches='tight')
    elif averaged == True:
        plt.savefig('%s%s_wind-speed-%s_%s-min_%s.png' % (save_dir, site_ID, units, avg_window, tag), \
                    dpi=500, bbox_inches='tight')
    elif averaged == "static":
        plt.savefig('%s%s_wind-speed-%s_%s-min-%s_%s.png' % (save_dir, site_ID, units, avg_window, averaged, tag), \
                    dpi=500, bbox_inches='tight')
    elif averaged == "resampled":
        plt.savefig('%s%s_wind-speed-%s_%s-min-%s_%s.png' % (save_dir, site_ID, units, avg_window, averaged, tag), \
                    dpi=500, bbox_inches='tight')
    else:
        plt.savefig('%s%s_wind-speed-%s_%s.png' % (save_dir, site_ID, units, tag), \
                    dpi=500, bbox_inches='tight')
    
elif units == "mph":
    if averaged == False:
        plt.savefig('%s%s_wind-speed-%s_%s.png' % (save_dir, site_ID, units, tag), \
                    dpi=500, bbox_inches='tight')
    elif averaged == True:
        plt.savefig('%s%s_wind-speed-%s_%s-min_%s.png' % (save_dir, site_ID, units, avg_window, tag), \
                    dpi=500, bbox_inches='tight')
    elif averaged == "static":
        plt.savefig('%s%s_wind-speed-%s_%s-min-%s_%s.png' % (save_dir, site_ID, units, avg_window, averaged, tag), \
                    dpi=500, bbox_inches='tight')
    elif averaged == "resampled":
        plt.savefig('%s%s_wind-speed-%s_%s-min-%s_%s.png' % (save_dir, site_ID, units, avg_window, averaged, tag), \
                    dpi=500, bbox_inches='tight')
    else:
        plt.savefig('%s%s_wind-speed-%s_%s.png' % (save_dir, site_ID, units, tag), \
                    dpi=500, bbox_inches='tight')
    
elif units == "kts":
    if averaged == False:
        plt.savefig('%s%s_wind-speed-%s_%s.png' % (save_dir, site_ID, units, tag), \
                    dpi=500, bbox_inches='tight')
    elif averaged == True:
        plt.savefig('%s%s_wind-speed-%s_%s-min_%s.png' % (save_dir, site_ID, units, avg_window, tag), \
                    dpi=500, bbox_inches='tight')
    elif averaged == "static":
        plt.savefig('%s%s_wind-speed-%s_%s-min-%s_%s.png' % (save_dir, site_ID, units, avg_window, averaged, tag), \
                    dpi=500, bbox_inches='tight')
    elif averaged == "resampled":
        plt.savefig('%s%s_wind-speed-%s_%s-min-%s_%s.png' % (save_dir, site_ID, units, avg_window, averaged, tag), \
                    dpi=500, bbox_inches='tight')
    else:
        plt.savefig('%s%s_wind-speed-%s_%s.png' % (save_dir, site_ID, units, tag), \
                    dpi=500, bbox_inches='tight')

#show the figure that was generated
plt.show()


