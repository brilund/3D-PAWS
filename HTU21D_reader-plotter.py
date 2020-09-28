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

#This code reads and plots data from the UCAR/NCAR COMET 3D-PAWS system HTU21D
#    humidity sensor.
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
#    Jun 22, 2020 - First Write
#    Jun 24, 2020 - Added some more plotting autonomy (i.e. simply change
#                   'var_name' in the USER OPTIONS section and all plot setup
#                   will be done automatically [e.g. y-axis title, y-axis
#                   range, etc.])
#    Jun 26, 2020 - Added some error checkers to validate the format and logic
#                   of the user's start and end time inputs ('mintime' and
#                   'maxtime')
#    Jun 30, 2020 - Added ability to collect the number of missing reports,
#                   store a list of files with erroneous characters and/or
#                   overwritten lines of data, and collect the duplicated
#                   timestamps as well as the number of them
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
#       a. other...
#       b. other...
#    4. Use prompts for user input??? This will ensure the options are changed
#       when the program is run for any user, but could also be tedious to
#       have to enter those options every time; perhaps a parameter file is
#       better???
#    5. Separate major sections into callable functions: reader, processor,
#       output, plotter, etc.
#
#
#How to Use:
#    1. Change all variables in "USER OPTIONS" section to desired input
#           directory
#           site_ID
#           var_name: temp_C, temp_F, rel_hum
#           save_dir
#           wildcard
#           tag
#    2. Run with "python HTU21D_reader-plotter.py" in terminal, or open in
#       Spyder and run from there.
#
#
#Example header from files --> no file header(s)!!! (this could change...)
#
#Example data from files:
#    
#
#
#NOTES: the y-axis range for some variables will be site-dependent. These are
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
#                plt.savefig('%s%s_HTU21D_temp-C_2019.png' % (save_dir, site_ID), dpi=500, \
#                bbox_inches='tight')


##############################################################################
#########################    IMPORTING MODULES    ############################
##############################################################################

import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
import glob
import pandas as pd
import sys



##############################################################################
############################    USER OPTIONS    ##############################
##############################################################################

#set the 'directory' variable to the absolute path where your data are stored;
#    don't forget the trailing forward slash!
directory = "/Users/blund/Documents/3D-PAWS/Data/WMO_HIGHWAY_01/data/htu21d/"

#change this to the name of the site from which data are being plotted; this
#    will be used in the plot title as well as the name of the figure
site_ID = "CSA_3DPAWS01"

#change this to the name of the variable you want to plot; a list of
#    acceptable options can be found in the "How to Use:" section above
var_name = "temp_C"

#specify the FULL file path to the directory in which to save your figures;
#    don't forget to include the trailing forward slash!
save_dir = "/Users/blund/Documents/Python_Scripts/Figures/CSA_3DPAWS01/HTU21D/"

#uncomment this option to read in EVERY file withing the directory you
#    specified above in 'directory'
wildcard = "*"
#uncomment this option to specify your own wildcard to select a subset of data
#    within the directory you specified above in 'directory
#wildcard = "*201902*"

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

#check to see if the user-input variable is from the list provided
if var_name == "temp_C" or var_name == "temp_F" or var_name == "rel_hum":
    pass
else:
    print("'%s' is not an accepted variable name\n" % var_name)
    print("Accepted variable names are...")
    print("'rel_hum' for relative humidity (%)")
    print("'temp_C' for temperature (deg C)")
    print("'temp_F' for temperature (deg F)")
    sys.exit()

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
hour = [] #hour in UTC
minute = [] #minutes after the hour [UTC]
temp_C = [] #temperature in degrees Celcius
temp_F = [] #temperature in degrees Fahrenheit 
rel_hum = [] #relative humidity (%)

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
            if len(l) == 8: #this simple condition ought to weed out
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
                temp_C.append(l[5])
                temp_F.append(l[6])
                rel_hum.append(l[7])
            else: #if the above condition of 8 elements is not met, then 
                #    count the occurrence and skip to the next line/iteration
                counter += 1 #consider appending the 'file' to a list meant to
                
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
if len(month) == len(day) == len(year) == len(hour) == len(minute) == len(temp_C) \
    == len(temp_F) == len(rel_hum):
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
temp_C = np.array(temp_C, dtype=float) #this is a float
temp_F = np.array(temp_F, dtype=float) #this is a float
rel_hum = np.array(rel_hum, dtype=float) #this is a float


