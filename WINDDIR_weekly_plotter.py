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
#    plots on a weekly basis.
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
#    August 25, 2020 - First Write
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
#    3. Separate major sections into callable functions: reader, processor,
#       output, plotter, etc.
#    4. Modify this code to include the ability to create weekly plots from
#       ANY sensor
#    5. Skip weeks for which all data are NaNs (this should be faily easy)
#    6. Include the averaging option(?)
#
#
#How to Use:
#    1. Change all variables in "USER OPTIONS" section to desired input
#           directory
#           site_ID
#           save_dir
#           wildcard
#           mintime
#           maxtime
#    2. Run with "python weekly_plotter.py" in terminal, or open in
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



##############################################################################
############################    USER OPTIONS    ##############################
##############################################################################

#set the 'directory' variable to the absolute path where your data are stored;
#    don't forget the trailing forward slash!
directory = "/Users/blund/Documents/3D-PAWS/Data/CSA_3DPAWS01/wx_stn/WINDDIR/"

#change this to the name of the site from which data are being plotted; this
#    will be used in the plot title as well as the name of the figure
site_ID = "CSA_3DPAWS01"

#specify the FULL file path to the directory in which to save your figures;
#    don't forget to include the trailing forward slash!
save_dir = "/Users/blund/Documents/Python_Scripts/Figures/CSA_3DPAWS01/WINDDIR/"

#uncomment this option to read in EVERY file withing the directory you
#    specified above in 'directory'
#wildcard = "*"
#uncomment this option to specify your own wildcard to select a subset of data
#    within the directory you specified above in 'directory'
wildcard = "*"

#set the time frame over which to plot (UTC); you must use the following
#    format: "YYYY-MM-DD HH:mm"; to plot the whole dataset, set 'mintime'
#    and 'maxtime' to empty strings (e.g. mintime = ""), likewise, to plot
#    from the beginning of the time period, set mintime = "" and set 'maxtime'
#    to your end date/time. Vice versa for plotting to the end of the whole
#    time period
mintime = ""
maxtime = ""



##############################################################################
###########################    READ IN FILE(S)    ############################
##############################################################################

#read in the dataframe for wind direction from the wind_dir_function; this
#    is pre-processed data being read in so any sorting, removal of duplicate
#    timestamps, data conversions, etc. is done before the data frame is read
#    into this program. Those parameters are specified in THIS program and
#    given/passed to the other program's function

df = wind_dir_processor(directory, wildcard)



##############################################################################
###########################    DATA PROCESSING    ############################
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


#lastly, check that the interval of time determined by the user-defined range
#    limits is at least 7 days
if (pd.to_datetime(maxtime) - pd.to_datetime(mintime)) < pd.Timedelta(weeks=1):
    ValueError("The time delta given by 'mintime' and 'maxtime' is less than 7 days.\nPlease give a 'mintime' and 'maxtime' such that the time delta is at least 7 days.")


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



##############################################################################
################################   OUTPUT   ##################################
##############################################################################

#placeholder section for generating a file that will store all kinds of stats,
#    metrics and other metadata for analysis

#information to add to this output file...
#a list of duplicate timestamps (aka 'duplicates')
#file names such that lines were skipped (aka 'problem files')



##############################################################################
###############################   PLOTTING   #################################
##############################################################################

''' Include an option for one variable to be plotted or to plot all variables
    in their own separate figures '''

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

# ############################ 
# week = pd.Timedelta(weeks=1)
# index = df.index[df.time == df.time[0] + week][0]
##############################

#find the starting index of the range over which to plot; this is simply
#    'mintime' but we will give it a different name for clarity
start = mintime

#find the ending index of the range over which to plot; this will be the
#    index of df.time that equals the 'maxtime' specified by the user; this,
#    too, is simply equal to 'maxtime', but we must add 1 to the index because
#    the 'range' function does not include the end value
end = maxtime + 1
####
# FOR ARCHIVAL PURPOSES; this was used when 'maxtime' was set to '-1' as the
#    last index; now we explicitly find the last index
#find the ending index of the range over which to plot; this will be the
#    index of df.time that equals the 'maxtime' specified by the user; there
#    are but two instances that keep us from simply setting this equal to
#    'maxtime' and that is when the user specifies the entire dataset (i.e.
#    'mintime' and 'maxtime' = "") or does not specify a 'maxtime' (i.e. plot
#    to the end of the dataset --> 'maxtime' = ""); we must add 1 to the index
#    because the 'range' function does not include the end value
#end = df.index[df.time == time[maxtime]][0]+1
####

#since data are recorded every minute, and there are 10080 minutes in 1 week,
#    we set the range interval to 10080 (equivalent to 'every 10080th index')
interval = 10080

#######################
for w in range(start,end,interval):
    
    #'mintime' and 'maxtime will now change through each iteration of the loop
    #    to serve as the indices defining the 1-week intervals throughout the
    #    dataset over which to plot; the difference between them, however, will
    #    always represent 1 week / 7 days
    mintime = w
    maxtime = w + interval
    
    #set 'maxtime' to the end of the range if 'maxtime' is out of the range
    #    specified; this will only occur if the range is not perfectly
    #    divisible by 1 week / 7 days; in this instance, the very last figure
    #    generated would NOT represent a 7 day period
    if maxtime > end:
        maxtime = end - 1 #now we subtract 1 because set_xlim() includes the
                          #    upper limit given when setting the range; if we
                          #    did not subtract 1, 'maxtime' would be out of
                          #    range for set_xlim()
        
    ### pandas plotting ###
    
    #plot
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
    
    tag = str(time[mintime])[:10].split("-")+["-"]+str(time[maxtime])[:10].split("-")
    tag = ''.join(x for x in tag)
    
    #save the figure
    plt.savefig('%s%s_wind-dir_%s.png' % (save_dir, site_ID, tag), \
                dpi=500, bbox_inches='tight')
    
    #show the figure that was generated
    plt.show()
    



