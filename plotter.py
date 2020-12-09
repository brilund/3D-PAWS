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

#This code plots 3D-PAWS data based on user input from a parent program.
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
#    Nov 04, 2020 - First Write; modified from original BMP_weekly_plotter.py
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
#       a) from plotter import plotter
#       ... or...
#       b) import plotter as pltr
#
#    3. Call the function in the parent program, ensuring that you pass the 
#       appropriate attributes/parameters:
#
#       a) call_plotter = plotter(mintime, maxtime, df)
#       ... or...
#       b) call_plotter = pltr.plotter(mintime, maxtime, df)
#
#    4. Run the parent program within terminal (e.g. "python main.py"),
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

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import sys
import datetime



##############################################################################
#####################   UNIVERSAL PLOTTING PARAMETERS    #####################
##############################################################################

def _universal_params(ax,df,mintime,maxtime,sensor,site_ID):
    #add dashed grid lines
    plt.grid(which='major', linestyle='--', color='dimgray')
    plt.grid(which='minor', linestyle=':',color='gray')
    
    #set x-axis limits/range
    ax.set_xlim(df.time[mintime], df.time[maxtime])
    
    #set the plot's title
    if sensor.lower() == "wind_vane":
        plt.title("%s : %s" % (site_ID, ''.join(sensor.replace('_', ' ')).upper()), fontsize=12)
        
    elif  sensor.lower == "rain":
        plt.title("%s : TIPPING BUCKET" % site_ID, fontsize=12)
        
    else: #all other sensors follow the standard plot title below
        plt.title("%s : %s" % (site_ID, sensor.upper()), fontsize=12)
    
    #set the x-axis label
    plt.xlabel("Date / Time (UTC)")
    
    #set the plot legend
    plt.legend(loc='upper left', bbox_to_anchor=(1, 1), framealpha=0.95,
                fancybox=True, shadow=True, fontsize=10)
    
    return



##############################################################################
##############################   SAVE FIGURE    ##############################
##############################################################################

def _save_figure(sensor, save_dir, site_ID, var_name, units, averaged,
                avg_window, mintime, maxtime, plot_opt, tag, df):
    
    if plot_opt == "weekly":
        #'tag' here represents the dates for which the figure's time frame is valid;
        #    it is used in the name of the figure
        tag = str(df.time[mintime])[:10].split("-")+["-"]+str(df.time[maxtime])[:10].split("-")
        tag = ''.join(x for x in tag)
        
    elif plot_opt =="daily":
        #'tag' here represents the date for which the figure's time frame is valid;
        #    it is used in the name of the figure
        tag = str(df.time[mintime])[:10].split("-")
        tag = ''.join(x for x in tag)
    
    elif plot_opt == "monthly":
        #'tag' here represents the dates for which the figure's time frame is valid;
        #    it is used in the name of the figure
        tag = str(df.time[mintime])[:7]
    
    #replace underscores in 'var_name' with hyphens/dashes; merely a personal
    #    preference for figure naming    
    var_name = ''.join(var_name.replace('_', '-'))
    
    #save the figure
    if sensor.lower() == "anemometer":
        var_name = "wind-spd"
        if averaged == False:
            plt.savefig('%s%s_%s-%s_%s.png' % (save_dir, site_ID, var_name, units, tag), \
                        dpi=500, bbox_inches='tight')
        elif averaged == True:
            plt.savefig('%s%s_%s-%s_%s-min_%s.png' % (save_dir, site_ID, var_name, units, avg_window, tag), \
                        dpi=500, bbox_inches='tight')
        elif averaged == "static" or averaged == "resampled":
            plt.savefig('%s%s_%s-%s_%s-min-%s_%s.png' % (save_dir, site_ID, var_name, units, avg_window, averaged, tag), \
                        dpi=500, bbox_inches='tight')
        
    elif sensor.lower() == "wind_vane":
        var_name = "wind-dir"
        plt.savefig('%s%s_%s_%s.png' % (save_dir, site_ID, var_name, tag), \
                    dpi=500, bbox_inches='tight')
        
    elif sensor.lower() == "rain":
        plt.savefig('%s%s_%s-%s_%s.png' % (save_dir, site_ID, sensor.upper(), units, tag), \
                    dpi=500, bbox_inches='tight')
    else:
        plt.savefig('%s%s_%s_%s_%s.png' % (save_dir, site_ID, sensor, var_name, tag),
                    dpi=500, bbox_inches='tight')
    
    #show the figure that was generated
    plt.show()