############################ Creating Timestamps #############################

#create an array containing the dates/times using the arrays above
#initialize the empty list to store these timestamps
time = []
for i in range(len(month)): #the variable could be any of the time variables
    #    (i.e. 'month', 'day', 'year', 'hour', 'minute') since each should be
    #    the same length. This is to include every time from every file.
    time.append('%s%s%s %s:%s' % (year[i],month[i],day[i],hour[i],minute[i]))
    #the format above is one of many that pandas will accept

#convert the 'time' list to pandas DatetimeIndex
#    NOTE: time is not reported to the second in these files, but the line the
#    below will output the date-time elements in HH:MM:SS format so the
#    assumption is that records are reported at the top of the minute, though
#    not explicitly true. (Can I change the output format?)
time = pd.to_datetime(time)

##############################################################################


#put all the data/time arrays into a DataFrame and set the index as the 'time'
#    column
df = pd.DataFrame({'time':time, 'temp_C':temp_C, 'temp_F':temp_F, 'rel_hum':rel_hum})


####################### Collect out-of-order timestamps #######################

''' This section has no bearing on plotting and data cleansing. It is intended
    for catalogging and analysis of raw data purposes only.                 '''

#find where out-of-order timestamps occur; this will return any and all
#    datetimeIndex that is out of order
#indices of times in the dataFrame where the difference between i+1 and i is
#    negative (i.e. out of chronological order)
idx = np.where(df.time.diff() < pd.Timedelta(minutes=0))

#list of actual times in the dataFrame according to the indices above
times_out_of_order = pd.to_datetime(np.array(df.time[pd.Index(idx[0])]))

#the number of occurrences such that timestamps are out of chronological order
num_out_of_order = len(times_out_of_order)

#tell the user the absolute frequency of which timestamps are out of order
print("Time reset %s times." % num_out_of_order)


##############################################################################


#sort rows chronologically by 'time' by setting 'time' as the index variable
df = df.set_index('time').sort_index().reset_index()


####################### Handling Duplicate Timestamps ########################

#check for duplicated timestamps
if pd.Index(df.time).has_duplicates == True:
    
    #keep a list of each duplicated timestamp; the method below will give ALL
    #    instances of a duplicated timestamps, so if there are 3 occurrences
    #    for the same time, two will appear in the list; by default the first
    #    occurrence of a duplicated timestamp is False
    duplicate_times = pd.to_datetime(np.array(df.time[pd.Index(df.time).duplicated()]))
    
    #remove all but the first occurrence of duplicate timestamps and store
    #    them in a new array which will serve as an addition to an output file
    #    later on
    duplicates = duplicate_times.drop_duplicates(keep='first')
    
    #convert the list of duplicated times to strings to later be output to a
    #    text file
    duplicate_times = [str(t) for t in duplicate_times]
    
    #get the number of duplicated times; might also be useful to output
    num_duplicate_times = len(duplicate_times)
    
    #print the number of duplicate timestamps to the user
    print("There are %s duplicate timestamps. Removing duplicated timestamps and associated data, but preserving the first occurrence.\n" % num_duplicate_times)
    
    #remove any and all rows that have the same timestamp (i.e. where there are
    #    duplicated times), but preserve the first occurrence; the following line
    #    first resets the index variable such that 'time' is a regular column like
    #    the rest of the data, then drops rows based solely on duplicates in 'time'
    #    (i.e. subset='time'), but keeps the first occurrence of any duplications
    #    (i.e. keep='first'), then sets the index back to the 'time' column (this
    #    will be necessary later on)
    df = df.drop_duplicates(subset='time', keep='first')
    #    NOTE: the above method assumes the first occurrence of a duplicated timestamp
    #          contains the correct/valid data, which is not necessarily true. To
    #          be handled later...
    
    #reorder the indices such that they follow a monotonically increasing order
    #    from 0 in the event that rows were removed from the above lines
    df = df.reset_index().drop(columns='index')
    
