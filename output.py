#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov 13 15:55:30 2020

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

#This code computes a number of metrics and analysis statistic from the
#    UCAR/NCAR COMET 3D-PAWS system and generates a file containing these
#    parameters.
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
#    Pandas
#    Sys
#
#
#History:
#    Nov 13, 2020 - First Write
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
#
#
#How to Use:
#    1. Save this file/program in the same directory as the parent program you
#       will use this function in conjunction with
#    2. Import this function in the parent program (no need for file
#       extensions):
#
#       a) from output import <function-name>
#       ... or...
#       b) import output
#
#    3. Call the function in the parent program, ensuring that you pass the 
#       appropriate attributes/parameters:
#
#       a) call_output = <function-name>(directory, var_name, wildcard)
#       ... or...
#       b) call_bmp = output.<function-name>(input1, input2, input3, etc.)
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
#NOTES:



##############################################################################
#########################    IMPORTING MODULES    ############################
##############################################################################

import numpy as np
import pandas as pd
import sys



##############################################################################
################################   OUTPUT   ##################################
##############################################################################

'are the bmp specs different between the different models?'
#these are taken from the sensor manuals themselves
#bmp specs
bmp_t_min = -40.
bmp_t_max = 85.
bmp_p_min = 300.
bmp_p_max = 1100.

#htu21D specs
htu_t_min = -40.
htu_t_max = 125.
htu_rh_min = 0.
htu_rh_max = 100.

#mcp9808 specs
mcp_t_min = -20.
mcp_t_max = 100.

#si1145 specs

#tipping bucket specs

#anemometer specs

#wind vane specs


######################### Uptime within Time Frame ########################### 

#this can only be called AFTER the 'time_checker.py' where 'mintime' and
#    'maxtime' are set to integers
def timeframe_uptime(mintime, maxtime, df):
    #calculate the total uptime based on the number of missing reports,
    #    but within the time frame ('mintime' and 'maxtime') set by the user; must
    #    add 1 to 'maxtime' because indexing ranges in python exclude the very
    #    last index from the range given (e.g. indexing from [0:10] will go from
    #    the zeroeth index to the 9th index, excluding the 10th index)
    #NOTE: if 'mintime' and 'maxtime' are set such that the entire dataset is
    #      being plotted, the uptime calculated below should be the same as that
    #      calculated above in the "Filling gaps with NaNs" subsection
    if mintime != 0 or maxtime != df.index[-1]:
        missing_reports = df[df.columns[1]][mintime:maxtime+1].isna().sum()
        total = pd.Timedelta(len(df.index[mintime:maxtime+1]), unit='m')
        uptime = pd.Timedelta((len(df.index[mintime:maxtime+1]) - missing_reports), unit='m')
        uptime_percent = round((1 - (float(missing_reports) / float(len(df[mintime:maxtime+1])))) * 100., 1)
        print("Uptime during the time frame is %s out of %s (%s%%).\n" % (uptime,total,uptime_percent))
        
        return missing_reports, total, uptime, uptime_percent 
    
#information to add to this output file...
#number of files read
#number of lines skipped
#file names such that lines were skipped (aka 'problem files')
#number of times that time reset (date/timestamps were out of order)
#list of duplicate timestamps (aka 'duplicates')
#number of data gaps
#number of missing reports
#uptime within the whole dataset
#uptime within the user-defined time frame
#uptime after removal of suspicious data points
#number of blips; blip range (min to max)
#standard deviation (running for 10-min, 30-min, 60-min; static for 1-day, 30-day, 1-year, diurnally, seasonally)
#uptime within each of those timescales for running and static periods (running for
#    10-min, 30-min, 60-min; static for 1-day, 30-day, 1-year, diurnally, seasonally)
#standard deviation after removal of suspicious data points


        
        
        