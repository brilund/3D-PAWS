#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Nov 12 17:12:49 2020

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

#This code reads and processes data from the UCAR/NCAR COMET 3D-PAWS system
#    suite of sensors. It should be used in combination with another parent
#    program. It returns a dataframe of the read and processed data.
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
#    Nov 12, 2020 - First Write
#
#
#Planned Features:
#    1. More sophistocated Error Catchers that print out useful statements to 
#       the user trhoughout the entire script
#
#
#How to Use:
#    1. Save this file/program in the same directory as the parent program you
#       will use this function in conjunction with
#    2. Import this function in the parent program (no need for file
#       extensions):
#
#       a) from reader import bmp
#       ... or...
#       b) import reader
#
#    3. Call the function in the parent program, ensuring that you pass the 
#       appropriate attributes/parameters:
#
#       a) call_bmp = bmp(directory, var_name, wildcard)
#       ... or...
#       b) call_bmp = reader.bmp(directory, var_name, wildcard)
#
#    4. Run the parent program with in terminal (e.g. "python 3D_main.py"),
#       or open the parent program in Spyder and run from there.
#
#
#Example header from files --> no file header(s)!!! (this could change...)
#
#Example data from files:
#    
#
#
#NOTES: The intended use of this file/function is in conjunction with another
#       file/program. There should be no need to edit anything in this
#       file/function. All parameters/attributes required to use this function
#       should be specified in the parent program.
# ----------------------------------------------------------------------------
#       At the moment, this program reads in all data even if a subset of time
#       is requested for plotting, which is a bit of an overkill



##############################################################################
#########################    IMPORTING MODULES    ############################
##############################################################################

import numpy as np
import glob
import pandas as pd
import sys



##############################################################################
########################    UNIVERSAL VARIABLES    ###########################
##############################################################################

#Initializing the lists that will store the data from each file for each
#    variable; only variables associated with the sensor that is being called
#    will be filled




##############################################################################
#########################    CREATING TIMESTAMPS    ##########################
##############################################################################

def timestamp_generator(year, month, day, hour, minute, second):
    
    #create an array containing the dates/times using the arrays above
    #initialize the empty list to store these timestamps
    time = []
    for i in range(len(month)): #the variable could be any of the time variables
        #    (i.e. 'month', 'day', 'year', 'hour', 'minute') since each should be
        #    the same length. This is to include every time from every file.
        if len(second) > 0:
            time.append('%s%s%s %s:%s:%s' % (year[i],month[i],day[i],hour[i],minute[i],second[i]))
        else: #no 'seconds'
            time.append('%s%s%s %s:%s' % (year[i],month[i],day[i],hour[i],minute[i]))
        #the format above is one of many that pandas will accept
    
    #convert the 'time' list to pandas DatetimeIndex
    #    NOTE: time is not reported to the second in these files, but the line the
    #    below will output the date-time elements in HH:MM:SS format so the
    #    assumption is that records are reported at the top of the minute, though
    #    not explicitly true. (Can I change the output format?)
    time = pd.to_datetime(time)
    
    return time



##############################################################################
#########################    ROUNDING TIMESTAMPS    ##########################
##############################################################################

#function for ensuring proper rounding of timestamps when timestamps are
#    recorded to the second; the round() function operates such that when a
#    timestamp falls half-way between two whole minutes, it chooses the even
#    minute (e.g. 15:30 rounds to 16:00, but 16:30 rounds to 16:00); we need
#    every occurrence of a half-minute to round up. The function(s) below does
#    just that
def half_up_minute(x):
    m = (x - x.dt.floor('1T')).dt.total_seconds() < 30   # Round True Down, False Up
    return x.where(m).dt.floor('1T').fillna(x.dt.ceil('1T'))

# For indices:
def half_up_minute_idx(idx):
    m = (idx - idx.floor('1T')).total_seconds() < 30   # Round True Down, False Up
    return pd.Index(np.select([m], [idx.floor('1T')], default=idx.ceil('1T')))



##############################################################################
############################    PRE-PROCESSING    ############################
##############################################################################

