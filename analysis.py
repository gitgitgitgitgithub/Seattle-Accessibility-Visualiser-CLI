# -*- coding: utf-8 -*-
"""
Created on Wed Apr 15 13:37:39 2026

@author: coleb
"""


import pandas as pd
import geopandas as gpd
import numpy as np
import matplotlib.pyplot as plt
from shapely.geometry import Point
import re
import os

#to avoid warnings in output
import warnings
warnings.filterwarnings("ignore")

#to use to filter point data to specific neighborhood or hoods

def assign(points,neighborhoods):#assigns each point to its neighborhood
    new_points = gpd.clip(points,neighborhoods) #only include points in a neighborhood
    new_points = gpd.sjoin(new_points,neighborhoods[["L_HOOD","S_HOOD","geometry"]],predicate="within", how= "left")
    return new_points

def crop_neighborhood(points,neighborhoods,neighborhood,LHOODS,SHOODS): 
    if neighborhood in LHOODS:
        local = neighborhoods[neighborhoods["L_HOOD"]==neighborhood]
    elif neighborhood in SHOODS:
        local = neighborhoods[neighborhoods["S_HOOD"]==neighborhood]
    local_spots = assign(points.drop(columns=["index_left", "index_right"], errors = "ignore"),local.drop(columns=["index_left", "index_right"], errors="ignore"))
    return local, local_spots

#package data for output

def sort_and_print(df,nbr_type,metric): #called with 'rank' keyword
    new_df=df.sort_values(by= metric, ascending = False)
    print(new_df[[nbr_type,metric]].to_string(index=False))

def point_counts(neighborhood_df,point_df,marker):#works for any set of points
    point_df_assigned = assign(point_df,neighborhood_df)
    counts = point_df_assigned.groupby(marker).size()  
    new_df = neighborhood_df.merge(counts.rename("count"),left_on=marker, right_index=True, how="left") 
    new_df["count"]=new_df["count"].fillna(0)
    return new_df

def point_density(neighborhood_df,points,marker):
    new_df = neighborhood_df.to_crs('epsg:2285')#convert to plane coords
    point_df = points.to_crs('epsg:2285')
    new_df = point_counts(new_df,point_df,marker)#adds stop_counts columns as before
    new_df["area"] = new_df["geometry"].area*0.092903/1e6 #convert to sq km rather than sq ft
    new_df["density/km2"]=new_df["count"]/new_df["area"]
    return new_df

#simple graph of points function
def graph_points(neighborhood, points):
    minx,miny,maxx,maxy=neighborhood.total_bounds
    marg_x=0.1*(maxx-minx)
    marg_y=0.1*(maxy-miny)
    fig, ax = plt.subplots(figsize=(10, 10))
    plt.xlim(minx-marg_x,maxx+marg_x)
    plt.ylim(miny-marg_y,maxy+marg_y)
    neighborhood.plot(ax=ax, color="lightgray", edgecolor="black")
    points.plot(ax=ax, color="blue", markersize=5)
    plt.show()

#the following is about making a heat map of nearest point to xy
def produce_grid(neighborhoods, separation):
    adj_hoods=neighborhoods.to_crs('epsg:3857')
    minx,miny,maxx,maxy=adj_hoods.total_bounds
    x_points=np.arange(minx,maxx,separation)
    y_points=np.arange(miny,maxy,separation)
    pairs = [(x,y) for x in x_points for y in y_points]
    grid = [Point(pair) for pair in pairs]
    grid = gpd.GeoDataFrame({"geometry":grid}, geometry="geometry", crs="epsg:3857")
    grid = assign(grid,adj_hoods) #assign is masking function 
    return grid

    
def heatmap(grid_points,points):
    adj_points =  points.to_crs('epsg:3857').drop(columns=["index_left", "index_right"], errors="ignore")
    grid = grid_points.to_crs('epsg:3857').drop(columns=["index_left", "index_right"], errors="ignore")
    nearest = gpd.sjoin_nearest(grid,adj_points,how="left",distance_col="distance")
    nearest = nearest.to_crs('epsg:4326')
    minx,miny,maxx,maxy=nearest.total_bounds
    marg_x=0.1*(maxx-minx)
    marg_y=0.1*(maxy-miny)
    fig, ax = plt.subplots(figsize=(10, 10))
    plt.xlim(minx-marg_x,maxx+marg_x)
    plt.ylim(miny-marg_y,maxy+marg_y)
    nearest.plot(column="distance", ax=ax,markersize=5,cmap='viridis_r' )
    plt.show()
