# -*- coding: utf-8 -*-
"""
Created on Sun Aug 28 12:14:45 2022

@author: kient
"""

# -*- coding: utf-8 -*-
"""
Created on Thu Aug 25 09:57:59 2022

@author: kient
"""

import os
import re
import pandas as pd
import numpy as np

exp_number = 'Calibrate_beta'

local_path = "D:\\plot\\Validation\\" + str(exp_number) + "\\"
local_path_raw = local_path + "\\output"
local_path_input = local_path + "\\input"

config_df = pd.read_csv(os.path.join(local_path_input,'inputs.csv'),index_col=False)
config_df.set_index('Index', inplace=True)

first_day = 120
second_day = 360
range_1 = [10,14]
range_2 = range(22,32)#Calibrate_Z_Kappa_0-50 is 21-31, else 22-32    
# tm,kappa = {0.0, 0.1}
tm,kappa = {0.5, 0.1}
z = 5.2

n_run = 1
data = []
for index,config in config_df.iterrows():
    # print(index,config)
    for run in range(n_run):
        # print(run)
        if config.treatment == tm and config.kappa == kappa and config.z == z:
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

data_plot.to_csv(local_path + str(exp_number) + '_S9-10_tm' + str(tm) + '_k' + str(kappa) + '_z' + str(z) + ".csv",index=False)  


data_plot = pd.read_csv(local_path + str(exp_number) + '_S9-10_tm' + str(tm) + '_k' + str(kappa) + '_z' + str(z) + ".csv") 


sum_moi = data_plot[["moi"+str(x) for x in range(1,10)]].sum(axis=1)
for x in range(1,10):
    data_plot["moi"+str(x)] = data_plot["moi"+str(x)]/sum_moi   


import seaborn as sns
from matplotlib import pyplot as plt

plt.close("all")   
plot = sns.scatterplot(data=data_plot, x="eir", y="pfpr", hue="month") 
plot.set(xscale="log")
plot.set(xlim=(10**-1,10**3),ylim=(0,100))
plot.set_yticks(range(0,100,10))
plot.set_xlabel('EIR')
plot.set_ylabel('% PfPR')
# plot.set(xlim=(0, 10))

plot.figure.savefig(local_path + str(exp_number) + '_S9-10_Log_tm' + str(tm) + '_k' + str(kappa) + '_z' + str(z) + '.png', dpi=300)

import seaborn as sns
from matplotlib import pyplot as plt

plt.close("all")   
plot = sns.scatterplot(data=data_plot, x="eir", y="pfpr", hue="month") 
plot.set(yscale="linear")
# plot.set(xlim=(0,10**3),ylim=(0,1.0))
plot.set_xlabel('EIR')
plot.set_ylabel('% PfPR')
# plot.set_yticks(range(0,100,10))
# plot.set(xlim=(0, 10))

plot.figure.savefig(local_path + str(exp_number) + '_S9-10_Linear_tm' + str(tm) + '_k' + str(kappa) + '_z' + str(z) + '.png', dpi=300)