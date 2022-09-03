# -*- coding: utf-8 -*-
"""
Created on Tue Aug 30 09:26:52 2022

@author: kient
"""

import os
import re
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
import seaborn as sns

exp_number = 'Calibrate_beta'

local_path = "D:\\plot\\Validation\\" + str(exp_number) + "\\S1516" +  "\\"
local_path_raw = local_path + "\\output"
local_path_input = local_path + "\\input"

# tm,kappa,z = (0.0, 0.2, 4.6)
tm,kappa,z = (0.5, 0.3, 5.4)

#%%

config_df = pd.read_csv(os.path.join(local_path_input,'inputs.csv'),index_col=False)
config_df.set_index('Index', inplace=True)

n_run = 10
data = []
for index,config in config_df.iterrows():
    # print(index,config)
    for run in range(n_run):
        # print(run)
        if float(config.treatment) == float(tm) and float(config.kappa) == float(kappa) \
        and float(config.z) == float(z):
            filename_summary = "validation_summary_%d.txt"%(index*1000 + run)
            filename_monthly = "validation_monthly_data_%d.txt"%(index*1000 + run)
            file_path_summary = os.path.join(local_path_raw, filename_summary)
            file_path_monthly = os.path.join(local_path_raw, filename_monthly)
            try:
                csv_summary = pd.read_csv(file_path_summary,sep='\t',header=None,index_col=None) 
                csv_summary.iloc[0,15] = (float)(csv_summary.iloc[0,15].replace('%',''))
                row = csv_summary.iloc[0,[4,6,15]]
                r_summary = row.to_list()
            except Exception as e:
                print(csv_summary + " error reading " + str(e))
            try:
                csv_monthly = pd.read_csv(file_path_monthly,sep='\t',header=None,index_col=None)
                #clinical episode per person per year
                row = csv_monthly.iloc[:-1,[*range(201,216),217]].mean()
                r_monthly = row.to_list()
                r_monthly.append((float)(config.kappa))
                r_monthly.append((float)(config.z))
                r_monthly.append((float)(config.beta))
                r_monthly.append((float)(config.gamma_sd / 5.0))
            except Exception as e:
                print(csv_summary + " error reading " + str(e))
            
            data.append(r_summary + r_monthly)
        
data_plot = pd.DataFrame(data)
data_plot.columns = ["eir","pfpr","top20",*[str(x+1) for x in range(15)],"mean_immune","kappa","z","beta",'C.V']

#%%
data_plot.to_csv(local_path + str(exp_number) + '_S15-16_tm' + str(tm) + '_k' + str(kappa) + '_z' + str(z) + ".csv",index=False)  

#%%
data_plot = pd.read_csv(local_path + str(exp_number) + '_S15-16_tm' + str(tm) + '_k' + str(kappa) + '_z' + str(z) + ".csv")

#%% Draw all plots
data_plot_top_20 = data_plot.groupby('top20').mean()
data_plot_melt = data_plot.melt(id_vars=['beta', 'z', 'kappa', 'eir','pfpr', 'top20', 'mean_immune','C.V'],var_name='age_class', value_name='phi')

fig, axes = plt.subplots(2,2,sharex=True,sharey=False)

for row in range(2):
    for col in range(2):
        if row == 0 and col == 0:
            sns.scatterplot(data=data_plot_top_20, x='eir', y='top20', hue='C.V',palette='tab10',ax=axes[row,col])
            axes[row,col].set_yticks(range(0,100,10))
        if row == 0 and col == 1:
            sns.scatterplot(data=data_plot, x='eir', y='mean_immune', hue='C.V',palette='tab10',ax=axes[row,col])
        if row == 1 and col == 0:
            plot_1_0 = sns.scatterplot(data=data_plot, x='eir', y='pfpr', hue='C.V',palette='tab10',ax=axes[row,col])
        if row == 1 and col == 1:
            plot_1_1 = sns.scatterplot(data=data_plot_melt, x='eir', y='phi', hue='C.V',palette='tab10',ax=axes[row,col])
        axes[row,col].set_xlim(0,150)
        axes[row,col].set_xticks(range(0,150,50))
        
figure = plt.gcf() # get current figure
figure.set_size_inches(18, 12)
plt.savefig(local_path + str(exp_number) + '_S15-16_All_tm' + str(tm) + '_k' + str(kappa) + '_z' + str(z) + '.png', dpi=300)

#%% 
# data_plot_top_20 = data_plot.groupby('top20').mean()

# fig, ax = plt.subplots()
# plot = sns.scatterplot(data=data_plot_top_20, x='eir', y='top20', hue='C.V',palette='tab10')
# ax.set_xlim(0,150)
# ax.set_xticks(range(0,150,50))
# ax.set_yticks(range(0,100,10))

# plot.figure.savefig(local_path + str(exp_number) + '_S15-16_EIR_Top20_tm' + str(tm) + '_k' + str(kappa) + '_z' + str(z) + '.png', dpi=300)

# #%% 
# fig, ax = plt.subplots()
# plot = sns.scatterplot(data=data_plot, x='eir', y='mean_immune', hue='C.V',palette='tab10')
# ax.set_xlim(0,150)
# ax.set_xticks(range(0,150,50))

# plot.figure.savefig(local_path + str(exp_number) + '_S15-16_EIR_Mean_Immune_tm' + str(tm) + '_k' + str(kappa) + '_z' + str(z) + '.png', dpi=300)

# #%% 
# fig, ax = plt.subplots()
# plot = sns.scatterplot(data=data_plot, x='eir', y='pfpr', hue='C.V',palette='tab10')
# ax.set_xlim(0,150)
# ax.set_xticks(range(0,150,50))

# plot.figure.savefig(local_path + str(exp_number) + '_S15-16_EIR_PfPR_tm' + str(tm) + '_k' + str(kappa) + '_z' + str(z) + '.png', dpi=300)
# #%%
# data_plot_melt = data_plot.melt(id_vars=['beta', 'z', 'kappa', 'eir','pfpr', 'top20', 'mean_immune','C.V'],var_name='age_class', value_name='phi')

# fig, ax = plt.subplots()
# plot = sns.scatterplot(data=data_plot_melt, x='eir', y='phi', hue='C.V',palette='tab10')
# ax.set_xlim(0,150)
# ax.set_xticks(range(0,150,50))