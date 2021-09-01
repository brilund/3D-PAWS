#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Dec 10 15:20:44 2020

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

#This code reads in all available sensor data (from a specific folder
#    structure) and assigns flags to every datum based on several tiers of
#    data quality assessment; this script and its functions are called from a
#    parent program.
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
#    First Write - Unknown
#
#
#PLANNED FEATURES:
#
#
#HOW TO USE:
#    1. Setup a folder structure for the data following the instructions in
#       'Folder Structure' section
#    2. Save this file/program in the same directory as the parent program you
#       will use this function in conjunction with
#    3. Import this function in the parent program (no need for file
#       extensions):
#
#       a) from quality_assurance import QA_main
#       ... or...
#       b) import quality_assurance as QA
#
#    4. Call the function in the parent program, ensuring that you pass the 
#       appropriate attributes/parameters:
#
#       a) check_time = QA_main(directory, df)
#       ... or...
#       b) call_time = QA.QA_main(directory, df)
#
#    5. Run the parent program within terminal (e.g. "python 3D_main.py"),
#       or open the parent program in Spyder and run from there.
#
#
#FOLDER STRUCTURE:
#    1. Create a parent folder (preferably named for the site the data are
#           from) that will contain the subfolders for each sensor you want to
#           read in. The full, absolute path to this folder should be what you
#           give to the 'directory' variable in '3D_main.py'
#    2. The parent folder should contain ONLY the subfolders for each sensor
#           you want to read in, no additional files can be in this parent
#           folder; it is critical that each sensor subfolder within each
#           station folder follow the same naming convention (e.g. 'bmp' for
#           the BMP180 or BMP280, 'winddir' for wind direction from the wind
#           vane, etc.)
#    3. If there are two BMP folders in the parent folder (e.g. BMP180
#           and BMP280), you will either need to combine both folders into one,
#           knowing that you will have a mixture of the two within your
#           dataset, OR, eliminate one folder from the parent folder
#       NOTE: it is important that the names of the folders within the parent
#           folder (the folders that house the data files) make sense, in that,
#           they contain a portion or all of the sensor name within the
#           folder name itself (e.g. 'bmp' for the BMP180 or BMP280, 'winddir'
#           for wind direction from the wind vane, etc.)
#
#
#Example header from files --> no file header(s)!!! (this could change...)
#
#Example data from files:
#    
#
#
#NOTES: you must select a filepath in 3D_main.py (the 'directory' variable)
#       that has data on either side of the time period chosen by 'mintime'
#       and 'maxtime' in 3D_main.py. After that, even if no other sensor
#       folder has data, the program should run normally. This means that if
#       your time frame is 202001010000 - 202001020000 and the chosen sensor
#       does not have data for that period but has data before AND after that,
#       the program will still run.
#       Even if other sensor folders (other than the first one read in as set
#       by 'directory' in 3D_main.py) do not have data for the selected
#       timeframe, BUT there is data in the sensor folder, the program will
#       function as normal. However, if there is zero data within any sensor
#       folder, the program will break and you should simply remove that
#       sensor folder from the parent folder.
#       If you have two BMP sensor folders (whether both have data or only one
#       has data), you must eliminate one folder, or combine data from both
#       folders into one BMP folder. Know that if you combine data into one
#       folder and there are any overlapping timestamps, the second set of
#       data read in with identical timestamps as the first set will be
#       discarded. This will depend on your file naming convention.


#the naming convention for the columns added to the data frame are as
#    follows...
#First letter (lowercase) represents the variable being tested. It is
#    followed by an underscore and two capital letters: LC, IC, TC, CC.
#    LC = Limits Check
#    IC = Internal Check
#    TC = Temporal Check
#    CC = Climatological Check
#For example, "t_LC" refers to the column(s) representing temperatures
#    flagged during the LIMITS CHECK. Only variables that are directly
#    measured from the sensor itself are checked during these procedures.
#    Variables that are computed using the measured variables (e.g.
#    temperature in Fahrenheit) are NOT checked, but are flagged if any
#    one of the measured variables used to calculate it are flagged.