def pre_processing(df, second):

    #################### Collect out-of-order timestamps #####################
    
    ''' This section has no bearing on plotting and data cleansing. It is intended
        for catalogging and analysis of raw data purposes only.                 '''
    
    #find where out-of-order timestamps occur; this will only catch the first
    #    occurrence of a timestamp out of order, is essence, indicating the
    #    beginning of a section of data within the file such that time reset X
    #    number of minutes in the past
    #indices of times in the dataFrame where the difference between i+1 and i is
    #    negative (i.e. out of chronological order)
    idx = np.where(df.time.diff() < pd.Timedelta(minutes=0))
    
    #list of actual times in the dataFrame according to the indices above
    times_out_of_order = pd.to_datetime(np.array(df.time[pd.Index(idx[0])]))
    
    #the number of occurrences such that timestamps are out of chronological order
    num_out_of_order = len(times_out_of_order)
    
    #tell the user the absolute frequency of which timestamps are out of order
    print("Time reset %s time(s).\n" % num_out_of_order)
    
    
    ######################## Massaging the timestamps ########################
    
    #round each timestamp to the nearest minute if timestamps contain seconds
    if len(second) > 0:
        df.time = half_up_minute(df.time)
        
    
    ##########################################################################
    
    '''No longer sorting the data here because I have found that some
    occurrences of data spikes are associated with the second occurrence of a
    duplicate timestamp, and sometimes Pandas' sorting method places the second
    (third, fourth, etc.) occurrence of duplicate timestamp(s) ahead of the
    true first occurrence of said timestamp. The methods below keep the first
    occurrence of a duplicate timestamp so by sorting the data later, we keep
    the valid data value and remove the duplicate timestamp with the bad value'''
    #sort rows chronologically by 'time' (aka. the index variable)
    #df = df.set_index('time').sort_index().reset_index()
    
    
    ##################### Handling Duplicate Timestamps ######################
    
    #check for duplicated timestamps
    if pd.Index(df.time).has_duplicates == True:
        
        #keep a list of each duplicated timestamp; the method below will give ALL
        #    instances of a duplicated timestamp, so if there are 3 occurrences
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
    
    elif df.time.empty == True:
        #if something screwy happened above whether in the program or the data
        #    such that no data were read in, 'time' in the data frame (or any other
        #    variable for that matter) should be empty. If so, raise an error so
        #    the program exits
        raise TypeError("No data. Program exiting. Check the reader.py file and/or the data files themselves.")
    
    else:
        print("There are no duplicated timestamps.\n")
    
    #by now, data should be sorted chronologically and rid of any duplicated
    #    timestamps.
    
        
    ######################### Filling Gaps with NaNs #########################
        
    #Now we check to see if there are any missing report times. Timestamps should
    #    be monotonically increasing by 1 minute intervals. Since the interval is
    #    not exactly 1 minute (sometimes it is 61 seconds), the total number of
    #    data gaps is not perfectly representative of the exact number of data
    #    gaps. Due to the sublte inconsistencies in time reporting intervals and
    #    the time rounding method, the line below will consider instances such as...
    #    2:55:29, 2:56:29, 2:57:30 rounding to 2:55:00, 2:56:00, 2:58:00...
    #    the line below will include 2:57 as a data gap when in fact, this is not
    #    necessarily true
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
        #NOTE: to truly cover the bases, you could use...
        #      nan_sum = df[df.columns[1:]].isna().sum()
        #      ...then check that each column sum is the same. But unless you
        #      assign any values as NaNs for any reason other than "missing
        #      value", this is not necessary. Food for thought!
        
        #this is a pandas series containing the indices for the whole dataset
        #    such that the corresponding data value is NaN (i.e. missing)
        missing_reports_idx = df.index[df[df.columns[1]].isna()==True]
        
        #the actual timestamps for missing data records (NaNs)
        missing_report_times = pd.to_datetime(np.array(df.time[missing_reports_idx]))
        
        #this is the total sum of NaNs within the entire dataset
        missing_reports_sum = df[df.columns[1]].isna().sum()
        print("There are %s missing reports in the dataset read in.\n" % missing_reports_sum)
    
        #calculate the total downtime/uptime based on the number of missing reports
        
        #total amount of time within the entire dataset
        total = pd.Timedelta(len(df), unit='m')
        uptime = pd.Timedelta((len(df) - missing_reports_sum), unit='m')
        uptime_percent = round((1 - (float(missing_reports_sum) / float(len(df)))) * 100., 1)
        print("Total uptime is %s out of %s (%s%%).\n" % (uptime,total,uptime_percent))
        
    else:
        print("There are no missing reports!\n")

    ##########################################################################
    
    
    #sort rows chronologically by 'time' (aka. the index variable)
    df = df.set_index('time').sort_index().reset_index()
    
    
    ##########################################################################
    
    return (df, missing_report_times)



##############################################################################
#################################    BMP    ##################################
##############################################################################

