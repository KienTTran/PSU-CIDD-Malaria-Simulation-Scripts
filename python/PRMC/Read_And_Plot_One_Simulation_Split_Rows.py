# -*- coding: utf-8 -*-
"""
Created on Tue Jan  4 22:35:31 2022

@author: kient
"""

from Read_Simulations import read_simulations
import pandas as pd
import seaborn as sns
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.cbook as cbook
import operator
import math

plot_keywords = [
            "Daily_Data",
            # "_1M_800_",
            # "_0.99_0.3_",
            # "_0.99_0.6_",
            # "_2007_",
            # "_2017_",
            # "_2027_",
            # "_2037_",
            ]
start_year = 2007
# end_year = 2017
end_year = 2027
# end_year = 2047
# display = "Year"
display = "Month"
# display = "Day"
year_interval = 1
month_interval = 12
day_interval = 90
genotypes = 4

# local_path = "D:/plot/Simulations/"
# local_path = "D:/plot/parasite_id/10K/"
# local_path = "D:/plot/parasite_id/100K/"
# local_path = "D:/plot/parasite_id/new/"
# local_path = "D:/plot/all/parasite_id/"
# local_path = "D:/plot/all/Nguyen/"
# local_path = "D:/plot/4000/"
# local_path = "D:/plot/new/"
# local_path = "D:/plot/new/250K_500K_1M/"
# local_path = "D:/plot/new/1M/"
# local_path = "D:/plot/new/1M/Parasite"
# local_path = "D:/plot/new/1M/PRMC"
# local_path = "D:/plot/new/Test/Normal"
# local_path = "D:/plot/new/Test/PRMC"
local_path = "D:/plot/new/1M/Test2/"
# local_path = "D:/plot/new/1M/4-Genotypes/PRMC"
# local_path = "D:/plot/new/1M/4-Genotypes/Parasite"
# local_path = "D:/plot/new/1M/4-Genotypes/Parasite"
plot_delay = 2

#Plot vars
plot_lines = []
plot_labels = []
ops = { 
        "+": operator.add, 
        "-": operator.sub,
        "x": operator.mul,
        "/": operator.truediv
        }

def plot_headers(title, data_mean, data_min, data_max, \
                    rep_cols_observe, col_index, row_index, \
                    rep_header_observe, rep_x_observe, axes, \
                    index, confident_interval):
    if index == 0:
        for header in rep_header_observe:
            sns.lineplot(data = data_mean, 
                        x = rep_x_observe,
                        y = header,
                        ax = axes[index],
                        ci = confident_interval,
                        linewidth = 1.0,
                        # linestyle="dashed"
                        # err_style='bars'
                        )
        axes[index].set_title("Allele Frequency",fontsize=12)
        # axes[index].axhline(y=0.5, color='grey', linestyle='--', linewidth = 2.0, alpha = 0.4)
        axes[index].legend(loc='lower right', labels=[headers[2:] for headers in rep_header_observe], ncol = 2)
    elif index == 1:
        for header in rep_header_observe:
            sns.lineplot(data = data_mean, 
                        x = rep_x_observe,
                        y = header,
                        ax = axes[index],
                        ci = confident_interval,
                        linewidth = 1.0,
                        # err_style='bars'
                        )
        axes[index].set_title("Genotype Frequency",fontsize=12)
        # axes[index].axhline(y=0.25, color='grey', linestyle='--', linewidth = 2.0, alpha = 0.4)
        axes[index].legend(loc='lower right', labels=[headers[2:] for headers in rep_header_observe], ncol = 2)
    else:
        for header in rep_header_observe:
            sns.lineplot(data = data_mean, 
                        x = rep_x_observe,
                        y = header,
                        ax = axes[index],
                        ci = confident_interval,
                        linewidth = 1.0,
                        # err_style='bars'
                        )
        axes[index].set_title("Linkage Disequilibrium",fontsize=12)
        axes[index].tick_params(which="both", bottom=True)
        axes[index].legend(loc='center', labels=[headers[2:] for headers in rep_header_observe], ncol = 2)
        axes[index].set_xlabel(None)
    axes[index].set_ylabel(None) 
    
print("Reading simulations")   
simulations = read_simulations(local_path, plot_keywords, plot_delay)
if simulations == []:
    print("No simulation available")
else:
    print("Ploting simulations")
    