##############################################################################
#########################    IMPORTING MODULES    ############################
##############################################################################

import numpy as np
import pandas as pd
import glob
import os
import reader
import sys



##############################################################################
#############################    LIMITS TEST    ##############################
##############################################################################

def limits_test(sensor, df):
    
    ''' Since this entire program reads in all data from a single station,
        and some procedures will rely on the quality of other varialbes, we
        must rewrite this section to perform the limits test on ALL variables.
        It could be a loop through all column names'''

    #performing simple limits test on the data to verify that measurements are
    #    within the sensor's specifications according to the sensor's manual
    
    'are the bmp specs different between the different models?'
    #these are taken from the sensor manuals themselves
    #bmp specs
    bmp_t_min = -40.  # deg C
    bmp_t_max = 85.   # deg C
    bmp_p_min = 300.  # hPa
    bmp_p_max = 1100. # hPa
    bmp_a_min = -500. # meters
    bmp_a_max = 9000. # meters
    bmp_rh_min = 0.   # %
    bmp_rh_max = 100. # %
    
    #htu21D specs
    htu_t_min = -40.  # deg C
    htu_t_max = 125.  # deg C
    htu_rh_min = 0.   # %
    htu_rh_max = 100. # %
    
    #mcp9808 specs
    mcp_t_min = -40.  # deg C
    mcp_t_max = 125.  # deg C
    
    #si1145 specs
    si_min = 0.       # W m^-2
    si_max = 13000.   # W m^-2; this is a theoretically maximum determined by
                      #    analyzing the absolutely maximum SI readings for all
                      #    stations within the tropical latitudes
    
    #tipping bucket specs
    tb_min = 0.       # mm
    tb_max = 5.       # mm this is based on a WMO maximum recorded 1-hour
                      #    rainfall total divided by 60 to yield the 1-minute
                      #    total of 5 mm in a 1 minute period.
    int_tb_max = 305. # mm this is the 1-hour cumulative maximum rainfall total
    
    #anemometer specs
    ws_min = 0.       # m/s
    ws_max = 75.      # m/s
    
    #wind vane specs
    wd_min = 0.       # deg
    wd_max = 360.     # deg
    
    
    ############################### BMP Sensor ###############################

    if sensor.lower() == "bmp180" or sensor.lower() == "bmp280":
        #create a new column for each meausure variable (temp_C, station_P and
        #    alt) filled with 0s and 1s; 0s where values are within spec, and
        #    1s where values are out of spec
        
        #if either or both T and P our out of spec, then all the subsequent
        #    variables calculated from them are also out of spec and must be
        #    flagged at the very least, discarded if necessary
        #temp_F need only be flagged if temp_C is flagged
        #SLP_hPa and SLP_inHg must be flagged if ANY measured value is out of
        #    spec (temp_C, altitude, or pressure)
        #altitude must be flagged if "" and/or "" is flagged
        
        #generate separate arrays of zeros the same length as the dataframe;
        #    these will each serve as the columns of flags in the dataframe for
        #    their respective measured variables
        t_LC = np.zeros(len(df)) # temperature
        p_LC = t_LC              # pressure
        a_LC = t_LC              # altitude
        
        #find the indices in the dataframe for each measured variable such that
        #    the value is outside the specifications for the given variable
        t_idx = df.index[(df.temp_C <= bmp_t_min) | (df.temp_C >= bmp_t_max)]
        p_idx = df.index[(df.station_P <= bmp_p_min) | (df.station_P >= bmp_p_max)]
        a_idx = df.index[(df.alt <= bmp_a_min) | (df.alt >= bmp_a_max)]
        
        #for the indices in the dataframe of values that are outside the
        #    specifications, change the values at the same indices in the zero
        #    arrays to ones (these indicate the values out of range)
        t_LC[t_idx] = 1
        p_LC[p_idx] = 1
        a_LC[a_idx] = 1
        
        # #create a new column full of zeros that will be flipped to ones if
        # #    they fail the limits check
        # df['t_LC'] = 0.
        # df.t_LC = df.t_LC[df.index[(df.temp_C <= bmp_t_min) | (df.temp_C >= bmp_t_max)]] = 1
        
        #add new columns in the dataframe indicating with 1s where the
        #    temperature, pressure, altitude, and relative humidity (for BME
        #    only) records are flagged for exceeding the limits test, 0s for
        #    the opposite
        df.insert(3,"t_LC",t_LC)
        df.insert(5,"p_LC",p_LC)
        df.insert(9,"a_LC",a_LC)
    
    
    ############################# HTU21D Sensor ##############################
    
    if sensor.lower() == "htu21d":
    
        #temp_F must be flagged only if temp_C is flagged
    
        #generate separate arrays of zeros the same length as the dataframe;
        #    these will each serve as the columns of flags in the dataframe for
        #    their respective measured variables
        t_LC = np.zeros(len(df)) # temperature
        rh_LC = t_LC             # relative humidity
        
        #find the indices in the dataframe for each measured variable such that
        #    the value is outside the specifications for the given variable
        t_idx = df.index[(df.temp_C <= htu_t_min) | (df.temp_C >= htu_t_max)]
        rh_idx = df.index[(df.rel_hum <= htu_rh_min) | (df.rel_hum >= htu_rh_max)]
        
        #for the indices in the dataframe of values that are outside the
        #    specifications, change the values at the same indices in the zero
        #    arrays to ones (these indicate the values out of range)
        t_LC[t_idx] = 1
        rh_LC[rh_idx] = 1
        
        #add new columns in the dataframe indicating with 1s where the
        #    temperature, pressure, altitude, and relative humidity (for BME
        #    only) records are flagged for exceeding the limits test, 0s for
        #    the opposite
        df.insert(3,"t_LC",t_LC)
        df.insert(5,"rh_LC",rh_LC)
    
    
    ############################# MCP9808 Sensor #############################
    
    if sensor.lower() == "mcp9808":
    
        #temp_F must be flagged only if temp_C is flagged
        
        #generate separate arrays of zeros the same length as the dataframe;
        #    these will each serve as the columns of flags in the dataframe for
        #    their respective measured variables
        t_LC = np.zeros(len(df)) # temperature
        
        #find the indices in the dataframe for each measured variable such that
        #    the value is outside the specifications for the given variable
        t_idx = df.index[(df.temp_C <= mcp_t_min) | (df.temp_C >= mcp_t_max)]
        
        #for the indices in the dataframe of values that are outside the
        #    specifications, change the values at the same indices in the zero
        #    arrays to ones (these indicate the values out of range)
        t_LC[t_idx] = 1
        
        #add new columns in the dataframe indicating with 1s where the
        #    temperature, pressure, altitude, and relative humidity (for BME
        #    only) records are flagged for exceeding the limits test, 0s for
        #    the opposite
        df.insert(3,"t_LC",t_LC)
    
    
    ############################# SI1145 Sensor ##############################
    
    if sensor.lower() == "si1145":
    
        #generate separate arrays of zeros the same length as the dataframe;
        #    these will each serve as the columns of flags in the dataframe for
        #    their respective measured variables
        si_LC = np.zeros(len(df)) # temperature
        
        #find the indices in the dataframe for each measured variable such that
        #    the value is outside the specifications for the given variable
        si_idx = df.index[(df.temp_C < si_min) | (df.temp_C > si_max)]
        
        #for the indices in the dataframe of values that are outside the
        #    specifications, change the values at the same indices in the zero
        #    arrays to ones (these indicate the values out of range)
        si_LC[si_idx] = 1
        
        #add new columns in the dataframe indicating with 1s where the
        #    temperature, pressure, altitude, and relative humidity (for BME
        #    only) records are flagged for exceeding the limits test, 0s for
        #    the opposite
        df.insert(5,"si_LC",si_LC)
    
    
    ############################### Anemometer ###############################
    
    if sensor.lower() == "anemometer":
    
        #generate separate arrays of zeros the same length as the dataframe;
        #    these will each serve as the columns of flags in the dataframe for
        #    their respective measured variables
        ws_LC = np.zeros(len(df)) # temperature
        
        #find the indices in the dataframe for each measured variable such that
        #    the value is outside the specifications for the given variable
        ws_idx = df.index[(df.wind_speed < ws_min) | (df.wind_speed > ws_max)]
        
        #for the indices in the dataframe of values that are outside the
        #    specifications, change the values at the same indices in the zero
        #    arrays to ones (these indicate the values out of range)
        ws_LC[ws_idx] = 1
        
        #add new columns in the dataframe indicating with 1s where the
        #    temperature, pressure, altitude, and relative humidity (for BME
        #    only) records are flagged for exceeding the limits test, 0s for
        #    the opposite
        df.insert(2,"ws_LC",ws_LC)
    
    
    ############################### Wind Vane ################################
    
    if sensor.lower() == "wind_vane":
    
        #generate separate arrays of zeros the same length as the dataframe;
        #    these will each serve as the columns of flags in the dataframe for
        #    their respective measured variables
        wd_LC = np.zeros(len(df)) # temperature
        
        #find the indices in the dataframe for each measured variable such that
        #    the value is outside the specifications for the given variable
        wd_idx = df.index[(df.wind_dir < wd_min) | (df.wind_dir > wd_max)]
        
        #for the indices in the dataframe of values that are outside the
        #    specifications, change the values at the same indices in the zero
        #    arrays to ones (these indicate the values out of range)
        wd_LC[wd_idx] = 1
        
        #add new columns in the dataframe indicating with 1s where the
        #    temperature, pressure, altitude, and relative humidity (for BME
        #    only) records are flagged for exceeding the limits test, 0s for
        #    the opposite
        df.insert(2,"wd_LC",wd_LC)
    
    
    ############################ Tipping Bucket ##############################
    
    if sensor.lower() == "rain":
        
        #there are no real "limits", per se, to how many tips can occur; there
        #    are physical contraints climatologically speaking but the bucket
        #    can tip and many times as it wants, technically. Perhaps a limits
        #    test from a mechanical perspective is not the best approach
    
        #generate separate arrays of zeros the same length as the dataframe;
        #    these will each serve as the columns of flags in the dataframe for
        #    their respective measured variables
        tb_LC = np.zeros(len(df)) # temperature
        
        #find the indices in the dataframe for each measured variable such that
        #    the value is outside the specifications for the given variable
        tb_idx = df.index[(df.rain < tb_min) | (df.rain > tb_max)]
        
        #for the indices in the dataframe of values that are outside the
        #    specifications, change the values at the same indices in the zero
        #    arrays to ones (these indicate the values out of range)
        tb_LC[tb_idx] = 1
        
        #add new columns in the dataframe indicating with 1s where the
        #    temperature, pressure, altitude, and relative humidity (for BME
        #    only) records are flagged for exceeding the limits test, 0s for
        #    the opposite
        df.insert(2,"tb_LC",tb_LC)
    
    
    ##########################################################################
    
    print("------------------------------------------------------------------")
    
    #
    return df
    
    