def bmp(directory, wildcard):
    
    #tell the user that the function was called
    print("------------------------------------------------------------------\n")
    print("BMP reader function called...\n")
    
    #find all data files within the specified directory
    file_list = glob.glob(directory + wildcard)
    #sort the list of files
    file_list = sorted(file_list)
    
    #Read in the data file(s) from the file_list
    #Begin by initializing the lists that will store the data from each file for
    #    each variable
    month = [] #calendar day
    day = [] #calendar month
    year = [] #calendar year
    hour = [] #hour in UTC
    minute = [] #minutes after the hour [UTC]
    second = [] #seconds after the minute [UTC]
    temp_C = [] #temperature in degrees Celcius
    temp_F = [] #temperature in degrees Fahrenheit
    station_P = [] #station pressure in hectopascals
    SLP_hPa = [] #sea-level pressure in hectopascals
    SLP_inHg = [] #sea-level pressure in inches of mercury
    alt = [] #station altitude in meters
    
    #loop through the list of files, collecting values from each file and
    #    appending them to the appropriate list; each list will contain the data
    #    for a single variable from all files
    #set a counter for the number of lines with erroneous characters encountered
    counter = 0
    problem_files = [] #initialize a list to house files with erroneous characters
                       #    and partially overwritten lines
    
    #Read in the data file(s) from the file_list
    for file in file_list:
        with open(file, mode = "r") as f: #open the current file in read mode
            for line in f: #read each line of the file
                l = line.strip('\n').split() #remove carriage returns and whitespace
                if len(l) == 11: #this simple condition ought to weed out
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
                    station_P.append(l[7])
                    SLP_hPa.append(l[8])
                    SLP_inHg.append(l[9])
                    alt.append(l[10])
                else: #if the above condition of 11 elements is not met, then then 
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
    
    
    
    
    #------------------------------------------------------------------------#
    #------------------------    DATA PROCESSING    -------------------------#
    #------------------------------------------------------------------------#
    
    ########################## Checking Array Size ###########################
    
    #check that the number of elements in each array are the same
    if len(month) == len(day) == len(year) == len(hour) == len(minute) == \
        len(temp_C) == len(temp_F) == len(station_P) == len(SLP_hPa) == \
        len(SLP_inHg) == len(alt):
        #if all arrays have the same number of elements, then the read/append
        #    conditions above were met and everything is good.
        print("Number of elements in each variable array are equal. Continue...\n")
        
        if len(month) == 0: #can be any variable since now we know they are
        #    all equal in size/length
            raise ValueError("No data. Program exiting. Check the directory path and/or the data files themselves.\n The # of columns in the data files may not match what is specified by the condition set in the READ IN FILE(S) section")
            
    else:
        #if all arrays do not have the same number of elements...
        print("Number of elements in each variable array are not equal. Program exited.\n")
        sys.exit() #... kill the program
    
    
    ##########################################################################
    
    
    #convert variable lists to numpy arrays for simpler processing
    month = np.array(month) #this is a string
    day = np.array(day) #this is a string
    year = np.array(year) #this is a string
    hour = np.array(hour) #this is a string
    minute = np.array(minute) #this is a string
    temp_C = np.array(temp_C, dtype=float) #this is a float
    temp_F = np.array(temp_F, dtype=float) #this is a float
    station_P = np.array(station_P, dtype=float) #this is a float
    SLP_hPa = np.array(SLP_hPa, dtype=float) #this is a float
    SLP_inHg = np.array(SLP_inHg, dtype=float) #this is a float
    alt = np.array(alt, dtype=float) #this is a float
    
    
    ########################## Creating Timestamps ###########################
    
    #call the timestamp generator function
    time = timestamp_generator(year, month, day, hour, minute, second)
    
    
    ##########################################################################
    
    #original
    #put all the data/time arrays into a DataFrame
    df = pd.DataFrame({'time':time, 'temp_C':temp_C, 'temp_F':temp_F,
                       'station_P':station_P, 'SLP_hPa':SLP_hPa,
                       'SLP_inHg':SLP_inHg, 'alt':alt})
    
    
    ############################# Data Cleansing #############################
    
    #call the pre-processing function; this will collect out-of-order
    #    timestamps, handle duplicate timestamps, and fill data gaps with NaNs
    call_processor = pre_processing(df, second)
    df = call_processor[0]
    missing_reports = call_processor[1]
    
    
    ##########################################################################

    print("------------------------------------------------------------------")
    
    #will need to return 'count' and 'problem_files' if you want to add them to
    #    your output file; will also need to adjust variables in '3D_main.py'
    #    if returning 'count' and 'problem_files'
    return (df, missing_reports)



##############################################################################
################################    HTU21D    ################################
##############################################################################

