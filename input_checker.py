#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Nov  5 15:13:43 2020

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

#This code checks a number of user inputs from the 3D_main.py program.
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
#       will use this function in conjunction with (3D_main.py)
#    2. Import this function in the parent program (no need for file
#       extensions):
#
#       a) from input_checker import input_checker
#       ... or...
#       b) import input_checker as inputs
#
#    3. Call the function in the parent program, ensuring that you pass the 
#       appropriate attributes/parameters:
#
#       a) check_inputs = input_checker(sensor, var_name, units, averaged, avg_window, reformat, elevation, latitude, longitude)
#       ... or...
#       b) check_inputs = inputs.input_checker(sensor, var_name, units, averaged, avg_window, reformat, elevation, latitude, longitude)
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
#NOTES: 



##############################################################################
#########################    IMPORTING MODULES    ############################
##############################################################################

import numpy as np
import pandas as pd
import sys



##############################################################################
############################    VERIFY INPUT    ##############################
##############################################################################

#first define the function to check the smoothing/averaging parameters;
#    depending on the sensor/variables chosen by the user, this function will
#    get called; if sensors/variables do not have smoothing/averaging allowed,
#    then we don't care what these parameters are and this function does not
#    get called
def _smooth_params(averaged, avg_window):
    
    #tell the user that the function was called
    print("------------------------------------------------------------------\n")
    print("'smooth_params' function called...\n")
    
    #if plotting averaged data, check that the averaging window is valid
    if averaged == True or averaged == "static" or averaged == "resampled":
        if avg_window < 1 or type(avg_window) != int:
            raise ValueError("Averaging window must be an integer greater than or equal to 1.")
        elif avg_window == 1:
            #setting the averaging window to 1 is equivalent to plotting raw data,
            #    so set 'averaged' to False and inform the user
            print("Averaging window set to 1. Plotting raw data...")
            averaged = False
        # elif avg_window >= len(df):
        #     raise ValueError("Averaging window must be less that the total number of data points.")
        else:
            #All other conditions are accepted
            pass
    elif averaged != "static" and averaged != "resampled" and averaged != False:
        #if "averaged" is not equal to any of the other three accepted conditions,
        #    then raise an error
        raise ValueError("'averaged' option not recognized.")
    else:
        #'averaged' should equal False if we got to this point, and in that
        #    case, there no need to do anything
        pass
    
    
    ##########################################################################
    
    #need only return 'averaged' since that variable can change depending on user
    #    inputs
    return averaged


############################### Input Checker ################################