##############################################################################
######################    INTERNAL CONSISTENCY TEST    #######################
##############################################################################

# #here is where the physical limitiations of each variable will be pitted
# #    against all other variables (where applicable) to determine validity,
# #    for example, dewpoint cannot exceed temperature

# def IC_test(sensor, df):
#
#     #set wind direction to zero if wind SPEED is below some threshold
#
#     #here is where you can set limitations (and subsequent flags on those
#     #    that exceed the limitations) for the SI1145 readings based on the
#     #    known amounts of incoming solar radiation from both total and 
#     #    specific spectral range contributions

#     #if liquid precip is reported, temperature should be at least ???
#     #how do we determine liquid precipiation with the data we have???
#     #humidity should also be above some threshold (75% ???)



##############################################################################
######################    TEMPORAL CONSISTENCY TEST    #######################
##############################################################################

#here is where we will flag any data blips (sharp, non-physical rises or
#    decreases) or runs (extended periods of non-/low-variability) in data
#NOTE: blip tests and run tests will vary depending on the sensor/variable
#    type

def temporal_test(sensor, df):

    if sensor.lower() == "anemometer":
        
        print(sensor)
        
        #testing wind data requires both wind speed and direction data, so
        #    both sensor's data must be read in if performing these tests
        #beware of erroneously flagged calm winds (speed and direction); you may
        #    have to set a threshold of wind speed such that there is a higher
        #    tolerance for excessively low variability IF wind speeds are below
        #    some statistically significant, predetermined threshold
        
        #consider setting wind direction to zero for wind speeds less than X m/s???
        #runs in wind direction are very likely the result of calm winds
        
        #first, find 
        
    ############################### Blip Test ################################
    
    #due to the turbulent nature of wind, blip testing for wind data is more
    #    like scanning for abnormally high variability

    #blip testing could be a two-tiered test comprised of a first pass that
    #    flags any datum about which the consecutive forward-first
    #    differences are non-zero and of opposite sign; the second pass can
    #    consist of testing that flagged datum against a threshold
    #    determined by a moving window of standard deviation calculations;
    #    if the datum fails both tests, it is flagged; data that are flagged
    #    by only one test should be manually inspected; consider a 5- to
    #    10-minute window; this may flag some frontal passages for which you
    #    may need to implement additional tests like checking other
    #    variables (wind speed and/or direction change, humidity change,
    #    pressure change, etc.)
    
    #in the interest of time, if a user specifies a subset of the dateset by
    #    setting 'mintime' and 'maxtime' to something other than the very
    #    first and last timestamp in the dataset, you may want to perform this
    #    particular procedure on only the subset of data specified.
    #NOTE: if you only apply this test to the specified subset, you may as
    #      well do the same for all other procedures; this will also affect
    #      your plans for the output file
    #also try to test for jumps/steps using similar methods
    
    #precip data will likely need to be exempt from temporal consistency tests
    #    since the very nature of precipitation means that there will
    #    inevitably be long runs (like with no rain occurring) and blips
    
    
    ################################ Run Test ################################
    
    #must also test for runs in data; start by flagging values i such that the 
    #    next adjacent value i+1 is equivalent to i. For every i+n value
    #    thereafter that does not change, these values will be flagged. The
    #    very first occurrence of the run will NOT be flagged
    
    #due to the turbulent nature of wind, run testing for wind data is more
    #    like scanning for abnormally low variability
    
    
    if "bmp" in sensor.lower():
        print(sensor)
        
        #barring extreme weather phenomenon, temperature should not vary by
        #    much in a 1-minute period
        #could take the average/mean of the running 60-minute standard
        #    deviation and use that as the maximum difference threshold, or
        #    find the maximum standard deviations
        
    if "htu" in sensor.lower():
        
        #first find the running 1-hour standard deviation for temperature and
        #    humidity
        #NOTE: the column references here will not work if the limits test is
        #    performed above because the flag columns are inserted to the
        #    right of the column they refer to
        T_limits = df.iloc[:,1].rolling(window=60).std(skipna=True).mean()
        RH_limits = df.iloc[:,2].rolling(window=60).std(skipna=True).mean()
        
        #find every datum about which the consecutive forward-first
        #    differences are of opposite sign
        # use df.diff()
        
        #create the temperature and RH temporal consistency flag test column
        #    and fill with zeros
        df['t_TC'] = 0.
        #flip zeros to 1s for any row such that the associated temperature is
        #    greater than the prescribed temperature 3-standard-deviation
        #    threshold
        df.t_TC = df.t_TC[df.index[df.temp_C > 3*T_limits]] = 1
    
        