def htu21d(directory, wildcard):
    
    #tell the user that the function was called
    print("------------------------------------------------------------------\n")
    print("HTU21D reader function called...\n")
    
    #find all data files within the specified directory
    file_list = glob.glob(directory + wildcard)
    #sort the list of files
    file_list = sorted(file_list)
    
    #Read in the data file(s) from the file_list
    #Begin by initializing the lists that will store the data from each file for
    #    each variable
    month = [] #calendar day
    day = [] #calendar month
    year = [] #calendar year
    hour = [] #hour in UTC
    minute = [] #minutes after the hour [UTC]
    second = [] #seconds after the minute [UTC]
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
    
    
    
    #------------------------------------------------------------------------#
    #------------------------    DATA PROCESSING    -------------------------#
    #------------------------------------------------------------------------#
    
    ########################## Checking Array Size ###########################
    
    #check that the number of elements in each array are the same
    if len(month) == len(day) == len(year) == len(hour) == len(minute) == len(temp_C) \
        == len(temp_F) == len(rel_hum):
        #if all arrays have the same number of elements, then the read/append
        #    conditions above were met and everything is good.
        print("Number of elements in each variable array are equal. Continue...\n")
        
        if len(month) == 0: #can be any variable since now we know they are
        #    all equal in size/length
            raise ValueError("No data. Program exiting. Check the directory path and/or the data files themselves.\n The # of columns in the data files may not match what is specified by the condition set in the READ IN FILE(S) section")
        
    else:
        #if all arrays do not have the same number of elements...
        print("Number of elements in each variable array are not equal. Program exited.\n")
        sys.exit() #... kill the program
        #consider telling the user where (i.e. what file) the above conditions was
        #    not met; this could pinpoint an otherwise unknown issue that needs
        #    addressing
    
    ##########################################################################
    
    
    #convert variable lists to numpy arrays for simpler processing
    month = np.array(month) #this is a string
    day = np.array(day) #this is a string
    year = np.array(year) #this is a string
    hour = np.array(hour) #this is a string
    minute = np.array(minute) #this is a string
    temp_C = np.array(temp_C, dtype=float) #this is a float
    temp_F = np.array(temp_F, dtype=float) #this is a float
    rel_hum = np.array(rel_hum, dtype=float) #this is a float
    
    
    ########################## Creating Timestamps ###########################
    
    #call the timestamp generator function
    time = timestamp_generator(year, month, day, hour, minute, second)

    
    ##########################################################################
    
    
    #put all the data/time arrays into a DataFrame
    df = pd.DataFrame({'time':time, 'temp_C':temp_C, 'temp_F':temp_F,
                       'rel_hum':rel_hum})
    
    
    ############################# Data Cleansing #############################
    
    #call the pre-processing function; this will collect out-of-order
    #    timestamps, handle duplicate timestamps, and fill data gaps with NaNs
    call_processor = pre_processing(df, second)
    df = call_processor[0]
    missing_reports = call_processor[1]
    
    
    ##########################################################################

    print("------------------------------------------------------------------")
    
    #will need to return 'count' and 'problem_files' if you want to add them to
    #    your output file; will also need to adjust variables in '3D_main.py'
    #    if returning 'count' and 'problem_files'
    return (df, missing_reports)



##############################################################################
###############################    MCP9808    ################################
##############################################################################

