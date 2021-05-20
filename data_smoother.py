#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov  6 17:29:21 2020

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

#This code checks the smoothing (averaging) parameters the data given based on user inputs from the
#    3D_main.py program.
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
#    Nov 05, 2020 - First Write
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

import numpy as np
import pandas as pd
import sys


####################### Check Averaging Parameters #######################

''' If/when the ability for smoothing/averaging for ALL sensors/variables
occurs, you will need to account for 'var_name' when creating the new column
in the dataframe '''

def smoothing(averaged, avg_window, df, plot_opt):
    
    #tell the user that the function was called
    print("------------------------------------------------------------------\n")
    print("'smoothing' function called...\n")
    
    #This function will compute any user-defined specifics for averaging the data.
    #    The options here include "do nothing" i.e. raw data, computing a running
    #    average based on a user-defined averaging window (e.g. 5 minutes, 10
    #    minutes 13 minutes, etc.), plotting static-averaged data (useful for
    #    longer time series), or plotting a lower density of data (useful for
    #    longer time series)
    if averaged == True:
        if plot_opt != "":
            #computing the running average of wind speed based on the user-defined
            #    averaging window; add this as a new column in the existing dataframe
            #    and shift the computed values back in time X-1 minutes where X is the
            #    user-defined averaging window, so that the value computed over that
            #    duration is now valid for the beginning of the time frame (i.e. a 10-
            #    min running average beginning at 08:00 will be valid [plotted] for
            #    [at] 08:00); the iloc[:,1] tells it to only go this for all values
            #    in the second column (identified by the first index)
            print("Plotting %s-min running averaged data..." % avg_window)
            df['windspd_avg'] = df.iloc[:,1].rolling(window=avg_window).mean().shift(-(avg_window-1))
        
        else:
            df['windspd_avg'] = df.iloc[:,1].rolling(window=avg_window).mean().shift(-(avg_window-1))
        
    elif averaged == False:
        if plot_opt != "":
            #if averaging is set to False, then do nothing and continue on your merry
            #    way
            print("Plotting raw data...")
            pass
    
    elif averaged == "static":
        if plot_opt != "":
            #"static" average based on the user-defined averaging window but with a
            #    temporal resolution equivalent to the averaging window; this line is
            #    exactly the same as with the running average, but we will select every
            #    nth data point (beginning with the first) when plotting since that is
            #    equivalent to computing the static average
            print("Plotting %s-min static averaged data..." % avg_window)
            df['windspd_avg'] = df.iloc[:,1].rolling(window=avg_window).mean().shift(-(avg_window-1))
        
        else:
            df['windspd_avg'] = df.iloc[:,1].rolling(window=avg_window).mean().shift(-(avg_window-1))
    
    elif averaged == "resampled":
        if plot_opt != "":
            #resampling; there is no need to do anything here, but the "resampled"
            #    option will plot every nth raw data point where 'n' is the averaging
            #    window ("avg_window") set by the user
            print("Plotting every %s data points (minutes)..." % avg_window)
    
    #NOTE: we need not account for the potential of "averaged" not being an
    #      accepted option because the input_checker will handle that exception
    
    
    ##########################################################################
    
    print("------------------------------------------------------------------")
    
    #return the dataframe because it can get modified depending on the
    #    combination of smoothing/averaging parameters
    return df

if __name__ == "__main__":
    smoothing()