for rep_file in simulations:
    rep_tag = ""  
    rep_tags = []
    print(rep_file)
    for split_items_1 in rep_file.split("/"):
        if "\\" in split_items_1:
            rep_tags = split_items_1.split("\\")
            print(rep_tags)
            if len(rep_tags) > 3:
                rep_tag = rep_tags[-3]
            else:
                rep_tag = rep_tags[-1]
        else:
            rep_tags = rep_file.split("/")
            rep_tag = rep_tags[-1]
    
    rep_tag_data = rep_tag.split("_")
    print(rep_tag_data)

    rep_data_raw = []
    rep_data_observe = []
    rep_data_mean_observe = []
    rep_locations = [
                      [0,1,2,3]
                    ]
    rep_headers = []  
    rep_header_legend = []
    rep_data_range = [start_year, end_year]
    rep_total_location = 1  
    rep_data_csv = 0
    
    #Plot
    rep_location_colors = [ "cyan", "orange", "green", "purple", "yellow", "red" ]
                   
    try:
        rep_data_csv = pd.read_csv(rep_file)
    except pd.errors.EmptyDataError:
        print('Empty csv file!')
        continue
         
    rep_data_raw.append(rep_data_csv)
        
    for data in rep_data_raw:
        rep_data_observe.append(data)
    
    total_genotypes = pow(genotypes,2)
    index_pop_gen_start = pow(genotypes,2) + 4
    index_pop_gen_end = index_pop_gen_start + pow(genotypes,2)
    
    #Change data to frequency
    for data in rep_data_observe:        
        data["First"] = data['Day'].apply(lambda x: data.Day[0:1])
        data_month = (data.Day - data.First) / 30
        data_year = (data.Day - data.First) / 365
        data_month = data_month.round(0)
        data_year = data_year.round(0)
        #Delete columns that will not be plotted
        del data['First']
        if 'Calendar' in data.columns:
            del data['Calendar']
        if '0:Prevalence' in data.columns:
            del data['0:Prevalence']
        if '0:IFRate' in data.columns:
            del data['0:IFRate']
        
        data.insert(1,"Month",data_month)
        data.insert(2,"Year",data_year)
        
        #Calculate sum of genotypes
        sum = data.iloc[:, index_pop_gen_start:index_pop_gen_end].sum(axis=1)
        
        #Calculate allele frequency
        # 2-genotypes
        # data["0:Allele K"] = (data["0:KYY--C1x"] + data["0:KYY--Y1x"])/sum
        # data["0:Allele C"] = (data["0:KYY--C1x"] + data["0:TYY--C1x"])/sum
        # data["0:Allele T"] = (data["0:TYY--C1x"] + data["0:TYY--Y1x"])/sum
        # data["0:Allele Y"] = (data["0:KYY--Y1x"] + data["0:TYY--Y1x"])/sum
        # 4-genotypes
        data["0:Allele K"] = (  data["0:KNF--C1x.1"] + data["0:KNF--C1X.1"]
                              + data["0:KNF--C2x.1"] + data["0:KNF--C2X.1"]
                              + data["0:KNY--C1x.1"] + data["0:KNY--C1X.1"]
                              + data["0:KNY--C2x.1"] + data["0:KNY--C2X.1"]
                              )/(sum)
        data["0:Allele T"] = (  data["0:TNF--C1x.1"] + data["0:TNF--C1X.1"]
                              + data["0:TNF--C2x.1"] + data["0:TNF--C2X.1"]
                              + data["0:TNY--C1x.1"] + data["0:TNY--C1X.1"]
                              + data["0:TNY--C2x.1"] + data["0:TNY--C2X.1"]
                              )/(sum)
        data["0:Allele F"] = (  data["0:KNF--C1x.1"] + data["0:KNF--C1X.1"]
                              + data["0:KNF--C2x.1"] + data["0:KNF--C2X.1"]
                              + data["0:TNF--C1x.1"] + data["0:TNF--C1X.1"]
                              + data["0:TNF--C2x.1"] + data["0:TNF--C2X.1"]
                              )/(sum)
        data["0:Allele Y"] = (  data["0:KNY--C1x.1"] + data["0:KNY--C1X.1"]
                              + data["0:KNY--C2x.1"] + data["0:KNY--C2X.1"]
                              + data["0:TNY--C1x.1"] + data["0:TNY--C1X.1"]
                              + data["0:TNY--C2x.1"] + data["0:TNY--C2X.1"]
                              )/(sum)
        data["0:Allele 1"] = (  data["0:KNF--C1x.1"] + data["0:KNF--C1X.1"]
                              + data["0:KNY--C1x.1"] + data["0:KNY--C1X.1"]
                              + data["0:TNF--C1x.1"] + data["0:TNF--C1X.1"]
                              + data["0:TNY--C1x.1"] + data["0:TNY--C1X.1"]
                              )/(sum)
        data["0:Allele 2"] = (  data["0:KNF--C2x.1"] + data["0:KNF--C2X.1"]
                              + data["0:KNY--C2x.1"] + data["0:KNY--C2X.1"]
                              + data["0:TNF--C2x.1"] + data["0:TNF--C2X.1"]
                              + data["0:TNY--C2x.1"] + data["0:TNY--C2X.1"]
                              )/(sum)        
        data["0:Allele x"] = (  data["0:KNF--C1x.1"] + data["0:KNF--C2x.1"]
                              + data["0:KNY--C1x.1"] + data["0:KNY--C2x.1"]
                              + data["0:TNF--C1x.1"] + data["0:TNF--C2x.1"]
                              + data["0:TNY--C1x.1"] + data["0:TNY--C2x.1"]
                              )/(sum)
        data["0:Allele X"] = (  data["0:KNF--C1X.1"] + data["0:KNF--C2X.1"]
                              + data["0:KNY--C1X.1"] + data["0:KNY--C2X.1"]
                              + data["0:TNF--C1X.1"] + data["0:TNF--C2X.1"]
                              + data["0:TNY--C1X.1"] + data["0:TNY--C2X.1"]
                              )/(sum)
        
        #Calculate genotype frequency
        data.iloc[:, index_pop_gen_start:index_pop_gen_end] = data.iloc[:, index_pop_gen_start:index_pop_gen_end].div(sum, axis='index')                    
                
        # Calculate LD
        # 2-genotypes
        # data["0:[KC] - [K][C]"] = data["0:KYY--C1x"] - (data["0:Allele K"]*data["0:Allele C"])
        # data["0:[TY] - [T][Y]"] = data["0:TYY--Y1x"] - (data["0:Allele T"]*data["0:Allele Y"]) 
        # 4-genotypes   
        data["0:[KY1x] - ([K][Y][1][x])"] = data["0:KNY--C1x.1"] - (data["0:Allele K"] * data["0:Allele Y"] 
                                                                    * data["0:Allele 1"] * data["0:Allele x"])
        data["0:[TY1x] - ([T][Y][1][x])"] = data["0:TNY--C1x.1"] - (data["0:Allele T"] * data["0:Allele Y"] 
                                                                    * data["0:Allele 1"] * data["0:Allele x"])
        data["0:[KF2X] - ([K][F][2][X])"] = data["0:KNF--C2X.1"] - (data["0:Allele K"] * data["0:Allele F"] 
                                                                    * data["0:Allele 2"] * data["0:Allele X"])
        data["0:[TF2X] - ([T][F][2][X])"] = data["0:TNF--C2X.1"] - (data["0:Allele T"] * data["0:Allele F"] 
                                                                    * data["0:Allele 2"] * data["0:Allele X"])
                              
    # rep_data_mean_observe = rep_data_observe[0]    
    
    rep_headers = rep_data_observe[0].columns
    print(rep_headers)
    
    rep_data_concat = [rep_data for rep_data in rep_data_observe]             
    rep_data_mean_observe = pd.concat(rep_data_concat).mean(level=0)            
    rep_data_min_observe = pd.concat(rep_data_concat).min(level=0)          
    rep_data_max_observe = pd.concat(rep_data_concat).max(level=0)         
    rep_data_quantile_observe = pd.concat(rep_data_concat).quantile(axis=0)
    
    x_tick_major = []
    x_tick_major_label = []
    y_tick_major = [x * 0.1 for x in range(0, 7)]
        
    for month in range(0,int(rep_data_mean_observe.Month.tail(1))):
        if month % 24 == 0:
            x_tick_major.append(month)
            x_tick_major_label.append(start_year + int(month/12))
        
    
    #None/sd
    confident_interval = None
    rep_header_observe = []
    rep_header_observe.append(rep_headers[index_pop_gen_end:(index_pop_gen_end + genotypes*2)]) #index 0 - Allele frequency
    rep_header_observe.append(rep_headers[index_pop_gen_start:index_pop_gen_end]) #index 1 - Genotype frequency
    rep_header_observe.append(rep_headers[(index_pop_gen_end + genotypes*2):(index_pop_gen_end + genotypes*2 + 5)]) #index 2 - LD
    
    rep_header_legend = []
    
    for index in range(0,int((len(rep_header_observe))/rep_total_location)):
        rep_header_legend.append(rep_header_observe[index][2:])
    
    rep_rows_observe = 3
    rep_cols_observe = 1
    
    fig, axes = plt.subplots(nrows=rep_rows_observe, 
                              ncols=rep_cols_observe,
                              sharex="col", sharey=False, 
                              figsize = (300,100),
                              gridspec_kw={'height_ratios': [1,3,1]})
    fig.subplots_adjust(top = 0.94, bottom = 0.06, right = 0.95, left = 0.05, 
                        hspace=0.2, wspace = 0.2)
    sns.set_style("darkgrid")
           
    #Ploting
    for col_index in range(0,rep_cols_observe):
        for row_index in range(0,rep_rows_observe):
            index = col_index + row_index * rep_cols_observe
            plot_headers(rep_tag, rep_data_mean_observe, rep_data_min_observe, rep_data_max_observe, \
                         rep_cols_observe, col_index, row_index, \
                         rep_header_observe[index], display, axes, \
                         index, confident_interval)
                
    plt.minorticks_on()
    plt.xticks(x_tick_major,x_tick_major_label)
    # plt.yticks(y_tick_major)
    plt.pause(plot_delay)
