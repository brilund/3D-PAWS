#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Dec 10 15:20:44 2020

@author: blund
"""

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
    si_max = 1000.    # W m^-2
    
    #tipping bucket specs
    tb_min = 0.       # mm
    tb_max = 100.     # mm
    
    #anemometer specs
    ws_min = 0.       # m/s
    ws_max = 50.      # m/s
    
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
    
    #
    
    
    ############################### Anemometer ###############################
    
    if sensor.lower() == "anemometer":
    
    #
    
    
    ############################### Wind Vane ################################
    
    if sensor.lower() == "wind_vane":
    
    #
    
    
    ############################ Tipping Bucket ##############################
    
    if sensor.lower() == "rain":
    
    #
    
    
    ##########################################################################
    
    print("------------------------------------------------------------------")
    
    #
    # return df
    
    

##############################################################################
#######################   INTERNAL CONSISTENCY TEST   ########################
##############################################################################

def IC_test(sensor, mintime, maxtime, df):



##############################################################################
#######################   TEMPORAL CONSISTENCY TEST   ########################
##############################################################################

def temporal_test(sensor, mintime, maxtime, df):


   
if __name__ == "__main__":
    limits_test()