def mcp9808(directory, wildcard):
    
    #tell the user that the function was called
    print("------------------------------------------------------------------\n")
    print("MCP9808 reader function called...\n")
    
    #find all data files within the specified directory
    file_list = glob.glob(directory + wildcard)
    #sort the list of files
    file_list = sorted(file_list)
    
    #Read in the data file(s) from the file_list
    #Begin by initializing the lists that will store the data from each file for
    #    each variable
    month = [] #calendar day
    day = [] #calendar month
    year = [] #calendar year
    hour = [] #hour in UTC
    minute = [] #minutes after the hour [UTC]
    second = [] #seconds after the minute [UTC]
    temp_C = [] #temperature in degrees Celcius
    temp_F = [] #temperature in degrees Fahrenheit 
    
    #loop through the list of files, collecting values from each file and
    #    appending them to the appropriate list; each list will contain the data
    #    for a single variable from all files
    #set a counter for the number of lines with erroneous characters encountered
    counter = 0
    problem_files = [] #initialize a list to house filenames with erroneous
                       #    characters and partially overwritten lines
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
                    temp_C.append(l[5])
                    temp_F.append(l[6])
                else: #if the above condition of 7 elements is not met, then 
                    #    count the occurrence and skip to the next line/iteration
                    counter += 1
                    
                    #append the problematic filename to a list
                    problem_files.append(file)
                    continue
                
        #no need to close opened files; the 'with' method above does that for us
    
    #print the number of files read in
    print("%s files read" % len(file_list))
    
    #print the number of lines skipped due to erroneous characters or partially
    #    overwritten data lines
    print("%s lines skipped\n" % counter)
    
    
    
    #------------------------------------------------------------------------#
    #------------------------    DATA PROCESSING    -------------------------#
    #------------------------------------------------------------------------#
    
    ########################## Checking Array Size ###########################
    
    #check that the number of elements in each array are the same
    if len(month) == len(day) == len(year) == len(hour) == len(minute) == len(temp_C) \
        == len(temp_F):
        #if all arrays have the same number of elements, then the read/append
        #    conditions above were met and everything is good.
        print("Number of elements in each variable array are equal. Continue...\n")
        
        if len(month) == 0: #can be any variable since now we know they are
        #    all equal in size/length
            raise ValueError("No data. Program exiting. Check the directory path and/or the data files themselves.\n The # of columns in the data files may not match what is specified by the condition set in the READ IN FILE(S) section")
    else:
        #if all arrays do not have the same number of elements...
        print("Number of elements in each variable array are not equal. Program exited.\n")
        sys.exit() #... kill the program
        #consider telling the user where (i.e. what file) the above conditions was
        #    not met; this could pinpoint an otherwise unknown issue that needs
        #    addressing
    
    ##########################################################################
    
    
    #convert variable lists to numpy arrays for simpler processing
    month = np.array(month) #this is a string
    day = np.array(day) #this is a string
    year = np.array(year) #this is a string
    hour = np.array(hour) #this is a string
    minute = np.array(minute) #this is a string
    temp_C = np.array(temp_C, dtype=float) #this is a float
    temp_F = np.array(temp_F, dtype=float) #this is a float
    
    
    ########################## Creating Timestamps ###########################
    
    #call the timestamp generator function
    time = timestamp_generator(year, month, day, hour, minute, second)
    
    
    ##########################################################################
    
    
    #put all the data/time arrays into a DataFrame
    df = pd.DataFrame({'time':time, 'temp_C':temp_C, 'temp_F':temp_F})
    
    
    ############################# Data Cleansing #############################
    
    #call the pre-processing function; this will collect out-of-order
    #    timestamps, handle duplicate timestamps, and fill data gaps with NaNs
    call_processor = pre_processing(df, second)
    df = call_processor[0]
    missing_reports = call_processor[1]
    
    
    ##########################################################################

    print("------------------------------------------------------------------")
    
    #will need to return 'count' and 'problem_files' if you want to add them to
    #    your output file; will also need to adjust variables in '3D_main.py'
    #    if returning 'count' and 'problem_files'
    return (df, missing_reports)



##############################################################################
################################    SI1145    ################################
##############################################################################

def si1145(directory, wildcard):
    
    #tell the user that the function was called
    print("------------------------------------------------------------------\n")
    print("SI1145 reader function called...\n")
    
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
    month = [] #calendar day
    day = [] #calendar month
    year = [] #calendar year
    hour = [] #hour in UTC
    minute = [] #minutes after the hour [UTC]
    second = [] #seconds after the minute [UTC]
    vis = [] #visible light in Watts per meter squared
    ir = [] #infrared radiation "" "" "" "" ""
    uv = [] #ultraviolet radiation "" "" "" "" ""
    uvi = [] #ultraviolet index
    
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
                if len(l) == 9: #this simple condition ought to weed out
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
                    vis.append(l[5])
                    ir.append(l[6])
                    uv.append(l[7])
                    uvi.append(l[8])
                    
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
    
    
    
    #------------------------------------------------------------------------#
    #------------------------    DATA PROCESSING    -------------------------#
    #------------------------------------------------------------------------#
    
    ########################## Checking Array Size ###########################
    
    #check that the number of elements in each array are the same
    if len(month) == len(day) == len(year) == len(hour) == len(minute) == len(vis) \
        == len(ir) == len(uv) == len(uvi):
        #if all arrays have the same number of elements, then the read/append
        #    conditions above were met and everything is good.
        print("Number of elements in each variable array are equal. Continue...\n")
        
        if len(month) == 0: #can be any variable since now we know they are
        #    all equal in size/length
            raise ValueError("No data. Program exiting. Check the directory path and/or the data files themselves.\n The # of columns in the data files may not match what is specified by the condition set in the READ IN FILE(S) section")
            
    else:
        #if all arrays do not have the same number of elements...
        print("Number of elements in each variable array are not equal. Program exited.\n")
        sys.exit() #... kill the program
        #consider telling the user where (i.e. what file) the above conditions was
        #    not met; this could pinpoint an otherwise unknown issue that needs
        #    addressing
    
    ##########################################################################
    
    
    #convert variable lists to numpy arrays for simpler processing
    month = np.array(month) #this is a string
    day = np.array(day) #this is a string
    year = np.array(year) #this is a string
    hour = np.array(hour) #this is a string
    minute = np.array(minute) #this is a string
    vis = np.array(vis, dtype=float) #this is a float
    ir = np.array(ir, dtype=float) #this is a float
    uv = np.array(uv, dtype=float) #this is a float
    uvi = np.array(uvi, dtype=float) #this is a float
    
    
    ########################## Creating Timestamps ###########################
    
    #call the timestamp generator function
    time = timestamp_generator(year, month, day, hour, minute, second)
    
    
    ##########################################################################
    
    
    #put all the data/time arrays into a DataFrame
    df = pd.DataFrame({'time':time, 'vis':vis, 'ir':ir, 'uv':uv, 'uvi':uvi})
    
    
    ############################# Data Cleansing #############################
    
    #call the pre-processing function; this will collect out-of-order
    #    timestamps, handle duplicate timestamps, and fill data gaps with NaNs
    call_processor = pre_processing(df, second)
    df = call_processor[0]
    missing_reports = call_processor[1]
    
    
    ##########################################################################

    print("------------------------------------------------------------------")
    
    #will need to return 'count' and 'problem_files' if you want to add them to
    #    your output file; will also need to adjust variables in '3D_main.py'
    #    if returning 'count' and 'problem_files'
    return (df, missing_reports)