##############################################################################
##############################    PLOTTERs    #################################
##############################################################################

#to plot figures for the user-defined time frame, call this function; this is
#    the default plotting function; the other plotting options depend on this
#    function; think of this one as the PARENT plotter
def plotter(sensor, save_dir, site_ID, var_name, units, averaged, avg_window,
            mintime, maxtime, plot_opt, tag, df):
    
    #no print statement here telling the user that this function was called
    #    because this one gets called MANY times from the other plotting
    #    functions (daily, weekly and monthly)
        
    #plot based on 'sensor'
    if sensor.lower() == "anemometer":
        
        #import matplotlib for anemometer only because we need to use that
        #    rcParams thing
        import matplotlib as mpl
        
        #not sure what this does, but supposedly it is necessary for larger datasets;
        #    this will not plot without it
        mpl.rcParams['agg.path.chunksize'] = 10000
        
        #plot based on the user-defined averaging/smoothing parameters
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
            #plotting all raw data; should eliminate this statement because
            #    averaging parameters are checked in input_checker.py and if
            #    'averaged' does not meet any of the above conditions, the
            #    program will exit at the input-checking stage, never getting
            #    to this stage so the line below is a wasted of space; will
            #    vet this thoroughly
            ax = df.plot(x='time', y='wind_speed', color='b', label='wind_%s' % units,
                         figsize=(30,5))
            
    ##########    
        #some parameters specific to 'units'
        if units == "mps": #plot wind speed in meters per second
            
            #set y-axis limits/range
            ax.set_ylim(0., 10.)
            
            #set the y-axis label
            plt.ylabel("Wind Speed (m s$^-1$)")
            
        elif units == "kmph": #plot wind speed in kilometers per hour
            
            #set y-axis limits/range
            ax.set_ylim(0., 90.)
            
            #set the y-axis label
            plt.ylabel("Wind Speed (km h$^-1$)")
            
        elif units == "mph":
            
            #set y-axis limits/range
            ax.set_ylim(0., 50.)
            
            #set the y-axis label
            plt.ylabel("Wind Speed (m h$^-1$)")
        
        elif units == "kts": #plot wind speed in knots
            
            #set y-axis limits/range
            ax.set_ylim(0., 50.)
            
            #set the y-axis label
            plt.ylabel("Wind Speed (kts)")
        
        else:
            #in theory, we have already accounted for this potential error with
            #    the input_checker, so this is redundant; may remove at some
            #    point
            print("'units' not recognized. Program exiting...")
            sys.exit()
    
##########   
    elif sensor.lower() == "wind_vane":
        ax = df.plot(x='time', y='wind_dir', color='b', label='wind_dir',
                     figsize=(30,5))
    
        #set y-axis limits/range
        ax.set_ylim(0., 360.)
        
        #set the y-axis label
        plt.ylabel("Wind Direction (degrees)")
        
##########    
    elif sensor.lower() == "rain":
        ax = df.plot(x='time', y=['rain', 'no_rain'], color=['b','r'],
                     label=['rain','no-rain'], figsize=(30,5))
        
        #set y-axis range and title based on "millimeters"
        if units == "mm":
            #set y-axis limits/range
            ax.set_ylim(-0.1, 5.)
            
            #set the y-axis label
            plt.ylabel("Precipitation (mm)")
        
        #set y-axis range and title based on "inches"
        elif units == "inches":
            #set y-axis limits/range
            ax.set_ylim(-0.01, 0.2)
            
            #set the y-axis label
            plt.ylabel("Precipitation (in.)")
            
