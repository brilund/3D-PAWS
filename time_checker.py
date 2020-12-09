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

#This code checks the validity of user-input time variables from a parent
#    program.
#
#Written by Brianna Lund
#
#QUESTIONS?
#Email me at blund@ucar.edu
#
#LICENSE:
#This code may be used and distributed freely, provided proper attribution is
#    given to UCAR and the author.
#
#
#REQUIREMENTS:
#    Python 3
#    Numpy
#    Pandas
#    Sys
#
#
#HISTORY:
#    Nov 03, 2020 - First Write; modified from original BMP_weekly_plotter.py
#
#
#PLANNED FEATURES:
#
#
#HOW TO USE:
#    1. Save this file/program in the same directory as the parent program you
#       will use this function in conjunction with
#    2. Import this function in the parent program (no need for file
#       extensions):
#
#       a) from time_checker import time_checker
#       ... or...
#       b) import time_checker as tc
#
#    3. Call the function in the parent program, ensuring that you pass the 
#       appropriate attributes/parameters:
#
#       a) call_time = time_checker(mintime, maxtime, df)
#       ... or...
#       b) call_time = tc.time_checker(mintime, maxtime, df)
#
#    4. Run the parent program within terminal (e.g. "python BMP_plotter.py"),
#       or open the parent program in Spyder and run from there.
#
#
#Example header from files --> no file header(s)!!! (this could change...)
#
#Example data from files:
#    
#
#
#NOTES: At the moment, this program reads in all data (the whole dataframe)
#       even if a subset of time is requested for plotting, analysis, etc.,
#       which is a bit of an overkill



##############################################################################
#########################    IMPORTING MODULES    ############################
##############################################################################

import numpy as np
import pandas as pd
import sys



##############################################################################
##############################    FUNCTION    ################################
##############################################################################

