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
rep_month = "08"
rep_day = "27"
rep_hour = "16"
rep_date = rep_year + "_" + rep_month + "_" + rep_day + "_" + rep_hour 
rep_job_number = 1
rep_tags = [
            "None",
            # "SFT_AS",
            # "5YearCycling",
            # "AdaptiveCycling",
            # "MFT"
            ]
rep_locate = "Cluster"
rep_base_name = "Monthly_Data"
rep_ext = ".txt"
rep_prefix = "../analysis/"
rep_files = []

#Data vars
rep_data_raw = []
rep_data_observe = []
rep_data_range = [2007,2037]
rep_total_location = 4
rep_locations = [
                  [0],
                  [0,1,2,3],
                  [0,1,2,3],
                  [0,1,2,3],
                  [0,1,2,3]
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
                        "Residence",
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


# fig, axes = plt.subplots(nrows=len(rep_headers_observe), ncols=len(rep_tags),sharex=True, sharey=True, figsize = (100,50))
# fig.subplots_adjust(hspace=0.5)

# #Ploting
# for col,tag_index in zip(range(len(rep_tags)),range(len(rep_tags))):
#     for row,header_index in zip(range(len(rep_headers_observe)),range(len(rep_headers_observe))):
#         index = (header_index)*(len(rep_tags))+(tag_index) + 1#         
#         plt.subplot(len(rep_headers_observe),len(rep_tags),index)
#         for location_index in rep_locations[tag_index]:
#             g = sns.lineplot(data = rep_data_observe[tag_index], x=rep_x_observe,y=rep_headers_observe[header_index]+str(location_index), color=rep_location_colors[location_index], ci=None)
#             g.set(xlabel=None)
#             g.set(ylabel=None)
#         if row == 0:
#             plt.title(rep_tags[tag_index])
#         if col == 0:
#             plt.ylabel(rep_headers_observe[header_index])
#         if row == (len(rep_headers_observe) - 1):
#             plt.xlabel(rep_x_observe)

# plt.show()

#Plot PR population
rep_headers_observe = [ 
                        "Population",
                        "Prevalence",
                        ]
rep_x_observe = "Calendar"

fig, axes = plt.subplots(nrows=len(rep_headers_observe), ncols=len(rep_tags),sharex=True, sharey=True, figsize = (100,50))
fig.subplots_adjust(hspace=0.5)

#Ploting
for tag_index in range(len(rep_tags)):        
    plt.subplot(411)
    for location_index in rep_locations[tag_index]:
        # prevalence_population = 
        g = sns.lineplot(data = rep_data_observe[tag_index], 
                            x = rep_x_observe,
                            y = rep_data_observe[tag_index]["Population"+str(location_index)],
                            ci=None)
        plt.title(rep_tags[tag_index])
        plt.ylabel("Population")
        
    plt.subplot(412)
    for location_index in rep_locations[tag_index]:
        # prevalence_population = 
        g = sns.lineplot(data = rep_data_observe[tag_index], 
                            x = rep_x_observe,
                            y = rep_data_observe[tag_index]["Positive"+str(location_index)],
                            ci=None)
        plt.ylabel("Positive")
        
    plt.subplot(413)
    for location_index in rep_locations[tag_index]:
        # prevalence_population = 
        g = sns.lineplot(data = rep_data_observe[tag_index], 
                            x = rep_x_observe,
                            y = rep_data_observe[tag_index]["Population"+str(location_index)] \
                                * rep_data_observe[tag_index]["Prevalence"+str(location_index)]/100.0,
                            ci=None)
        plt.title(rep_tags[tag_index])
        plt.ylabel("Prevalence Population")
        
    plt.subplot(414)
    for location_index in rep_locations[tag_index]:
        # prevalence_population = 
        g = sns.lineplot(data = rep_data_observe[tag_index], 
                            x = rep_x_observe,
                            y = rep_data_observe[tag_index]["TCLT5"+str(location_index)],
                            ci=None)
        plt.ylabel("TCTL5")
        plt.xlabel(rep_x_observe)
        
plt.show()

# #Plot PR-EIR
# rep_headers_observe = [ 
#                         "Prevalence",
#                         ]
# rep_x_observe = "EIR"

# fig, axes = plt.subplots(nrows=len(rep_headers_observe), ncols=len(rep_tags),sharex=True, sharey=True, figsize = (100,50))
# fig.subplots_adjust(hspace=0.5)

# #Ploting
# for col,tag_index in zip(range(len(rep_tags)),range(len(rep_tags))):
#     for row,header_index in zip(range(len(rep_headers_observe)),range(len(rep_headers_observe))):
#         index = (header_index)*(len(rep_tags))+(tag_index) + 1
#         plt.subplot(len(rep_headers_observe),len(rep_tags),index)
#         for location_index in rep_locations[tag_index]:
#             g = sns.scatterplot(data = rep_data_observe[tag_index], x=rep_x_observe+str(location_index),y=rep_headers_observe[header_index]+str(location_index))
#             g.set(xlabel=None)
#             g.set(ylabel=None)
#         if row == 0:
#             plt.title(rep_tags[tag_index])
#         if col == 0:
#             plt.ylabel(rep_headers_observe[header_index])
#         if row == (len(rep_headers_observe) - 1):
#             plt.xlabel(rep_x_observe)

# plt.show()
