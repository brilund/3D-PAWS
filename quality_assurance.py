#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Dec 10 15:20:44 2020

@author: blund
"""



#the naming convention for the columns added to the data frame are as
#    follows...
#First letter (lowercase) represents the variable being tesed. It is
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



##############################################################################
##############################   LIMITS TEST   ###############################
##############################################################################

def limits_test(sensor, mintime, maxtime, df):

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
    si_max = 13000.    # W m^-2
    
    #tipping bucket specs
    tb_min = 0.       # mm
    tb_max = 500.     # mm
    
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
        t_idx = df.index[(df.temp_C <= bmp_t_min) & (df.temp_C >= bmp_t_max)]
        p_idx = df.index[(df.station_P <= bmp_p_min) & (df.station_P >= bmp_p_max)]
        a_idx = df.index[(df.alt <= bmp_a_min) & (df.alt >= bmp_a_max)]
        
        #for the indices in the dataframe of values that are outside the
        #    specifications, change the values at the same indices in the zero
        #    arrays to ones (these indicate the values out of range)
        t_LC[t_idx] = 1
        p_LC[p_idx] = 1
        a_LC[a_idx] = 1
        
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
        t_idx = df.index[(df.temp_C <= htu_t_min) & (df.temp_C >= htu_t_max)]
        rh_idx = df.index[(df.rel_hum <= htu_rh_min) & (df.rel_hum >= htu_rh_max)]
        
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
        t_idx = df.index[(df.temp_C <= mcp_t_min) & (df.temp_C >= mcp_t_max)]
        
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
        si_idx = df.index[(df.temp_C < si_min) & (df.temp_C > si_max)]
        
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
        ws_idx = df.index[(df.wind_speed < ws_min) & (df.wind_speed > ws_max)]
        
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
        wd_idx = df.index[(df.wind_dir < wd_min) & (df.wind_dir > wd_max)]
        
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
        tb_idx = df.index[(df.rain < tb_min) & (df.rain > tb_max)]
        
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
    
    

# ##############################################################################
# #######################   INTERNAL CONSISTENCY TEST   ########################
# ##############################################################################

# #here is where the physical limitiations of each variable will be pitted
# #    against all other variables (where applicable) to determine validity,
# #    for example, dewpoint cannot exceed temperature

# def IC_test(sensor, mintime, maxtime, df):
#
#     #set wind direction to zero if wind SPEED is below some threshold
#
#     #here is where you can set limitations (and subsequent flags on those
#     #    that exceed the limitations) for the SI1145 readings based on the
#     #    known amounts of incoming solar radiation from both total and 
#     #    specific spectral range contributions

#     #if liquid precip is reported, temperature should be at least ???
#     #how do we determine liquid precipiation with the data we have???



##############################################################################
#######################   TEMPORAL CONSISTENCY TEST   ########################
##############################################################################

#here is where we will flag any data blips (sharp, non-physical rises or
#    decreases) or runs (extended periods of non-/low-variability) in data

def temporal_test(sensor, mintime, maxtime, df):

    #beware of erroneously flagged calm winds (speed and direction); you may
    #    have to set a threshold of wind speed such that there is a higher
    #    tolerance for excessively low variability IF wind speeds are below
    #    some statistically significant, predetermined threshold

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
    
    #must also test for runs in data; start by flagging values i such that the 
    #    next adjacent value i+1 is equivalent to i. For every i+n value
    #    thereafter that does not change, these values will be flagged. The
    #    very first occurrence of the run will NOT be flagged



# ##############################################################################
# #######################   CLIMATOLOGICAL LIMITS TEST   #######################
# ##############################################################################

# def climo_test(sensor, mintime, maxtime, df):
#
#     #here might be the appropriate place to place an upper limit on the
#     #    radiation sensor's readings
    # #t_min = -80.  # this minimum is not used because the WMO Guide's
    #                # minimum is well below the lower limit of this
    #                # sensor
    # t_max = 60.   # deg C
    # p_min = 500.  # hPa
    # p_max = 1080. # hPa
    # a_min = 0.    # meters
    # a_max = 8850. # meters (based on the elevation of the summit of Mt. Everest)
    # #rh_min = 0.   # these limits are within or equivalent to those set by
    #               # sensor specification, hence, not necessary
    # #rh_max = 100. # " "
    
    # si_min = 0.       # W m^-2
    # si_max = 13000.    # W m^-2
    
    # precip_min = 0.       # mm
    # precip_max = 500.     # mm
    
    # #anemometer specs
    # ws_min = 0.       # m/s
    # ws_max = 75.      # m/s
    
    # #wind vane specs
    # wd_min = 0.       # deg
    # wd_max = 360.     # deg


   
if __name__ == "__main__":
    limits_test()
    # IC_test()
    # temporal_test()






