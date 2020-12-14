#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Dec 10 15:20:44 2020

@author: blund
"""

##############################################################################
#############################   LIMITS TEST   ################################
##############################################################################

def quality_assurance(sensor, mintime, maxtime, df):

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
        #create a new column filled with 0s and 1s; 0s where values are within
        #    spec, and 1s where values are out of spec
        df.index[df.temp_C <= bmp_t_min], df.index[df.temp_C >= bmp_t_max]
        
        #if either or both T and P our out of spec, then all the subsequent
        #    variables calculated from them are also out of spec and must be
        #    flagged at the very least, discarded if necessary
        #temp_F need only be flagged if temp_C is flagged
        #SLP_hPa and SLP_inHg must be flagged if ANY measure value is out of
        #    spec (temp_C, altitude, or pressure)
        #station_P must be flagged only if pressure is flagged
    
    
    ############################# HTU21D Sensor ##############################
    
    #temp_F must be flagged only if temp_C is flagged
    
    
    ############################# MCP9808 Sensor #############################
    
    #temp_F must be flagged only if temp_C is flagged
    
    
    ############################# SI1145 Sensor ##############################
    
    #
    
    
    ############################### Anemometer ###############################
    
    #
    
    
    ############################### Wind Vane ################################
    
    #
    
    
    ############################ Tipping Bucket ##############################
    
    #
    
    
    
    
    
    
    
    