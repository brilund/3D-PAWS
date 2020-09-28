#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun 25 13:31:37 2020

@author: blund
"""


#This code reads and plots the hurricane track output from WRF model data
#    sensor.
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
#    Cartopy
#    netCDF4
#
#
#History:
#    June 25, 2020 - First Write
#
#
#Planned Features:
#    1. Add the ability to compute the layer average virtual temperature for a
#       more precises conversion to MSLP using the hypsometric equation
#
#
#How to Use:
#    1. Change all variables in "USER OPTIONS" section to desired input
#           directory
#           filename
#           save_dir
#           lat_top
#           lat_bottom
#           lon_left
#           lon_right
#    2. Run with "python hurricane_track_plotter.py" in terminal, or open in
#       Spyder and run from there.
#
#
#Example header from files: N/A
#
#Example data from files: N/A
#    
#
#
#NOTES:



##############################################
############ IMPORTING MODULES ###############
##############################################

import matplotlib.pyplot as plt
import numpy as np
import cartopy as cp
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
import matplotlib.ticker as mticker
from netCDF4 import Dataset
import matplotlib.path as mpath



##############################################
############### USER OPTIONS #################
##############################################

#set the 'directory' variable to the absolute path where your data are stored;
#    don't forget the trailing forward slash!
directory = "/Users/blund/Documents/side_projects/hurricane_tracks/drive-download-20200625T195439Z-001/"

#specify the name of the file you want to read in; include the file extension
#    if one exists
filename = "wrfout_d01_2020-05-20_00_00_00"

#specify the FULL file path to the directory in which to save your figures;
#    don't forget to include the trailing forward slash!
save_dir = "/Users/blund/Documents/Python_Scripts/Figures/hurricane_track/"

#set the domain over which to plot. Use decimal degrees; positive values for
#    North/East and negative values for South/West (e.g. -45.5 for 45.5 deg S)...

#the northern most parallel for your plot
lat_top = 28.

#the southern most parallel for your plot
lat_bottom = 15.

#the western most meridian for your plot
lon_left = 82.

#the eastern most meridian for your plot
lon_right = 96.



##############################################
############## READ IN FILE(S) ###############
##############################################

#read in the data file; this is set for "read" mode only
file = Dataset(directory + filename, mode="r")

#collect necessary variables
lon = file.variables['XLONG'][:] #longitude (deg N; negative is South)
lat = file.variables['XLAT'][:] #latitude (deg E; negative is West)
time = file.variables['Times'][:] #time (UTC)
sfc_press = file.variables['PSFC'][:] #surface pressure (Pa)
temp = file.variables['T2'][:] #temperature
alt = file.variables['HGT'][:] #surface altitude (terrain height) in meters



##############################################
############## DATA PROCESSING ###############
##############################################

#convert the latitude and longitude 3D arrays into 2D spatial arrays (i.e.
#    eliminating the 'time' portion of the arrays)
lat = lat[0]
lon = lon[0]

#convert 'sfc_press' to hectopascals for easier processing
sfc_press /= 100.

#find the minimum surface pressure for each timestamp, and its associated
#    location...
#convert the domain's surface pressure to mean sea-level pressure using the
#    hypsometric equation

Rd = 287.058 #gas constant for dry air
g = 9.81 #acceleration of gravity
Tv = 290. #layer average virtual temperature assumption

#find the layer average temperature

#initialize a list that will contain tuples of indices denoting the location of
#    the minimum surface pressure for each timestamp
locations = []

#loop through each time step in the surface pressure array, convert each pressure
#    to MSLP, find the minimum surface pressure post-conversion, then collect
#    the indices denoting the locaiton of that minimum surface pressure
for i in range(len(sfc_press)):
    sfc_press[i] = sfc_press[i]*np.exp((g*alt[i])/(Rd*Tv))
    min_sfcp = np.min(sfc_press[i])
    locations.append(np.where(sfc_press[i] == min_sfcp))

#collect the lat and lon values denoting the location of the minimum sfc
#    pressure found above
lat_mark = [] #initialize the list to contain the latitude values
lon_mark = [] #initialize the list to contain the longitude values

#loop through the tuples of indices in 'locations' to collect the lat and lon
#    values referenced by those indices
for j in range(len(locations)):
    lat_mark.append(lat[int(locations[j][0])][int(locations[j][1])])
    lon_mark.append(lon[int(locations[j][0])][int(locations[j][1])])

#manually creating a hurricane symbol to be the plot marker
def get_hurricane():
    u = np.array([  [2.444,7.553],
                    [0.513,7.046],
                    [-1.243,5.433],
                    [-2.353,2.975],
                    [-2.578,0.092],
                    [-2.075,-1.795],
                    [-0.336,-2.870],
                    [2.609,-2.016]  ])
    u[:,0] -= 0.098
    codes = [1] + [2]*(len(u)-2) + [2] 
    u = np.append(u, -u[::-1], axis=0)
    codes += codes

    return mpath.Path(3*u, codes, closed=False)



##############################################
################# PLOTTING ###################
##############################################


############## Drawing the map ###############

#set the overall figure size
plt.figure(figsize=(10,10))

#create an instance of the map projection
ax = plt.axes(projection=cp.crs.PlateCarree())

#restrict the domain over which to plot based on the user-defined latitude and
#    longitude ranges
ax.set_extent([lon_left, lon_right, lat_bottom, lat_top], crs=cp.crs.PlateCarree())

#map the map pretty
#create a NaturalEarthFeature 'land' instance
land = cp.feature.NaturalEarthFeature(category="physical", name="land", scale='10m')

#create a NaturalEarthFeature 'ocean' instance
ocean = cp.feature.NaturalEarthFeature(category="physical", name="ocean", scale="10m")

#create a NaturalEarthFeature 'country borders' instance
borders = cp.feature.NaturalEarthFeature(category="cultural", name="admin_0_countries", scale="10m")

#create a NaturalEarthFeature 'states and provinces' instance
states = cp.feature.NaturalEarthFeature(category="cultural", name="admin_1_states_provinces", scale="10m")

#add all the features created above to the map
ax.add_feature(ocean, facecolor="lightsteelblue")
ax.add_feature(land, facecolor="wheat", edgecolor="dimgray")
ax.add_feature(states, facecolor="none", edgecolor="firebrick", linewidth=0.3)
ax.add_feature(borders, facecolor="none", edgecolor="dimgray")

#add gridlines; the following lines of code utilizing the Gridliner ('gl')
#    instance are necessary to plot x- and y-axis tick labels, titles, and gridlines
gl = ax.gridlines(crs=cp.crs.PlateCarree(), draw_labels=True,
                  linewidth=1., color='gray', linestyle='--')

#x-axis tick labels on top; default is True
gl.xlabels_top = False
#x-axis tick labels on the bottom; default is True
gl.xlabels_bottom = True
#y-axis tick labels on the right; default is True
gl.ylabels_right = True
#y-axis tick labels on the left; default is True
gl.ylabels_left = True

#set the locations of the x- and y-axis tick labels
gl.xlocator = mticker.FixedLocator(np.arange(lon_left,lon_right+1))
gl.ylocator = mticker.FixedLocator(np.arange(lat_bottom,lat_top+1))

#format the x- and y-axis tick labels; this makes them pretty with proper units
gl.xformatter = LONGITUDE_FORMATTER
gl.yformatter = LATITUDE_FORMATTER
gl.ylabel_style = {'size': 12}
gl.xlabel_style = {'size': 12}

#manual placement of x- and y-axis titles since Cartopy Gridliner is still rudiementary
#    and does not have a simple method for adding x- and y-axis titles; adjust
#    the very first two values to achieve the desired location of the title on
#    on the figure
#y-axis title
ax.text(-0.09, 0.5, 'Latitude', va='bottom', ha='center',
        rotation='vertical', rotation_mode='anchor',
        transform=ax.transAxes, fontsize=12)
#x-axis title
ax.text(0.5, -0.07, 'Longitude', va='bottom', ha='center',
        rotation='horizontal', rotation_mode='anchor',
        transform=ax.transAxes, fontsize=12)

#add a plot title and subtitle
#adjust the 'y' and 'x' values to achieve the desired location of suptitle
plt.suptitle("WRF Model Simulated Forecast Track for Cyclone Amphan",
             color='b', fontsize=17, y=0.92, x=0.51)
plt.title("(Based on 2020-05-20 00UTC Forecast)", fontsize=14)


############## Plot on the map ###############

#retrieve the hurricane symbol created above
hurricane = get_hurricane()

#plot the track with lines connecting each minimum pressure location
plt.plot(lon_mark[:13], lat_mark[:13], linewidth=2, color='navy')

#plot the minimum pressure locations only (no connecting line) using the
#    hurricane symbol
plt.scatter(lon_mark[:13],lat_mark[:13], marker=hurricane, s=700,
            edgecolors="crimson", facecolors='none', linewidth=2, zorder=2)

#annotate the points with date/time strings
n = ['2020-05-20 00Z','2020-05-20 03Z','2020-05-20 06Z','2020-05-20 09Z',
     '2020-05-20 12Z','2020-05-20 15Z','2020-05-20 18Z','2020-05-20 21Z',
     '2020-05-21 00Z','2020-05-21 03Z','2020-05-21 06Z','2020-05-21 09Z']
for i, txt in enumerate(n):
    ax.annotate(txt, (lon_mark[i], lat_mark[i]), style='italic', color='k',
                position = (lon_mark[i]+0.25,lat_mark[i]-0.1), fontweight='bold')

#switch the position of the last timestamp's annotation to the left side since
#    it's so close to the previous annotation
ax.annotate('2020-05-21 12Z', (lon_mark[13]-2.5, lat_mark[13]-0.1), style='italic',
            color='k', fontweight='bold')

#add a label for the body of water in the figure
ax.annotate('BAY OF BENGAL', (87.1, 17.1), color='slategray', style='italic',
            fontsize=20)



##############################################
################ SAVE FIGURE #################
##############################################

#save the figure; the name of the figure can be adjusted here
plt.savefig('%sWRF-simulated_amphan-track_valid_20200520-0000.png' % (save_dir), dpi=500, \
                bbox_inches='tight')

#show the figure that was generated
plt.show()