##########    
    else: #for all other sensors, we plot here
        ax = df.plot(x='time', y=var_name, color='b', label=var_name, figsize=(30,5))
    
        #plot parameters within these 'if' statements are those specific to each
        #    variable
        if var_name == "temp_C": #plot temperature in Celsius
            
            #set y-axis limits/range
            ax.set_ylim(-20., 45.)
            
            #set the y-axis label
            plt.ylabel("Temperature ($^o$C)")
            
        elif var_name == "temp_F": #plot temperature in Fahrenheit
            
            #set y-axis limits/range
            ax.set_ylim(-10., 110.)
            
            #set the y-axis label
            plt.ylabel("Temperature ($^o$F)")
        
        elif var_name == "rel_hum": #plot relative humidity (%)
            
            #set y-axis limits/range
            ax.set_ylim(0., 100.)
            
            #set the y-axis label
            plt.ylabel("Relative Humidity (%)")
            
        elif var_name == "station_P": #plot station pressure (hPa))
            
            #set y-axis limits/range
            ax.set_ylim(800., 875.)
            
            #set the y-axis label
            plt.ylabel("Station Pressure (hPa)")
        
        elif var_name == "SLP_hPa": #plot sea-level pressure (hPa)
            
            #set y-axis limits/range
            ax.set_ylim(900., 1100.)
            
            #set the y-axis label
            plt.ylabel("Sea-Level Pressure (hPa)")
            
        elif var_name == "SLP_inHg": #plot sea-level pressure (inches of Hg)
            
            #set y-axis limits/range
            ax.set_ylim(28., 32.)
            
            #set the y-axis label
            plt.ylabel("Sea-Level Pressure (inches of Hg)")
            
        elif var_name == "alt": #plot altitude (m)
            
            #set y-axis limits/range
            ax.set_ylim(1400., 1800.)
            
            #set the y-axis label
            plt.ylabel("Altitude (m)")
            
            #plot a horizontal line marking the actual altitude (according to Google
            #    Earth)
            #plt.axhline(y=1617, color='r', linestyle=":", label="1617 m")
            
        elif var_name == "vis": #plot temperature in Celsius
            
            #set y-axis limits/range
            ax.set_ylim(0., 1600.)
            
            #set the y-axis label
            plt.ylabel("Visible (W m$^-2$)")
            
        elif var_name == "ir": #plot temperature in Fahrenheit
            
            #set y-axis limits/range
            ax.set_ylim(0., 10000.)
            
            #set the y-axis label
            plt.ylabel("Infrared (W m$^-2$)")
            
        elif var_name == "uv": #plot temperature in Fahrenheit
            
            #set y-axis limits/range
            ax.set_ylim(0., 700.)
            
            #set the y-axis label
            plt.ylabel("Ultraviolet (W m$^-2$)")
            
        elif var_name == "uvi": #plot temperature in Fahrenheit
            
            #set y-axis limits/range
            ax.set_ylim(0., 7.)
            
            #set the y-axis label
            plt.ylabel("UV Index")
        
        else:
            #if none of the conditions above are met, print an error statement
            #    pointing the user to the potential cause (i.e. spelling)
            print("Variable name not found. Check the spelling of 'var_name'. Program exiting...")
            sys.exit()
            
    #Need to include a section that accounts for the wind BARB plotter
    
    ### UNIVERSAL PLOTTING PARAMETERS ###
    
    #call the function that sets up all the universal plotting parameters:
    #    gridlines, x-axis limits, titles, labels, legends, etc.
    _universal_params(ax,df,mintime,maxtime,sensor,site_ID)
    
    #save the figure by calling the hidden '_save_figure' function
    _save_figure(sensor, save_dir, site_ID, var_name, units, averaged,
                avg_window, mintime, maxtime, plot_opt, tag, df)

    return
    


##############################################################################
###########################    DAILY PLOTTER    ##############################
##############################################################################