##############################################################################
#######################    RAIN / TIPPING BUCKET    ##########################
##############################################################################

def rain_gauge(directory, wildcard):
    
    #tell the user that the function was called
    print("------------------------------------------------------------------\n")
    print("RAIN GAUGE reader function called...\n")
    
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
    month = [] #calendar day
    day = [] #calendar month
    year = [] #calendar year
    hour = [] #hour in UTC
    minute = [] #minutes after the hour [UTC]
    second = [] #seconds after the minute [UTC]
    rain = [] #precipitation amount in mm
    
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
                    rain.append(l[6])
                    
                elif len(l) == 6: #adding this exception because some rain
                    #    gauge data do NOT record time to the second
                    month.append(l[0])
                    day.append(l[1])
                    year.append(l[2])
                    hour.append(l[3])
                    minute.append(l[4])
                    rain.append(l[5])
                    
                else: #if neither condition of 7 or 8 elements is not met, then 
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
    
    
    
    #------------------------------------------------------------------------#
    #------------------------    DATA PROCESSING    -------------------------#
    #------------------------------------------------------------------------#
    
    ########################## Checking Array Size ###########################

    #check that the number of elements in each array are the same
    if len(month) == len(day) == len(year) == len(hour) == len(minute) == len(rain):
        #if all arrays have the same number of elements, then the read/append
        #    conditions above were met and everything is good.
        print("Number of elements in each variable array are equal. Continue...\n")
        
        if len(month) == 0: #can be any variable since now we know they are
        #    all equal in size/length
            raise ValueError("No data. Program exiting. Check the directory path and/or the data files themselves.\n The # of columns in the data files may not match what is specified by the condition set in the READ IN FILE(S) section")
            
    else:
        #if all arrays do not have the same number of elements...
        print("Number of elements in each variable array are not equal. Program exited.\n")
        sys.exit() #... kill the program
        #consider telling the user where (i.e. what file) the above conditions was
        #    not met; this could pinpoint an otherwise unknown issue that needs
        #    addressing
    
    ##########################################################################
    
    
    #convert variable lists to numpy arrays for simpler processing
    month = np.array(month) #this is a string
    day = np.array(day) #this is a string
    year = np.array(year) #this is a string
    hour = np.array(hour) #this is a string
    minute = np.array(minute) #this is a string
    if len(second) > 0:
        second = np.array(second) #this is a string
    else:
        pass
    rain = np.array(rain, dtype=float) #this is a float


    ########################## Creating Timestamps ###########################
    
    #call the timestamp generator function
    time = timestamp_generator(year, month, day, hour, minute, second)
    
    
    ###########################################################################
    
    
    #put all the data/time arrays into a DataFrame and set the index as the 'time'
    #    column
    df = pd.DataFrame({'time':time, 'rain':rain})
    
    
    ############################# Data Cleansing #############################
    
    #call the pre-processing function; this will collect out-of-order
    #    timestamps, handle duplicate timestamps, and fill data gaps with NaNs
    call_processor = pre_processing(df, second)
    df = call_processor[0]
    missing_reports = call_processor[1]
    
    
    ########################### Add Special Column ###########################

    #we have moved the data conversion portion to the plotter function so that
    #    we may remove the 'units' positional argument from the function
    
    #add a column to the dataframe that essentially masks all values except zeroes;
    #    this ought to more clearly show when data was being recorded but there
    #    was no rain vs. no data being recorded (i.e. downtime)
    df["no_rain"] = df.rain
    df.no_rain[df.no_rain > 0.] = np.nan
    
    
    ##########################################################################

    print("------------------------------------------------------------------")
    
    #will need to return 'count' and 'problem_files' if you want to add them to
    #    your output file; will also need to adjust variables in '3D_main.py'
    #    if returning 'count' and 'problem_files'
    return (df, missing_reports)



