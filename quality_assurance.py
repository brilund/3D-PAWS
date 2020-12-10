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
    si_max = 1000.
    si_min = 0.
    
    #tipping bucket specs
    
    #anemometer specs
    
    #wind vane specs

    if sensor.lower() == "bmp180" or sensor.lower() == "bmp280":