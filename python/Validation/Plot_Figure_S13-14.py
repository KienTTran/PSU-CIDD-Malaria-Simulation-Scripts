# -*- coding: utf-8 -*-
"""
Created on Sun Aug 28 21:51:08 2022

@author: kient
"""

import os
import re
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
import seaborn as sns

exp_number = 'Calibrate_beta'

local_path = "D:\\plot\\Validation\\" + str(exp_number) + "\\Others" +  "\\"
local_path_raw = local_path + "\\output"
local_path_input = local_path + "\\input"

config_df = pd.read_csv(os.path.join(local_path_input,'inputs.csv'),index_col=False)
config_df.set_index('Index', inplace=True)

first_day = 120
second_day = 360
range_1 = [10,14]
range_2 = range(22,32)

# tm,kappa,z,gamma_sd = (0.0, 0.2, 4.6,10)
tm,kappa,z,gamma_sd = (0.5, 0.3, 5.4,10)

n_run = 100
data = []
for index,config in config_df.iterrows():
    # print(index,config)
    for run in range(n_run):
        # print(run)
        if float(config.treatment) == float(tm) and float(config.kappa) == float(kappa) \
        and float(config.z) == float(z) and float(config.gamma_sd) == float(gamma_sd):
            filename = "validation_monthly_data_%d.txt"%(run + index*1000)
            # print(filename)
            beta = config.beta 
            file_path = os.path.join(local_path_raw, filename)
            try:
                csv = pd.read_csv(file_path,sep='\t',header=None,index_col=None)
                row = csv.iloc[first_day,range_1 + [*range_2]] 
                r = row.to_list()
                r.append(first_day)
                r.append(beta)
                data.append(r)
                # row = csv.iloc[first_day,range_1 + [*range_2]]  
                # r = row.to_list()
                # r.append(second_day)
                # r.append(beta)
                # data.append(r)        
            except:
                print(filename + " error reading")
        
data_plot = pd.DataFrame(data)
data_plot.columns = ["eir","pfpr",*["moi"+str(x) for x in range(10)],"month","beta"]

data_plot.to_csv(local_path + str(exp_number) + '_S13-14_tm' + str(tm) + '_k' + str(kappa) + '_z' + str(z) + ".csv",index=False)  

data_plot = pd.read_csv(local_path + str(exp_number) + '_S13-14_tm' + str(tm) + '_k' + str(kappa) + '_z' + str(z) + ".csv") 

sum_moi = data_plot[["moi"+str(x) for x in range(1,10)]].sum(axis=1)
for x in range(1,10):
    data_plot["moi"+str(x)] = data_plot["moi"+str(x)]/sum_moi     

data_120 = data_plot[data_plot.month == 120]   
betas = data_120.beta.unique()
#%%
fig, axes = plt.subplots(4,5,sharex=True,sharey=True, squeeze=True)
for index,beta in enumerate(betas):
    r = index//5
    c = index % 5
    data_beta = data_120[((data_120.beta == beta))]
    data_moi = data_beta[["moi"+str(x) for x in range(1,10)]]
    data_moi.columns=[*range(1,10)]
    data_moi_melt = pd.melt(data_moi)
    data_moi_melt.columns = ["MOI","freq"]
    sns.boxplot(data=data_moi_melt,x="MOI",y="freq",ax=axes[r,c])
    
    eir_percentile = np.percentile(data_beta["eir"],[25,50,75])
    pfpr_percentile = np.percentile(data_beta["pfpr"],[25,50,75])

    axes[r,c].set_ylabel('Percent Frequency')
    axes[r,c].set_xlabel('Number of Clones')
    if r < 3:
        axes[r,c].set_xlabel("")
    if c > 0:
        axes[r,c].set_ylabel("")
    
    axes[r,c].set_title("EIR: %.2f - PFPR: %.2f"%(eir_percentile[1],pfpr_percentile[1]))
    
figure = plt.gcf() # get current figure
figure.set_size_inches(16, 12)
plt.savefig(local_path + str(exp_number) + '_S13-14_tm' + str(tm) + '_k' + str(kappa) + '_z' + str(z) + '.png', dpi=100)