##############################################################################
##############################    WIND VANE    ###############################
##############################################################################

def wind_vane(directory, wildcard):
    #tell the user the function was called
    print("------------------------------------------------------------------\n")
    print("WIND VANE reader function called...\n")
    
    #find all data files within the specified directory
    file_list = glob.glob(directory + wildcard)
    #sort the list of files
    file_list = sorted(file_list)
    
    # you'll need to think about how to account for the different types of
    #    data files here. This will be the place to begin, perhaps with some
    #    'if' statements
    
    #Read in the data file(s) from the file_list
    #Begin by initializing the lists that will store the data from each file
    #    for each variable
    month = [] #calendar day
    day = [] #calendar month
    year = [] #calendar year
    hour = [] #hour of day [UTC]
    minute = [] #minutes after the hour [UTC]
    second = [] #seconds after the minute [UTC]
    wind_dir = [] #wind speed [m/s]
    
    #loop through the list of files, collecting values from each file and
    #    appending them to the appropriate list; each list will contain the
    #    data for a single variable from all files
    #set a counter for the number of lines with erroneous characters
    #    encountered
    counter = 0
    problem_files = [] #initialize a list to house files with erroneous
                       #    characters and partially overwritten lines
    num_lines = 0 #counts the total number of lines read in
    
    for file in file_list:
        with open(file, mode = "r") as f: #open the current file in read mode
            for line in f: #read each line of the file
                l = line.strip('\n').split() #remove carriage returns and
                                             #    whitespace
                num_lines += 1
                if len(l) == 9: #this simple condition ought to weed out
                    #    instances of erroneous characters at the end of a
                    #    file or lines that were partially overwritten; the
                    #    length, or # of elements in this variable 'l' should
                    #    be equivalent to the # of columns in your data file;
                    #    if not, the data line in question is likely a
                    #    partially overwritten line or the last line in a file
                    #    that did not record to 23:59 UTC and contains
                    #    erroneous characters (\@\@\@\@\@\@\)
                    month.append(l[0])
                    day.append(l[1])
                    year.append(l[2])
                    hour.append(l[3])
                    minute.append(l[4])
                    second.append(l[5])
                    wind_dir.append(l[7])
                    
                elif len(l) == 8: #for timestamps NOT recorded to the second
                    month.append(l[0])
                    day.append(l[1])
                    year.append(l[2])
                    hour.append(l[3])
                    minute.append(l[4])
                    #second.append(l[5])
                    wind_dir.append(l[6]) #wind_dir.append(l[7])
                    
                else: #if the above condition of 8 elements is not met, then 
                    #    count the occurrence and skip to the next 
                    #    ine/iteration
                    counter += 1
                    
                    #append the problematic filename to a list
                    problem_files.append(file)
                    continue
        f.close() #always close opened files
    
    #print the number of files read in
    print("%s files read" % len(file_list))
    
    #print the number of lines skipped due to erroneous characters or
    #    partially overwritten data lines
    print("%s lines skipped\n" % counter)
    
    
    
    #------------------------------------------------------------------------#
    #------------------------    DATA PROCESSING    -------------------------#
    #------------------------------------------------------------------------#
    
    ########################## Checking Array Size ###########################
    
    #check that the number of elements in each array are the same
    if len(month) == len(day) == len(year) == len(hour) == len(minute) == len(wind_dir): #\
        #== len(second):
        #if all arrays have the same number of elements, then the read/append
        #    conditions above were met and everything is good.
        print("Number of elements in each variable array are equal. Continue...\n")
        
        if len(month) == 0: #can be any variable since now we know they are
        #    all equal in size/length
            raise ValueError("No data. Program exiting. Check the directory path and/or the data files themselves.\n The # of columns in the data files may not match what is specified by the condition set in the READ IN FILE(S) section")
        
    else:
        #if all arrays do not have the same number of elements...
        print("Number of elements in each variable array are not equal. Program exited.\n")
        sys.exit() #... kill the program
        #consider telling the user where (i.e. what file) the above conditions
        #    was not met; this could pinpoint an otherwise unknown issue that
        #    needs addressing
        
    
    ##########################################################################
        
    
    #convert variable lists to numpy arrays for simpler processing
    month = np.array(month) #this is a string
    day = np.array(day) #this is a string
    year = np.array(year) #this is a string
    hour = np.array(hour) #this is a string
    minute = np.array(minute) #this is a string
    second = np.array(second) #this is a string
    wind_dir = np.array(wind_dir, dtype=float) #this is a float

    
    ########################## Creating Timestamps ###########################
    
    #call the timestamp generator function
    time = timestamp_generator(year, month, day, hour, minute, second)
    
    ##########################################################################
    
    
    #put all the data/time arrays into a DataFrame and set the index as the
    #    'time' column
    df = pd.DataFrame({'time':time, 'wind_dir':wind_dir})
    
    
    ############################# Data Cleansing #############################
    
    #call the pre-processing function; this will collect out-of-order
    #    timestamps, handle duplicate timestamps, and fill data gaps with NaNs
    call_processor = pre_processing(df, second)
    df = call_processor[0]
    missing_reports = call_processor[1]
    
    
    ##########################################################################

    print("------------------------------------------------------------------")
    
    #will need to return 'count' and 'problem_files' if you want to add them to
    #    your output file; will also need to adjust variables in '3D_main.py'
    #    if returning 'count' and 'problem_files'
    return (df, missing_reports)