#call this function to check the more critical user inputs
def input_checker(sensor, var_name, units, averaged, avg_window, reformat, elevation, latitude, longitude):
    
    #tell the user that the function was called
    print("------------------------------------------------------------------\n")
    print("'input_checker' function called...\n")
    
    #create a list containing the names of sensors that the user is allowed to
    #    choose from
    sensor_list = ["bmp180", "bmp280", "htu21d", "mcp9808", "si1145", "rain",
                   "anemometer", "wind_vane"]
        
        
    ##################### Check Sensor & Variable/Units ######################
    
    #create a list containing the variable names that the user is allowed to
    #    choose from
    varname_list = ["SLP_hPa", "SLP_inHg", "station_P", "alt", "temp_C",
                    "temp_F", "rel_hum", "vis", "ir", "uv", "uvi"]
    
    #create a list containing the unit identifiers that the user is allowed to
    #    choose from; remember that 'units' are only required for wind speed
    #    measurements and precipitation measurements
    units_list = ["mm","inches","mps","kmph","mph","kts"]
    
    #create a dictionary with the sensor names as keys and variable names / 
    #    units as elements associated with those keys
    dictionary = {sensor_list[0]:varname_list[:6], sensor_list[1]:varname_list[:6],
                  sensor_list[2]:varname_list[4:7], sensor_list[3]:varname_list[4:6],
                  sensor_list[4]:varname_list[7:], sensor_list[5]:units_list[:2],
                  sensor_list[6]:units_list[2:], sensor_list[7]:[]}
    
    #check whether 'sensor' (case insensitive) equals any of the accepted
    #    options in 'sensor_list'...
    if sensor.lower() == sensor_list[0] or sensor.lower() == sensor_list[1]: #BMP180/280
        
        #...if yes, check that 'var_name' was specificed appropriately and is
        #    associated with 'sensor'...
        if var_name in dictionary[sensor_list[0]]:
            pass
        
        #if not associated with the BMP180/280 sensor (or misspelled), print
        #    a message to the user
        else:
            print("'%s' is not an accepted variable name for %s\n" % (var_name,sensor))
            print("Accepted variable names are...")
            print("'%s' for sea-level pressure (hPa)" % varname_list[0])
            print("'%s' for sea-level pressure (inches of Hg)" % varname_list[1])
            print("'%s' for station pressure (hPa)" % varname_list[2])
            print("'%s' for altitude (m)" % varname_list[3])
            print("'%s' for temperature (deg C)" % varname_list[4])
            print("'%s' for temperature (deg F)" % varname_list[5])
            sys.exit()
    
    elif sensor.lower() == sensor_list[2]: #HTU21D
    
        if var_name in dictionary[sensor_list[2]]:
            pass
        
        else:
            print("'%s' is not an accepted variable name for %s\n" % (var_name,sensor))
            print("Accepted variable names are...")
            print("'%s' for temperature (deg C)" % varname_list[4])
            print("'%s' for temperature (deg F)" % varname_list[5])
            print("'%s' for relative humidity (%%)" % varname_list[6])
            sys.exit()
        
    elif sensor.lower() == sensor_list[3]: #MCP9808
    
        if var_name in dictionary[sensor_list[3]]:
            pass
        
        else:
            print("'%s' is not an accepted variable name for %s\n" % (var_name,sensor))
            print("Accepted variable names are...")
            print("'%s' for temperature (deg C)" % varname_list[4])
            print("'%s' for temperature (deg F)" % varname_list[5])
            sys.exit()
        
    elif sensor.lower() == sensor_list[4]: #SI1145
        
        if var_name in dictionary[sensor_list[4]]:
            pass
        
        else:
            print("'%s' is not an accepted variable name for %s\n" % (var_name,sensor))
            print("Accepted variable names are...")
            print("'%s' for visible light (W/m^2)" % varname_list[7])
            print("'%s' for infrared radiation (W/m^2)" % varname_list[8])
            print("'%s' for ultraviolet radiation (W/m^2)" % varname_list[9])
            print("'%s' for ultraviolet index (unitless)" % varname_list[10])
            sys.exit()
        
    elif sensor.lower() == sensor_list[5]: #RAIN
    
        if units in dictionary[sensor_list[5]]:
            pass
        
        else:
            print("'%s' is not an accepted unit identifier for %s\n" % (units,sensor))
            print("Accepted unit identifiers are...")
            print("'%s' for millimeters" % units_list[0])
            print("'%s' for inches" % units_list[1])
            sys.exit()
        
    elif sensor.lower() == sensor_list[6]: #ANEMOMETER
    
        if units in dictionary[sensor_list[6]]:
            #check the averaging options
            averaged = _smooth_params(averaged, avg_window)
            
        else:
            print("'%s' is not an accepted unit identifier for %s\n" % (units,sensor))
            print("Accepted unit identifiers are...")
            print("'%s' for meters per second (m/s)" % units_list[2])
            print("'%s' for kilometers per hour (km/h)" % units_list[3])
            print("'%s' for miles per hour (mi/h)" % units_list[4])
            print("'%s' for knots" % units_list[5])
            sys.exit()
        #will need to collect the "Converting the Data" section in this sensor's function
        
    elif sensor.lower() == sensor_list[7]: #WIND VANE
        #wind direction has no other inputs
        pass
    
    #if 'sensor' does not equal any of the accepts options...
    else:
        #print an error message, tell the user what options ARE accepted, then
        #    exit the program
        print("'%s' is not an accepted sensor name\n" % sensor)
        print("Accepted sensor names are...\n")
        for sensor in sensor_list:
            print(sensor)
        sys.exit()
    
    
    
    #------------------------------------------------------------------------#
    #-----------------    VERIFYING CONVERTER / QA INPUT    -----------------#
    #------------------------------------------------------------------------#
    
    #write this section to check the the input parameters satisfy the
    #    requirements of the converter.py and quality_assurance.py, such as
    #    'mintime' and 'maxtime' should be 00Z; this will simplify a lot of 
    #    things for the converter, at the very least
    
    #if converting data, check that the few parameters that are exclusive to
    #    the converter.py are valid
    if reformat == True:
        
        #check that latitude and longitude are within acceptable limits
        if latitude < -90. or latitude >= 90.:
            raise ValueError("Latitude out of range.")
        
        if longitude < -180. or longitude > 180.:
            raise ValueError("Longitude out of range.")
        
        #check that elevation is within acceptable limits
        if elevation < 0. or elevation > 8900.:
            raise ValueError("Elevation out of range.")
        
    elif reformat == False:
        pass
    else:
        print("'reformat' option not recognized (must be either True or False)")
        sys.exit()
    
    
    ##########################################################################
    
    print("------------------------------------------------------------------")
    
    #return 'averaged' because depending on the combination of accepted
    #    user inputs (e.g. averaged = True and avg_window = 1), this
    #    variable can change to allow the program to continue
    return averaged

   
if __name__ == "__main__":
    input_checker()
    
    