else:
    print("There are no duplicated timestamps.\n")

#by now, data should be sorted chronologically and rid of any duplicated
#    timestamps.
    
    
########################### Filling Gaps with NaNs ###########################
    
#Now we check to see if there are any missing report times. Timestamps should
#    be monotonically increasing by 1 minute intervals. The following line
#    will find the number of occurrences such that the difference between
#    timestamps is not equal to 1 minute.
num_data_gaps = (df.time.diff() > pd.Timedelta(minutes=1)).sum()
#NOTE: the value contained in 'num_data_gaps' is not necessarily representative
#      of the number of missing reports because each data gap could contain
#      multiple missing reports (e.g. a time gap from 14:10 UTC to 14:15 UTC
#      counts as only 1 data gap but accounts for 4 missing minutely reports
#      {14:11, 14:12, 14:13, and 14:14 UTC})

if num_data_gaps > 0: #NaNs are not included in 'num_data_gaps'
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
    
    #now, count the column (any column) sum of NaNs; THIS will tell you
    #    explicitly how many reports are missing and a better representation
    #    of uptime/downtime
    missing_reports = df.temp_C.isna().sum()
    print("There are %s missing reports in the dataset read in.\n" % missing_reports)

    #calculate the total downtime/uptime based on the number of missing reports
    total = pd.Timedelta(len(df), unit='m')
    uptime = pd.Timedelta((len(df) - missing_reports), unit='m')
    uptime_percent = round((1 - (float(missing_reports) / float(len(df)))) * 100., 1)
    print("Total uptime is %s out of %s (%s%%).\n" % (uptime,total,uptime_percent))
    
else:
    print("There are no missing reports!\n")

##############################################################################


#separate each column in the DataFrame back into numpy.arrays (DatetimeIndex for
#    the 'time' column)
time = pd.to_datetime(np.array(df.time))
temp_C = np.array(df.temp_C, dtype=float)
temp_F = np.array(df.temp_F, dtype=float)
rel_hum = np.array(df.rel_hum, dtype=float)

# #create a masked array from the variables above that masks all data except
# #    for the bad values
# masked_temp_C = np.ma.masked_not_equal(temp_C, 27.08)


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


######################### Uptime within Time Frame ########################### 

#calculate the total uptime based on the number of missing reports,
#    but within the time frame ('mintime' and 'maxtime') set by the user
missing_reports = df.temp_C[mintime:maxtime].isna().sum()
total = pd.Timedelta(len(df.index[mintime:maxtime]), unit='m')
uptime = pd.Timedelta((len(df.index[mintime:maxtime]) - missing_reports), unit='m')
uptime_percent = round((1 - (float(missing_reports) / float(len(df[mintime:maxtime])))) * 100., 1)
print("Uptime during the time frame is %s out of %s (%s%%).\n" % (uptime,total,uptime_percent))



##############################################################################
################################   OUTPUT   ##################################
##############################################################################

#placeholder section for generating a file that will store all kinds of stats,
#    metrics and other metadata for analysis



##############################################################################
###############################   PLOTTING   #################################
##############################################################################

''' Include an option for one variable to be plotted or to plot all variables
    in their own separate figures '''
#size of plot
plt.figure(figsize=(30,5))

# ######################
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
# ######################

