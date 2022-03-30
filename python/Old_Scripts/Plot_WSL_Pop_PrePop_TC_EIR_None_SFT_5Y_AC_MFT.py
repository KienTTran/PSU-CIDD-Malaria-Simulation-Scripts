# -*- coding: utf-8 -*-
"""
Created on Fri Jul 30 14:26:57 2021

@author: ktt5121
"""

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np

#File vars
rep_year = "2021"
rep_month = "08"
rep_day = "28"
rep_hour = "01"
rep_date = rep_year + "_" + rep_month + "_" + rep_day + "_" + rep_hour 
rep_job_number = 1
rep_tags = [
            "None",
            "SFT_AS",
            "5YearCycling",
            "AdaptiveCycling",
            "MFT"
            ]
rep_locate = "Cluster"
rep_base_name = "Monthly_Data"
rep_ext = ".txt"
rep_prefix = "../analysis/"
rep_files = []

#Data vars
rep_data_raw = []
rep_data_observe = []
rep_data_range = [2020,2037]
rep_total_location = 4
rep_locations = [
                  [0,1,2],
                  [0,1,2],
                  [0,1,2],
                  [0,1,2],
                  [0,1,2],
                ]
rep_headers = []
rep_headers_observe = []

#Plot
rep_location_colors = [ "cyan", "orange", "green", "purple", "yellow", "red" ]
                        
for tag in rep_tags:
    for job in range(rep_job_number):
        rep_files.append(rep_prefix + rep_date + "_" + rep_locate + "_" + rep_base_name + "_" + tag + "_" + str(job) + rep_ext)

for file in rep_files:
    rep_data_raw.append(pd.read_csv(file))
    
for data in rep_data_raw:    
    rep_data_observe.append(data[(data.Calendar > rep_data_range[0]) & (data.Calendar < rep_data_range[1])])
    rep_headers = data.columns
   
#Figure vars
rep_header_length = int((len(rep_headers) - 2) / rep_total_location)
# fig = plt.figure(figsize=(40,80))
# fig.subplots_adjust(hspace=20.0)


#Filter report headers and make headers for ploting
for header in rep_headers[-rep_header_length:]:
    rep_headers_observe.append(header.replace(str(rep_total_location-1),""))

#Overide headers
rep_headers_observe = [ 
                        "Population",
                        "Positive",
                        "Prevalence",
                        # "MClinicalEpisole",
                        "MNewInfect",
                        # "MTreatment",
                        # "MTreatmentFailure",
                        # "MNonTreatment",
                        "TCLT5",
                        "TCMT5",
                        # "EIR"
                        ]
rep_x_observe = "Calendar"


fig, axes = plt.subplots(nrows=4, ncols=len(rep_tags),sharex=True, sharey=True, figsize = (200,80))
fig.subplots_adjust(hspace=0.5, wspace=0.3)

x_tick_observe = np.arange(min(rep_data_observe[0][rep_x_observe]), 
                             max(rep_data_observe[0][rep_x_observe])+1, 5.0)


#Ploting
for col,tag_index in zip(range(len(rep_tags)),range(len(rep_tags))):
    for row in range(0,4):
        index = (row)*(len(rep_tags))+(tag_index) + 1
        plt.subplot(4,len(rep_tags),index)
        if row == 0:                  
            for location_index in rep_locations[tag_index]:
                g = sns.lineplot(data = rep_data_observe[tag_index], 
                                    x = rep_x_observe,
                                    y = rep_data_observe[tag_index]["MClinicalEpisole"+str(location_index)],
                                    ci=None)
                g.set(xlabel=None)
                g.set(ylabel=None)
                plt.title(rep_tags[tag_index])
                plt.xticks(x_tick_observe)
                # plt.yticks(np.arange (25, 100, 25))
            if col == 0:
                plt.ylabel("MClinicalEpisole")
        if row == 1:                 
            for location_index in rep_locations[tag_index]:
                g = sns.lineplot(data = rep_data_observe[tag_index], 
                                    x = rep_x_observe,
                                    y = rep_data_observe[tag_index]["TCLT5"+str(location_index)],
                                    dashes=True,
                                    ci=None)
                g = sns.scatterplot(data = rep_data_observe[tag_index], 
                                    x = rep_x_observe,
                                    y = rep_data_observe[tag_index]["TCMT5"+str(location_index)],
                                    marker="X", 
                                    color="red",
                                    ci=None)
                g.set(xlabel=None)
                g.set(ylabel=None)
                plt.yticks(np.arange (0, 1, 0.25))
                plt.xticks(x_tick_observe)
            if col == 0:
                plt.ylabel("TCLT5 TCMT5")
        if row == 2:                 
            for location_index in rep_locations[tag_index]:
                g = sns.lineplot(data = rep_data_observe[tag_index], 
                                    x = rep_x_observe,
                                    y = rep_data_observe[tag_index]["Population"+str(location_index)] \
                                        * rep_data_observe[tag_index]["Prevalence"+str(location_index)]/100.0,
                                    ci=None)
                g.set(xlabel=None)
                g.set(ylabel=None)
            if rep_locate == "Cluster":
                plt.yticks(np.arange (0, 50000, 10000))
            else:
                plt.yticks(np.arange (0, 1000, 100))
                plt.xticks(x_tick_observe)
            if col == 0:
                plt.ylabel("Prevalence Population")
        if row == 3:                 
            for location_index in rep_locations[tag_index]:
                g = sns.lineplot(data = rep_data_observe[tag_index], 
                                    x = rep_x_observe,
                                    y = rep_data_observe[tag_index]["EIR"+str(location_index)],
                                    ci=None)
                g.set(xlabel=None)
                g.set(ylabel=None)
                plt.yticks(np.arange (0, 100, 25))
                plt.xlabel(rep_x_observe)
                plt.xticks(x_tick_observe)
            if col == 0:
                plt.ylabel("EIR")

fig.legend(labels=[str(i) for i in rep_locations[0]], loc='lower center', ncol=5)
plt.show()