##############################################################################
######################    CLIMATOLOGICAL LIMITS TEST    ######################
##############################################################################

def climo_test(sensor, df):

    #here might be the appropriate place to place an upper limit on the
    #    radiation sensor's readings
    #t_min = -80.   # this minimum is not used because the WMO Guide's
                    # minimum is well below the lower limit of this
                    # sensor
    t_max = 60.     # deg C
    p_min = 500.    # hPa
    p_max = 1080.   # hPa
    a_min = 0.      # meters
    a_max = 8850.   # meters (based on the elevation of the summit of Mt. Everest)
    #rh_min = 0.    # these limits are within or equivalent to those set by
                    # sensor specification, hence, not necessary
    #rh_max = 100.  # " "
    
    si_min = 0.     # W m^-2
    si_max = 13000. # W m^-2
    
    precip_min = 0. # mm
    precip_max = 5. # mm
    
    #anemometer specs
    ws_min = 0.     # m/s
    ws_max = 75.    # m/s
    
    #wind vane specs
    wd_min = 0.     # deg
    wd_max = 360.   # deg



##############################################################################
##########################    QUALITY ASSURANCE    ###########################
##############################################################################

#here is the equivalent of '3D_main.py' for the quality assurance procedures
def QA_main(directory, df):

    #since performing QA requires that all data be read in, here we loop through
    #    each sensor's subfolder from the parental station folder, calling the
    #    appropriate reader.py function as we go. These data frames will be
    #    aligned by time and joined together into a single dataframe. Then, the
    #    varying QA procedures will be called: limits tests, temporal tests,
    #    internal tests, and finally, climatological tests. Based on the tests,
    #    the sensor/variable combo in question will be flagged, and all other data
    #    will be dropped from the dataframe
    #NOTE: the data returned may require manual inspection for erroneously
    #    flagged data
    
    #consider having two levels of QA: one that is concerned only with the
    #    sensor specified in 3D_main.py, thus, does not need the entire
    #    station's dataset read in, and one that IS concerned with assuring
    #    all the data; the later form can be considered a stricter form of
    #    assurance
    
    
    
    
    
    
    
    
    #this is the parent/station directory; it should be only one level up from
    #    the directory given in '3D_main.py' for the 'directory' variable; the
    #    "...[:-1]" removes the trailing forward slash, allowing for the
    #    os.path.dirname to collect the folder path one level above
    parent_dir = os.path.dirname(directory[:-1])
    
    #collect all the folders within the parent/station folder 'parent_dir' and
    #    sort them
    folder_list = sorted(glob.glob(parent_dir + "/*"))
    
    #check to see if there is more than 1 'bmp' folder in the parent/station
    #    folder
    if len(['bmp' for folder in folder_list if 'bmp' in folder.lower()]) > 1:
        print("There is more than 1 BMP folder in the parent folder. Combine your BMP folders, or remove one from the parent folder.")
        sys.exit()
        
    #remove the sensor folder that was already read in via '3D_main.py'
    folder_list.remove(directory[:-1])
    
    #initiate the sensor list
    sensor_list = []
    #collect the sensor name from each folder path in folder_list
    for folder in folder_list:
        sensor_list.append(folder[len(parent_dir)+1:]) 
        
    #check to see if there are the same number of sensor folders in the parent
    #    folder as there are sensors in the 'sensor_list'
    #NOTE: the odds of this condition ever arising should be next to none
    #    since the sensor_list is generated from the folder_list, but this
    #    checker is here just in case.
    if len(sensor_list) != len(folder_list):
        raise ValueError("Number of sensors is not equal to the number of folders.")
        
    else:
        pass
    
    
    #zip up the contents of the sensor and folder lists, so that each sensor
    #    name given by the 'sensor' variable is matched with its corresponding
    #    folder containing the data for said sensor (set by 'folder_list')
    tuple_lst = list(zip(folder_list,sensor_list))
    
    #need this because it is an input for the 'reader.py'
    wildcard = "*"
    
    #check/ensure that the order of file paths matches that of the
    #    sensor list?????
    #REPLY: don't need to check this with the current method I have because
    #    the sensor list is generated from the folder_list so by default, they
    #    they will be in the same
        
    #within the parent station folder, loop through each sensor's data folder
    for folder,sensor in tuple_lst:
        
        #add a forward slash and wildcard character to the directory path
        full_path = folder + "/*"
    
           
            
        #--------------------------------------------------------------------#
        #-----------------------    READ IN FILE(S)   -----------------------#
        #--------------------------------------------------------------------#
        
        #call the appropriate function based on the sensor/variable name; need a bunch
        #    'if' statments here
        
        
        #read in the dataframe(s) by calling the function designed to read the data;
        #    this is pre-processed data being read in so any sorting, removal of
        #    duplicate timestamps, data conversions, etc. is done before these
        #    dataframes are read into this program. Parameters such as averaging and
        #    averaging window are specified in THIS program and given to the other
        #    program's function so that parameters in the other program do not override
        #    the ones used for THIS program
        
        if "bmp" in sensor.lower():
            call_reader = reader.bmp(full_path, wildcard)
        elif "htu" in sensor.lower():
            call_reader = reader.htu21d(full_path, wildcard)
        elif "mcp" in sensor.lower():
            call_reader = reader.mcp9808(full_path, wildcard)
        elif "1145" or "radiation" in sensor.lower():
            call_reader = reader.si1145(full_path, wildcard)
        elif "rain" or "tip" or "bucket" or "gauge" in sensor.lower():
            call_reader = reader.rain_gauge(full_path, wildcard)
        elif "vane" or "dir" or "direction" in sensor.lower():
            call_reader = reader.wind_vane(full_path, wildcard)
        elif "speed" or "spd" or "anemometer" in sensor.lower():
            call_reader = reader.anemometer(full_path, wildcard)
        else:
            print("Cannot determine sensor type in the given folder names. Consider the following naming convention...\n")
            print("'bmp' for the BMP180, BMP280, or BME sensors.")
            print("'htu21d' for the HTU21D sensor.")
            print("'mcp9808' for the MCP9808 sensor.")
            print("'si1145' for the light / radiation sensor.")
            print("'rain' for the rain gauge / tipping bucket.")
            print("'winddir' for the wind vane")
            print("'windspd' for the anemometer.")
            print("Program exited...\n")
            sys.exit()
        
        #df = reader."%s"(directory, wildcard) % sensor
        df_temp = call_reader[0]
        missing_reports_times = call_reader[1]
        
        
        
        #--------------------------------------------------------------------#
        #----------------    ADJUST COLUMN NAMES & MERGE    -----------------#
        #--------------------------------------------------------------------#
        
        ''' For QA procedures requiring more than one sensor's dataset,
            consider how you might handle instances such that there is no data'''
        
        
        #change the column names to include the sensor name for the HTU, BMP,
        #    and MCP so that we can distinguish between the 3 temperatures
        
        if sensor.lower() == "bmp180" or "bmp280":
            #add sensor name to the all column names except for the 'time'
            #    column
            df_temp = df_temp.rename(columns={'temp_C':'%s_tempC' % sensor,
                                              'temp_F':'%s_tempF' % sensor})
            
        elif sensor.lower() == "htu21d":
            #add sensor name to the all column names except for the 'time'
            #    column
            df_temp = df_temp.rename(columns={'temp_C':'%s_tempC' % sensor,
                                              'rel_hum':'%s_relhum' % sensor,
                                              'temp_F':'%s_tempF' % sensor})
        
        elif sensor.lower() == "mcp9808":
            #add sensor name to the all column names except for the 'time'
            #    column
            df_temp = df_temp.rename(columns={'temp_C':'%s_tempC' % sensor,
                                              'temp_F':'%s_tempF' % sensor})
            
        else:
            #no other sensors share variable names so we don't need to add the
            #    sensor name in front of the rest of the variables
            pass
        
        
        #add the newly-read-in dataframe to the main exisiting dataframe; the
        #    parameters set here create the UNION of the merged datasets, so
        #    that no data is lost from either dataframe; this means that where
        #    there is no overlap, the values are simply NaNs
        df = df.join(df_temp.set_index('time'), on='time', how='outer', sort=True)
        
        #reset the indices so that they are in monotonically increasing order,
        #    beginning with zero
        df = df.set_index('time').sort_index().reset_index()
        
    ### END OF 'subfolder'/'sensor' LOOP ###
    

    #------------------------------------------------------------------------#
    #---------------------    CALL the QA PROCEDURES    ---------------------#
    #------------------------------------------------------------------------#

    ############################# Limits Test ################################

    df = limits_test(df)
    
    # df = IC_test(df)
    
    df = temporal_test(df)
    
    df = climo_test(df)


   
if __name__ == "__main__":
    limits_test()
    # IC_test()
    # temporal_test()
    # climo_test()






