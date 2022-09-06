# -*- coding: utf-8 -*-
"""
Created on Fri Sep  2 12:53:46 2022

@author: kient
"""
import math
import seaborn as sns
from matplotlib import pyplot as plt
import numpy as np
import pandas as pd
import os

exp_number = 'Calibrate_beta'

local_path = "D:\\plot\\Validation\\" + str(exp_number) + "\\Others" +  "\\"
local_path_raw = local_path + "\\output"
local_path_input = local_path + "\\input"

config_df = pd.read_csv(os.path.join(local_path_input,'inputs.csv'),index_col=False)
config_df.set_index('Index', inplace=True)

#%%
kappa = np.round(np.arange(0.1,2.51,0.25),2)
# kappa = config_df.kappa.unique()
a = np.arange(1,11,1)
data = []
a2_10 = math.pow(1.01,10 - 10)*0.0013809

for age in a:
    a2 = []      
    a2.append(age)
    for k in kappa: 
        a2.append(math.pow(age/10.0,k) * math.pow(1.01,age) * 0.00125 / a2_10)
    data.append(a2)
            
data_plot = pd.DataFrame(data)
kappa_column = [str(x) for x in kappa]
data_plot.columns = ['age',*kappa_column]
data_plot_melt = data_plot.melt(['age'],var_name='kappa',value_name='age2/age10')

fig, ax = plt.subplots(1,1)
plot = sns.lineplot(data=data_plot_melt,x='age',y='age2/age10',hue='kappa',palette='tab10') 
ax.set_xlim(1,10)
ax.set_xticks(range(1,11,1))
ax.set_xlabel('Age')
ax.set_ylabel(r'$\dfrac{a2(age)}{a2(10)}$',rotation=0)
plt.legend(ncol=2)

figure = plt.gcf() # get current figure
figure.set_size_inches(16, 10)
plt.savefig(local_path + str(exp_number) + '_S1.png', dpi=100)
# plot.figure.savefig(local_path + str(exp_number) + '_S1.png', dpi=300)
#%%
plt.close('all')
data = []
# z = [2.0,4.0,6.0,8.0]	
z = np.round(np.arange(1,10.01,1.0),2)	
m = np.round(np.arange(0,1.0,0.01),2)

for mm in m:
    p_cli = []
    p_cli.append(mm)
    for zz in z:
        p_cli.append(0.99 / (1 + math.pow((mm/0.4),zz)))
    data.append(p_cli)
    
data_plot = pd.DataFrame(data)
z_column = [str(x) for x in z]
data_plot.columns = ['immune_level',*z]
data_plot_melt = data_plot.melt(['immune_level'],var_name='z',value_name='p_cli')

fig, ax = plt.subplots(1,1)
sns.lineplot(data=data_plot_melt,x='immune_level',y='p_cli',hue='z',palette='tab10',ax=ax)  
ax.set_xlim(0,1.0)
ax.set_xticks(np.arange(0,1.1,0.1))
ax.set_xlabel('Immunity Level')
ax.set_ylabel('Probability of developing symptoms')
plt.legend(ncol=2)

figure = plt.gcf() # get current figure
figure.set_size_inches(16, 10)
plt.savefig(local_path + str(exp_number) + '_S2.png', dpi=100)
# plot.figure.savefig(local_path + str(exp_number) + '_S2.png', dpi=300)