#to plot figures on a daily basis within the user-defined time frame, call
#    this function
def daily_plotter(sensor, save_dir, site_ID, var_name, units, averaged,
                  avg_window, mintime, maxtime, plot_opt, tag, df):
    
    #tell the user that the function was called
    print("------------------------------------------------------------------\n")
    print("'daily_plotter' function called...\n")

    ''' Note that the very first occurrence of a 00:00 UTC time in the dataset
    should never occur later than the 1,439th index because there are 1,440
    minutes in a day'''
    
    #set two counters: one to count the total number of days, and the other to
    #    count the number of days that were actually plotted (skipping days
    #    for which there are no data)
    #NOTE: the total count is technically equivalent to n-2 total FULL days for 
    #      time frames not perfectly divisible by 1440 minutes; if the last
    #      interval does not equate to a full day but contains data, it will
    #      still be counted in the total count of days
    total_count = 0 #count for ALL weeks possible within the time frame
    plotted_count = 0 #count for all weeks that were plotted within the time frame
    
    #this line will find the first occurrence of a 00:00 UTC time in the
    #    selected timeframe; this is the start of your range to loop through
    #    for making daily plots
    start = pd.DatetimeIndex(df.time[mintime:maxtime]).indexer_at_time('00:00:00')[0] + mintime
    
    #before getting into the loop, to account for instances such that the
    #    dataset or the time frame set by the user begins with a partial day
    #    (e.g. the first timestamp is NOT 00:00 UTC) plot that partial day all
    #    by itself only up to the index marking the first occurrence of a
    #    00:00 UTC timestamp in the dataset / timeframe (a.k.a. 'start'
    #    variable)
    if df.time[mintime:start].dt.time.empty != True and df.time[mintime:start].dt.time[mintime] != datetime.time(0,0):
        
        #increase total counter by 1
        total_count += 1
        
        #skip the creation of plot if there are no data within the current 1-day
        #    period
        if (averaged == True or averaged == "static") and (df[df.columns[2]][mintime:start].notna().any() == False):
            #we need this special except above because when 'averaged' is set
            #    to either of those two conditions, a new column is created in
            #    the dataframe and it contains a different number of NaNs than
            #    the column from which it was computed->created; the only
            #    change is that we are referring to df.columns[2] instead of
            #    df.columns[1]; this will likely have to change if I add the
            #    ability to average ANY variable (not just wind speed)
            print("%s - %s not plotted --> No data" % (df.time[mintime], df.time[start]))
            pass #don't plot
            
        else:
            if df[df.columns[1]][mintime:start].empty == True:
                #this little condition avoids printing the statement that
                #    "2019-01-08 00:00 - 2019-01-08 00:00" has no data because, of
                #    course, this is a single time so it has no length/data; this
                #    will only happen for datasets or given time frames that
                #    exactly equal 1 day / 1440 minutes
                pass
            
            elif df[df.columns[1]][mintime:start].notna().any() == False:
                #tell the user this time frame was not plotted due to the absence of
                #    any data
                print("%s - %s not plotted --> No data" % (df.time[mintime], df.time[start]))
                pass #move on the next iteration of the loop
            
            #if there is even a single data point within the current time frame,
            #    plot it
            else:
                
                #increase the plotting counter by 1
                plotted_count +=  1
                
                #call the default plotter function here; this also sets up the
                #    universal plotting parameters AND saves the figures all in one
                plotter(sensor, save_dir, site_ID, var_name, units, averaged,
                        avg_window, mintime, start, plot_opt, tag, df)
    
    #since data are recorded every minute, and there are 1440 minutes in 1 day,
    #    we set the range interval to 1440 (equivalent to 'every 1440th index');
    #NOTE: this hard-coded method only works because we explicitly set each
    #      record at a 1-minute interval and we fill any gaps in data with NaNs;
    #      this will get more complicated if you start using raw seconds in
    #      your timestamps
    interval = 1440
    
    #find the ending index of the range over which to plot; this will be the
    #    index of df.time that equals the 'maxtime' specified by the user; this,
    #    too, is simply equal to 'maxtime', but we must add 1 to the index because
    #    the 'range' function does not include the end value
    end = maxtime + 1
    
    #store a list of dates/times that encompass weeks that were not plotted due to
    #    missing data
    
    #######################
    #now, loop through the entire time frame set by the user with 1-week intervals
    #    making a week-long plot of the chosen variable for each iteration
    for d in range(start,end,interval):
        
        #increase total counter by 1
        total_count += 1
        
        #'mintime' and 'maxtime will now change through each iteration of the loop
        #    to serve as the indices defining the 1-day intervals throughout the
        #    dataset over which to plot; the difference between them, however, will
        #    always represent 1 day / 1440 minutes
        mintime = d
        maxtime = d + interval
        
        #set 'maxtime' to the end of the range if 'maxtime' is out of the range
        #    specified; this will only occur if the range is not perfectly
        #    divisible by 1 day / 1440 minutes; in this instance, the very last
        #    figure generated would NOT represent a 1-day period
        if maxtime > end:
            maxtime = end - 1 #now we subtract 1 because set_xlim() includes the
                              #    upper limit given when setting the range; if we
                              #    did not subtract 1, 'maxtime' would be out of
                              #    range for set_xlim()
        
        #skip the creation of plot if there are no data within the current 1-day
        #    period
        if (averaged == True or averaged == "static") and (df[df.columns[2]][mintime:maxtime].notna().any() == False):
            #we need this special except above because when 'averaged' is set
            #    to either of those two conditions, a new column is created in
            #    the dataframe and it contains a different number of NaNs than
            #    the column from which it was computed->created; the only
            #    change is that we are referring to df.columns[2] instead of
            #    df.columns[1]; this will likely have to change if I add the
            #    ability to average ANY variable (not just wind speed)
            print("%s - %s not plotted --> No data" % (df.time[mintime], df.time[maxtime]))
            pass #don't plot
        
        else:
            
            if df[df.columns[1]][mintime:maxtime].empty == True:
                #this little condition avoids printing the statement that
                #    "2019-01-08 00:00 - 2019-01-08 00:00" has no data because, of
                #    course, this is a single time so it has no length/data; this
                #    will only happen for datasets or given time frames that
                #    exactly equal 1 day / 1440 minutes
                pass
            
            elif df[df.columns[1]][mintime:maxtime].notna().any() == False:
                #tell the user this time frame was not plotted due to the absence of
                #    any data
                print("%s - %s not plotted --> No data" % (df.time[mintime], df.time[maxtime]))
                pass #move on the next iteration of the loop
            
            #if there is even a single data point within the current time frame,
            #    plot it
            else:
                
                #increase the plotting counter by 1
                plotted_count +=  1
                
                #call the default plotter function here; this also sets up the
                #    universal plotting parameters AND saves the figures all in one
                plotter(sensor, save_dir, site_ID, var_name, units, averaged,
                        avg_window, mintime, maxtime, plot_opt, tag, df)
        
    return



