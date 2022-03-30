# -*- coding: utf-8 -*-
"""
Created on Fri Jul 30 14:26:57 2021

@author: ktt5121
"""

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

#File vars
rep_year = "2021"
rep_month = "11"
rep_day = "05"
rep_hour = "10"
rep_data_range = [2007,2037]
rep_total_location = 4
rep_prmc_size = 20
rep_date = rep_year + "_" + rep_month + "_" + rep_day + "_" + rep_hour 
rep_strategies = [
            # "None",
            "SFT",
            # "5YearCycling",
            # "AdaptiveCycling",
            # "MFT"
            ]
rep_base_name = "Daily_Data_PRMC"
rep_ext = ".txt"
rep_prefix = "../output/"
rep_files = []

#Data vars
rep_data_raw = []
rep_data_observe = []
rep_data_mean_observe = []
rep_locations = [
                  [0,1,2,3]
                ]
rep_headers = []
      
def plot_one_header_CI(header, data, col_index, row_index, confident_interval):
    # print("row_index: " + str(row_index))
    # print("col_index: " + str(col_index))
    axis = axes[row_index,col_index] if col_index > 1 else axes[row_index]
    if "ByLocation" in header:
        for location_index in rep_locations[0]: 
            sns.lineplot(data = data, 
                        x = rep_x_observe,
                        y = header+str(location_index),
                        ax = axis,
                        ci = confident_interval) 
    else:
        sns.lineplot(data = data, 
                    x = rep_x_observe,
                    y = header,
                    ax = axes[row_index,col_index],
                    ci = confident_interval)
        
def plot_one_header(header, data, col_index, row_index, confident_interval):
    plot_one_header_CI(header, data, col_index, row_index, confident_interval)
    # plot_one_header_2M(header, tag_index, header_index,confident_interval)
    axis = axes[row_index,col_index] if col_index > 1 else axes[row_index]
    axis.set_title(header,fontsize=8)
    axis.set_ylabel(None)
    
def plot_headers(header, data, col_index, row_index, confident_interval):
    plot_one_header(header, data, col_index, row_index, confident_interval)
            
        
def short_header(header):
    new_header = header
    words = {
                "ByLocation":"",
                "Current":"Cr.",  
                "Probability":"P.",  
                "Total":"T.",  
                "Monthly":"M.", 
                "Malaria":"Ma.",  
                "Parasite":"Par.",    
                "BloodSlidePrevalence":"Pre.",  
                "Prevalence":"Pre.", 
                "Treatment":"Treat.",
                "Population":"Pop.",  
                "Cumulative":"Cu.",  
                "Resistance":"Res.",  
                "Mutation":"Mut.", 
                "NumberOf":"No.",  
                "Frequency":"Freq.",  
                "Clinical":"Cli.", 
                "Positive":"Pos.",
            }    
    for key in words:
        if key in header:
            new_header = new_header.replace(key,words[key])
    return new_header

#Plot
rep_location_colors = [ "cyan", "orange", "green", "purple", "yellow", "red" ]
                        
for strategy in rep_strategies:
    rep_files = rep_prefix + rep_date + "_" + rep_base_name + "_" + strategy + rep_ext

rep_data_raw = pd.read_csv(rep_files)
    
rep_data_observe = rep_data_raw[(rep_data_raw.Calendar >= rep_data_range[0]) & (rep_data_raw.Calendar <= rep_data_range[1])]
rep_headers = rep_data_raw.columns  
                  
rep_data_mean_observe = rep_data_observe
    
rep_data_mean_observe["Year"] = rep_data_mean_observe.Calendar - rep_data_range[0]
        
rep_header_observe = rep_headers

fig, axes = plt.subplots(nrows=rep_rows_observe, 
                         ncols=rep_cols_observe,
                         sharex="col", sharey=False, 
                         figsize = (300,100))