#'mintime', 'maxtime', and 'df' (dataframe) are called from the main function;
#    'df' is needed because we use the dataframe and some dataframe methods to
#    check timestamps
def time_checker(mintime, maxtime, plot_opt, df):
    
    #tell the user that the function was called
    print("------------------------------------------------------------------\n")
    print("'time_checker' function called...\n")

    ##############################################################################
    ###########################    DATA PROCESSING    ############################
    ##############################################################################
    
    #create a 'time' variable from the 'time' column in the DataFrame as a
    #   DatetimeIndex array; this will be used for other calculations/test below
    time = pd.to_datetime(np.array(df.time))
    
    
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
        
    elif len(mintime) == 16 and len(maxtime) == 16: #they should include 16 characters
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
        raise ValueError("Incorrect format for 'mintime'; should be YYYY-MM-DD HH:mm")
        
    #then check to see if 'mintime' and 'maxtime' are within the dataset that was
    #    read in
    #Note: the method min() and max() are functions of both DataFrames and
    #      datetimeindex, so if we wanted, we could also do this: df.time.min()
    if pd.to_datetime(mintime) < df.time.min() or \
        pd.to_datetime(mintime) > df.time.max() or \
            pd.to_datetime(maxtime) > df.time.max() or \
                pd.to_datetime(maxtime) < df.time.min():
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
    
    #if using the daily, weekly, or monthly plotter, check that the interval
    #    of time determined by the user-defined range limits is at least 1 day,
    #    7 days, or 28 days, respectively
    if plot_opt == "weekly" and ((df.time[maxtime] - df.time[mintime]) < pd.Timedelta(weeks=1)):
        raise ValueError("The time delta given by 'mintime' and 'maxtime' is less than 7 days.\nPlease give a 'mintime' and 'maxtime' such that the time delta is at least 7 days when using the weekly plotter, or use the default plotter instead.")
    if plot_opt == "daily" and ((df.time[maxtime] - df.time[mintime]) < pd.Timedelta(days=1)):
        raise ValueError("The time delta given by 'mintime' and 'maxtime' is less than 1 day.\nPlease give a 'mintime' and 'maxtime' such that the time delta is at least 1 day when using the daily plotter, or use the default plotter instead.")
    if plot_opt == "monthly" and ((df.time[maxtime] - df.time[mintime]) < pd.Timedelta(days=28)):
        raise ValueError("The time delta given by 'mintime' and 'maxtime' is less than 28 days.\nPlease give a 'mintime' and 'maxtime' such that the time delta is at least 28 days when using the monthly plotter, or use the default plotter instead.")
    else:
        #this line will find the index of the very first day/time for each month in
        #    the whole dataframe
        day1_of_month_idx = df.index[df.set_index('time').index.day == 1][::1440]
        
        #this line will find the index(indices) of the very first day/time for each
        #    month within the time frame set by the user (within 'mintime' and
        #    'maxtime')
        day1_of_month_idx = day1_of_month_idx[(day1_of_month_idx>mintime) & (day1_of_month_idx<maxtime)]
        
        #if the user time frame is GREATER THAN or EQUAL TO 28 days but does
        #    not contain a first-of-the-month date/timestamp
        #    (e.g. mintime = "2017-10-01 00:01" and maxtime = "2017-10-28 00:01"),
        #    then default to the regular plotter
        if day1_of_month_idx.empty == True:
            print("Timeframe set by 'mintime' and 'maxtime' does not contain a first-of-the-month date/time.\nSetting 'plot_opt' to default.")
            plot_opt = "plotter"
    
    ######################### Uptime within Time Frame ########################### 
    
    #calculate the total uptime based on the number of missing reports,
    #    but within the time frame ('mintime' and 'maxtime') set by the user; must
    #    add 1 to 'maxtime' because indexing ranges in python exclude the very
    #    last index from the range given (e.g. indexing from [0:10] will go from
    #    the zeroeth index to the 9th index, excluding the 10th index)
    #NOTE: if 'mintime' and 'maxtime' are set such that the entire dataset is
    #      being plotted, the uptime calculated below should be the same as that
    #      calculated above in the "Filling gaps with NaNs" subsection
    if mintime != 0 or maxtime != df.index[-1]:
    
        #this is a pandas series containing the indices WITHIN THE TIME FRAME
        #    such that the corresponding data value is NaN (i.e. missing)
        missing_reports_idx = df.index[mintime:maxtime+1][df[df.columns[1]][mintime:maxtime+1].isna()==True]
        
        #the actual timestamps for missing data records (NaNs)
        missing_report_times = pd.to_datetime(np.array(df.time[missing_reports_idx]))
        
        #this is the total sum WITHIN THE TIME FRAME such that the data are
        #    NaNs
        missing_reports_sum = df[df.columns[1]][mintime:maxtime+1].isna().sum()
        
        #total amount of time WITHIN THE TIME FRAME
        total = pd.Timedelta(len(df.index[mintime:maxtime+1]), unit='m')
        
        #total amount of uptime WITHIN THE TIME FRAME
        uptime = pd.Timedelta((len(df.index[mintime:maxtime+1]) - missing_reports_sum), unit='m')
        
        #total uptime percentage WITHIN THE TIME FRAME
        uptime_percent = round((1 - (float(missing_reports_sum) / float(len(df[mintime:maxtime+1])))) * 100., 1)
        print("Uptime during the time frame is %s out of %s (%s%%).\n" % (uptime,total,uptime_percent))
        
    
    ##########################################################################

        print("------------------------------------------------------------------")
        
        #will have to return additional variables once the OUTPUT option is
        #    implemented because some relevant output information is 
        #    calculated here; must also return 'plot_opt' in the event that
        #    the time frameset by the user is greater than the required 28 
        #    days, but does not contain a first-of-the-month date/time
        #    (e.g. mintime = "2017-10-01 00:01" and maxtime = "2017-10-28 00:01")
        return mintime, maxtime, plot_opt, missing_report_times
    
    else:
        #don't return missing_report_times if 'mintime' and 'maxtime' are set
        #    as empty stings, indicating use of the WHOLE dataset
        return mintime, maxtime, plot_opt

if __name__ == "__main__":
    time_checker()

    