##############################################################################
###########################    WEEKLY PLOTTER    #############################
##############################################################################

#to plot figures on a weekly basis within the user-defined time frame, call
#    this function
def weekly_plotter(sensor, save_dir, site_ID, var_name, units, averaged,
                   avg_window, mintime, maxtime, plot_opt, tag, df):
    
    #tell the user that the function was called
    print("------------------------------------------------------------------\n")
    print("'weekly_plotter' function called...\n")
    
    #find the starting index of the range over which to plot; this is simply
    #    'mintime' but we will give it a different name because 'mintime' has a
    #    differnt purpose within the 'for' loop below
    start = mintime
    
    #find the ending index of the range over which to plot; this will be the
    #    index of df.time that equals the 'maxtime' specified by the user; this,
    #    too, is simply equal to 'maxtime', but we must add 1 to the index because
    #    the 'range' function does not include the end value
    end = maxtime + 1
    
    #since data are recorded every minute, and there are 10080 minutes in 1 week,
    #    we set the range interval to 10080 (equivalent to 'every 10080th index');
    #NOTE: this hard-coded method only works because we explicitly set each
    #      record at a 1-minute interval and we fill any gaps in data with NaNs;
    #      this will get more complicated if you start using raw seconds in
    #      your timestamps
    interval = 10080
    
    #set two counters: one to count the total number of weeks, and the other to
    #    count the number of weeks that were actually plotted (skipping weeks
    #    for which there are no data)
    #NOTE: the total count is technically equivalent to n-1 total FULL weeks for 
    #      time frames not perfectly divisible by 7 days; if the last interval
    #      does not equate to a full week but contains data, it will still be
    #      counted in the total count of weeks
    total_count = 0 #count for ALL weeks possible within the time frame
    plotted_count = 0 #count for all weeks that were plotted within the time frame
    
    #store a list of dates/times that encompass weeks that were not plotted due to
    #    missing data
    
    #######################
    #now, loop through the entire time frame set by the user with 1-week intervals
    #    making a week-long plot of the chosen variable for each iteration
    for w in range(start,end,interval):
        
        #increase total counter by 1
        total_count += 1
        
        #'mintime' and 'maxtime will now change through each iteration of the loop
        #    to serve as the indices defining the 1-week intervals throughout the
        #    dataset over which to plot; the difference between them, however, will
        #    always represent 1 week / 7 days (i.e. 10080)
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
        
        #skip the creation of plot if there are no data within the current 7-day
        #    period
        if df[df.columns[1]][mintime:maxtime].empty == True:
            #this little condition avoids printing the statement that
            #    "2019-01-08 00:00 - 2019-01-08 00:00" has no data because, of
            #    course, this is a single time so it has no length/data; this
            #    will only happen for datasets or given time frames that
            #    exactly equal 1 week / 7 days
            pass
        elif df[df.columns[1]][mintime:maxtime].notna().any() == False:
            #tell the user this time frame was not plotted due to the absence of
            #    any data
            print("%s - %s not plotted --> No data" % (df.time[mintime], df.time[maxtime]))
            pass #move on the next iteration of the loop
        
        #if there is even a single data point within the current time frame,
        #    plot it
        else:
            
            #increase the plotting counter by 1
            plotted_count +=  1
            
            #call the default plotter function here; this also sets up the
            #    universal plotting parameters AND saves the figures all in one
            plotter(sensor, save_dir, site_ID, var_name, units, averaged,
                    avg_window, mintime, maxtime, plot_opt, tag, df)
        
    return