# #plot
# #plt.plot(time[:1000], temp_C[:1000], color='b', label="Temp C")
# plt.plot(time[:], rel_hum[:], color='b', label=var_name)#, marker='+', linestyle='None', ms=1.)
# #plt.plot(time[168116:481414], masked_temp_C[168116:481414], color='r', label="Bad Values", linestyle='None', marker='.', ms=1.5)

# #plt.ylim(0., 100.)
# # #plt.xlim('2017-08-31','2017-09-01')

# #add dashed grid lines
# plt.grid(linestyle='--')

# #title
# plt.title("CSA_3DPAWS01 : HTU21D Sensor", fontsize=12)

# # #set the x- and y-axis dimensions based on user-defined time frame
# # plt.axis([mintime,maxtime,minhgt,maxhgt])

# #x-axis label
# plt.xlabel("Time (UTC)")

# #rotate the x-axis tick labels for a better fit
# plt.xticks(fontsize=10, rotation=30,)

# #y-axis label
# plt.ylabel("Relative Humidity (%)")
# #plt.ylabel("Pressure ($^o$F)")

# #legend
# plt.legend(loc='upper left', bbox_to_anchor=(1, 1), framealpha=0.95,
#             fancybox=True, shadow=True, fontsize=10)

#######################
#attempting pandas plotting

#plot data based on the user-selected varible; plot parameters within these
#    'if' statements are those specific to each variable
if var_name == "temp_C": #plot temperature in Celsius
    ax = df.plot(x='time', y=var_name, color='b', label=var_name, figsize=(30,5))
    
    #set y-axis limits/range
    ax.set_ylim(-20., 45.)
    
    #set the y-axis label
    plt.ylabel("Temperature ($^o$C)")
    
elif var_name == "temp_F": #plot temperature in Fahrenheit
    ax = df.plot(x='time', y=var_name, color='b', label=var_name, figsize=(30,5))
    
    #set y-axis limits/range
    ax.set_ylim(-10., 110.)
    
    #set the y-axis label
    plt.ylabel("Temperature ($^o$F)")
    
elif var_name == "rel_hum": #plot relative humidity (%)
    ax = df.plot(x='time', y=var_name, color='b', label=var_name, figsize=(30,5))
    
    #set y-axis limits/range
    ax.set_ylim(0., 100.)
    
    #set the y-axis label
    plt.ylabel("Relative Humidity (%)")
    
else:
    #if none of the conditions above are met, print an error statement
    #    pointing the user to the potential cause (i.e. spelling)
    print("Variable name not found. Check the spelling of 'var_name'. Program exiting...")
    sys.exit()

### UNIVERSAL PLOTTING PARAMETERS ###
    
#add dashed grid lines
plt.grid(which='major', linestyle='--', color='dimgray')
plt.grid(which='minor', linestyle=':',color='gray')

#set x-axis limits/range
ax.set_xlim(time[mintime], time[maxtime])

#set the plot's title
plt.title("%s : HTU21D Sensor" % site_ID, fontsize=12)

#set the x-axis label
plt.xlabel("Date / Time (UTC)")

#set the plot legend
plt.legend(loc='upper left', bbox_to_anchor=(1, 1), framealpha=0.95,
            fancybox=True, shadow=True, fontsize=10)



##############################################################################
##############################   SAVE FIGURE    ##############################
##############################################################################

# #save the figure with a name based on the user-selected variable
# if var_name == "temp_C":
#     plt.savefig('%s%s_HTU21D_temp-C_%s.png' % (save_dir, site_ID, tag),
#                 dpi=500, bbox_inches='tight')
# elif var_name == "temp_F":
#     plt.savefig('%s%s_HTU21D_temp-F_%s.png' % (save_dir, site_ID, tag),
#                 dpi=500, bbox_inches='tight')
# elif var_name == "rel_hum":
#     plt.savefig('%s%s_HTU21D_rel-hum_%s.png' % (save_dir, site_ID, tag),
#                 dpi=500, bbox_inches='tight')

#show the figure that was generated
plt.show()


