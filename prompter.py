# -*- coding: utf-8 -*-
"""
Created on Wed Apr 15 14:02:51 2026

@author: coleb
"""
from analysis import heatmap, produce_grid, point_density, point_counts, graph_points, sort_and_print, crop_neighborhood
from data_loader import load_all_data

reminder_dict="""
Commands:
  heatmap [stairs|stops] d=[separation] [neighborhood]
  map [stairs|stops] [neighborhood]
  rank [districts/neighborhoods] by [stair|stop] [total|density] 
  end (ends the session)
  help (displays this text box)
  
Note: Omit neighborhood/district name to map the entire city. Capitalize neighborhood/district names, nothing else.

Examples:
  heatmap stairs d=100
  rank districts by stop density
  map stairs Capitol Hill
  
  
"""

#values used in parsing function
data = load_all_data()


def request_parser(prompt,data):  
    
    #establish data
    neighborhoods,large_view, LHOODS, SHOODS, stops, stairs = data
    
    point_dict ={"stairs": stairs,
             "stair":stairs,
               "stops": stops,
               "stop":stops}
    ranked_dict={"total":"count",
                 "density":"density/km2"}
    nbr_dict={"districts":"L_HOOD",
                 "neighborhoods":"S_HOOD"}
    
    #set up base values
    nbrhood, pts, funct, sep, ranked, nbr_type =None,None,None,None,None,None
    myprompt = prompt.strip().split()  
    skip=None #skip parse word if nec
    
    
    #assign values from prompt strings
    for i in range(len(myprompt)):
        if skip==i:
            continue
        if not nbrhood:#check word for neighborhood  
            if myprompt[i]=="all" or myprompt[i] in LHOODS or myprompt[i] in SHOODS:
                nbrhood=myprompt[i]
                continue
            elif i+1<len(myprompt) and myprompt[i]+" "+myprompt[i+1] in LHOODS:
                nbrhood = myprompt[i]+" "+myprompt[i+1]
                skip=i+1
                continue
            elif i+1<len(myprompt) and myprompt[i]+" "+myprompt[i+1] in SHOODS:
                nbrhood = myprompt[i]+" "+myprompt[i+1]
                skip=i+1
                continue
        if not pts:
            if myprompt[i] in list(point_dict):
                pts=myprompt[i]
                continue
        if not funct:
            if myprompt[i] in ['heatmap','map','rank']:
                funct=myprompt[i]
                continue
        if not sep:
            if len(myprompt[i].split('='))==2:
                sep = myprompt[i].split('=')[1]
                continue
        if not ranked:
            if myprompt[i] in list(ranked_dict):
                ranked = myprompt[i]
        if not nbr_type:
            if myprompt[i] in list(nbr_dict):
                nbr_type = myprompt[i]
    if not nbrhood:
        nbrhood ='all'
    if not nbr_type:
        nbr_type='districts'
    #print(nbrhood, pts, funct, sep, ranked, nbr_type)
    
    #perform tasks on values as necessary
    try:
        points = point_dict[pts]
    except KeyError:
        print("Invalid dataset! Point type (stairs/bus stops) not specified!")
        print(reminder_dict)
        return 0
    if nbrhood != "all": #user can crop city to whatever neighborhood they like
        neighborhood, points = crop_neighborhood(points,neighborhoods,nbrhood,LHOODS,SHOODS)
        
            
    else:
        if funct != "rank": #ranking is by default all neighborhoods
            print("No neighborhood identified. Including all neighborhoods.\n To specify a neighborhood, be sure to spell and capitalize it correctly.")
        neighborhood = neighborhoods
    if funct == "heatmap":
        try:
            separation = int(sep)
        except (TypeError, ValueError) as e:
            separation = 100
            print("Invalid Separation: Setting to default 100m. \nTo specify separation of n meters, include keyword '=n'")
        request = heatmap(produce_grid(neighborhood,separation),points)
    elif funct == "map":
        request = graph_points(neighborhood, points)
    elif funct == "rank":
        if nbr_type!='small':
            neighborhood = large_view
        if ranked == "total":
            request = sort_and_print(point_counts(neighborhood,points,nbr_dict[nbr_type]),nbr_dict[nbr_type],ranked_dict[ranked])
        elif ranked == "density":
            request = sort_and_print(point_density(neighborhood,points,nbr_dict[nbr_type]),nbr_dict[nbr_type],ranked_dict[ranked])
    try:
        return request
    except NameError:
        print("Invalid Request!")
        print(reminder_dict)
        return 0