##############################################################################
##############################    ANEMOMETER    ##############################
##############################################################################

def anemometer(directory, wildcard):
    #tell the user that the function was called
    print("------------------------------------------------------------------\n")
    print("ANEMOMETER reader function called...\n")
    
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
    month = [] #calendar day
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
    num_lines = 0 #counts the total number of lines read in
    
    for file in file_list:
        with open(file, mode = "r") as f: #open the current file in read mode
            for line in f: #read each line of the file
                l = line.strip('\n').split() #remove carriage returns and whitespace
                num_lines += 1
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
                elif len(l) == 6: #to account for timestamps not recorded to
                    #    the second
                    month.append(l[0])
                    day.append(l[1])
                    year.append(l[2])
                    hour.append(l[3])
                    minute.append(l[4])
                    wind_speed.append(l[5])
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
    
    
    
    #------------------------------------------------------------------------#
    #------------------------    DATA PROCESSING    -------------------------#
    #------------------------------------------------------------------------#
    
    ########################## Checking Array Size ###########################
    
    #check that the number of elements in each array are the same
    if len(month) == len(day) == len(year) == len(hour) == len(minute) == len(wind_speed):
        #if all arrays have the same number of elements, then the read/append
        #    conditions above were met and everything is good.
        print("Number of elements in each variable array are equal. Continue...\n")
        
        if len(month) == 0: #can be any variable since now we know they are
        #    all equal in size/length
            raise ValueError("No data. Program exiting. Check the directory path and/or the data files themselves.\n The # of columns in the data files may not match what is specified by the condition set in the READ IN FILE(S) section")
        
    else:
        #if all arrays do not have the same number of elements...
        print("Number of elements in each variable array are not equal. Program exited.\n")
        sys.exit() #... kill the program
        #consider telling the user where (i.e. what file) the above conditions was
        #    not met; this could pinpoint an otherwise unknown issue that needs
        #    addressing
    
    ##########################################################################
        
    
    #convert variable lists to numpy arrays for simpler processing
    month = np.array(month) #this is a string
    day = np.array(day) #this is a string
    year = np.array(year) #this is a string
    hour = np.array(hour) #this is a string
    minute = np.array(minute) #this is a string
    if len(second) > 0:
        second = np.array(second) #this is a string
    wind_speed = np.array(wind_speed, dtype=float) #this is a float
    
    
    ############################ Converting Data #############################
    
    #converting wind speed to user-defined units is now performed in the
    #    plotter program so that we may remove the 'units' input from this
    #    function
    
    
    ########################## Creating Timestamps ###########################
    
    #call the timestamp generator function
    time = timestamp_generator(year, month, day, hour, minute, second)
    
    ##########################################################################
    
    
    #put all the data/time arrays into a DataFrame and set the index as the 'time'
    #    column
    df = pd.DataFrame({'time':time, 'wind_speed':wind_speed})
    
    
    ############################# Data Cleansing #############################
    
    #call the pre-processing function; this will collect out-of-order
    #    timestamps, handle duplicate timestamps, and fill data gaps with NaNs
    call_processor = pre_processing(df, second)
    df = call_processor[0]
    missing_reports = call_processor[1]
    
    
    ##########################################################################

    print("------------------------------------------------------------------")
    
    #will need to return 'count' and 'problem_files' if you want to add them to
    #    your output file; will also need to adjust variables in '3D_main.py'
    #    if returning 'count' and 'problem_files'
    return (df, missing_reports)


#only execute the functions if they are explicitly called from the parent
#    3D_main.py program
if __name__ == "__main__":
    bmp()
    htu21d()
    mcp9808()
    si1145()
    rain_gauge()
    wind_vane()
    anemometer()
    #stream_gauge()