##############################################################################
###########################    MONTHLY PLOTTER    ############################
##############################################################################

#to plot figures on a monthly basis within the user-defined time frame, call
#    this function
def monthly_plotter(sensor, save_dir, site_ID, var_name,
                    units, averaged, avg_window, mintime, maxtime, plot_opt, tag, df):
    
    #tell the user that the function was called
    print("------------------------------------------------------------------\n")
    print("'monthly_plotter' function called...\n")

    #set two counters: one to count the total number of months, and the other to
    #    count the number of months that were actually plotted (skipping months
    #    for which there are no data)
    #NOTE: the total count is technically equivalent to n-2 total FULL months for 
    #      time frames that do not exactly start(end) on the very beginning(end)
    #      of the month; if the last interval does not equate to a full month
    #      but contains data, it will still be counted in the total count of
    #      days
    total_count = 0 #count for ALL months possible within the time frame
    plotted_count = 0 #count for all months that were plotted within the time frame

    #this line will find the index of the very first day/time for each month in
    #    the whole dataframe
    day1_of_month_idx = df.index[df.set_index('time').index.day == 1][::1440]
    
    #this line will find the index(indices) of the very first day/time for each
    #    month within the time frame set by the user (within 'mintime' and
    #    'maxtime')
    day1_of_month_idx = day1_of_month_idx[(day1_of_month_idx>mintime) & (day1_of_month_idx<maxtime)]
    
    #the starting index of the range over which to plot; this is the first
    #    index of 'day1_of_month_idx'; notice that if 'day1_of_month_idx' has
    #    length of 1, 'start' and 'day1_of_month_idx' are the same
    start = day1_of_month_idx[0]

    #before getting into the loop, to account for instances such that the
    #    dataset or the time frame set by the user begins with a partial month
    #    (e.g. the first timestamp is NOT 00:00 UTC on the first of the mont)
    #    plot that partial month all by itself only up to the index marking the
    #    first of the month in the dataset / timeframe (a.k.a. 'start' variable)
    if (day1_of_month_idx.empty == False) and (mintime not in day1_of_month_idx):
        
        #increase total counter by 1
        total_count += 1
        
        #skip the creation of plot if there are no data within the current 1-day
        #    period
        if (averaged == True or averaged == "static") and (df[df.columns[2]][mintime:start].notna().any() == False):
            #we need this special except above because when 'averaged' is set
            #    to either of those two conditions, a new column is created in
            #    the dataframe and it contains a different number of NaNs than
            #    the column from which it was computed->created; the only
            #    change is that we are referring to df.columns[2] instead of
            #    df.columns[1]; this will likely have to change if I add the
            #    ability to average ANY variable (not just wind speed)
            print("%s - %s not plotted --> No data" % (df.time[mintime], df.time[start]))
            pass #don't plot
            
        else:
            if df[df.columns[1]][mintime:start].empty == True:
                #this little condition avoids printing the statement that
                #    "2019-01-08 00:00 - 2019-01-08 00:00" has no data because, of
                #    course, this is a single time so it has no length/data; this
                #    will only happen for datasets or given time frames that
                #    exactly equal 1 day / 1440 minutes
                pass
            
            elif df[df.columns[1]][mintime:start].notna().any() == False:
                #tell the user this time frame was not plotted due to the absence of
                #    any data
                print("%s - %s not plotted --> No data" % (df.time[mintime], df.time[start]))
                pass #move on the next iteration of the loop
            
            #if there is even a single data point within the current time frame,
            #    plot it
            else:
                
                #increase the plotting counter by 1
                plotted_count +=  1
                
                #call the default plotter function here; this also sets up the
                #    universal plotting parameters AND saves the figures all in one
                plotter(sensor, save_dir, site_ID, var_name, units, averaged,
                        avg_window, mintime, start, plot_opt, tag, df)
                
    #find the ending index of the range over which to plot; this will be the
    #    index of df.time that equals the 'maxtime' specified by the user; this,
    #    too, is simply equal to 'maxtime'
    end = maxtime
    
    #store a list of dates/times that encompass weeks that were not plotted due to
    #    missing data
    
    #######################
    #now, loop through the entire time frame set by the user with 1-week intervals
    #    making a week-long plot of the chosen variable for each iteration
    for m in range(len(day1_of_month_idx)):
        
        #increase total counter by 1
        total_count += 1
        
        #'mintime' and 'maxtime will now change through each iteration of the loop
        #    to serve as the indices defining the 1-month intervals throughout
        #    the dataset over which to plot; the difference between them will
        #    vary depending on the date/time represented by them because the
        #    duration of months are not always equal
        mintime = day1_of_month_idx[m]
        
        if mintime == day1_of_month_idx[-1] and mintime == end:
            #exit the loop if 'mintime' and 'end' are both equal to the last
            #    element of 'day1_of_month_idx'
            break
        
        elif mintime == day1_of_month_idx[-1] and mintime != end:
            #set maxtime to 'end' if the last plot will not span a full month
            #    (i.e. the original 'maxtime' was not equal to the first of a
            #    month)
            maxtime = end
        else:
            #set 'maxtime' to the next element of 'day1_of_month_idx', after
            #    'mintime'
            maxtime = day1_of_month_idx[m+1]
        
        #skip the creation of plot if there are no data within the current 1-day
        #    period
        if (averaged == True or averaged == "static") and (df[df.columns[2]][mintime:maxtime].notna().any() == False):
            #we need this special except above because when 'averaged' is set
            #    to either of those two conditions, a new column is created in
            #    the dataframe and it contains a different number of NaNs than
            #    the column from which it was computed->created; the only
            #    change is that we are referring to df.columns[2] instead of
            #    df.columns[1]; this will likely have to change if I add the
            #    ability to average ANY variable (not just wind speed)
            print("%s - %s not plotted --> No data" % (df.time[mintime], df.time[maxtime]))
            pass #don't plot
        
        else:
            
            if df[df.columns[1]][mintime:maxtime].empty == True:
                #this little condition avoids printing the statement that
                #    "2019-01-08 00:00 - 2019-01-08 00:00" has no data because, of
                #    course, this is a single time so it has no length/data; this
                #    will only happen for datasets or given time frames that
                #    exactly equal 1 day / 1440 minutes
                pass
            
            elif df[df.columns[1]][mintime:maxtime].notna().any() == False:
                #tell the user this time frame was not plotted due to the absence of
                #    any data
                print("%s - %s not plotted --> No data" % (df.time[mintime], df.time[maxtime]))
                pass #move on the next iteration of the loop
            
            #if there is even a single data point within the current time frame,
            #    plot it
            else:
                
                #increase the plotting counter by 1
                plotted_count +=  1
                
                #call the default plotter function here; this also sets up the
                #    universal plotting parameters AND saves the figures all in one
                plotter(sensor, save_dir, site_ID, var_name, units, averaged,
                        avg_window, mintime, maxtime, plot_opt, tag, df)
        
    return

''' From here, you will want to use the indices in that list as the starting
    index from which to plot for each monthly plot. You only want to plot from
    that index to the next index in the list -1 in the dataframe (e.g. index
    for 2020-01-01 00:00 is 1236915 and index for 2020-02-01 00:00 is 1281555
    so you plot from df.plot[1236915:1281555] so because indexing is exclusive
    of the ending value, you don't have to worry about subracting 1). For the
    very last plot in the dataset, you will have to make sure that it plots to
    the end of the time frame, even if not a complete month. Something similar
    to what you did with weekly plotting such that for the last iteration, you
    set the ending index to the last index of the dataframe+1 but make sure to
    subtract that +1 again so that set_xlim is not out of range'''

# #returns a boolean array inditcating whether the datetimeindex given is the
# #    start of the month (doesn't care about time so any time on the first of
# #    the month will also return True); might be useful!
# pd.DatetimeIndex(df.time[mintime:maxtime]).is_month_start


##############################################################################

#only execute the functions if they are explicitly called from the parent
#    3D_main.py program
if __name__ == "__main__":
    plotter()
    daily_plotter()
    weekly_plotter()
    #monthly_plotter()



