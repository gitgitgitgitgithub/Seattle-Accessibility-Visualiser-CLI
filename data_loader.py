# -*- coding: utf-8 -*-
"""
Created on Sun Apr 12 11:26:40 2026

@author: coleb
"""


import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import os

#to avoid warnings in output
import warnings
warnings.filterwarnings("ignore")

def load_all_data():
    #import data, neighborhoods
    if os.path.exists("data/neighborhoods.gpkg"):
        neighborhoods = gpd.read_file("data/neighborhoods.gpkg")
    else:
        neighborhoods = gpd.read_file("data/neighborhoods.geojson")
        neighborhoods.to_file("data/neighborhoods.gpkg", driver="GPKG")#save for faster reloading
    
    #consolidated data for large neighborhoods
    large_view=neighborhoods.dissolve(by='L_HOOD').reset_index()
    
    #list of large and small neighborhoods for reference
    LHOODS,SHOODS=set(neighborhoods['L_HOOD']),set(neighborhoods['S_HOOD'])#to search later
    
    #stops
    if os.path.exists("data/stops.gpkg"):
        stops = gpd.read_file("data/stops.gpkg")
    else:
        transit_stops = pd.read_csv("data/stops.txt")
        #convert stops to geodata
        transit_stops=transit_stops[["stop_name", "stop_lat", "stop_lon"]]
        points = [Point(pair) for pair in zip(transit_stops.stop_lon,transit_stops.stop_lat)]
        stops = gpd.GeoDataFrame(transit_stops, geometry=points, crs="epsg:4326")#code for lat/lon data
        stops.to_file("data/stops.gpkg", driver="GPKG")
    
    #stairs
    if os.path.exists("data/stairs.gpkg"):
        stairs = gpd.read_file("data/stairs.gpkg")
    else:
        stairs = gpd.read_file("data/stairs.geojson")
        stairs.to_file("data/stairs.gpkg", driver="GPKG")
        
    return neighborhoods,large_view, LHOODS, SHOODS, stops, stairs

