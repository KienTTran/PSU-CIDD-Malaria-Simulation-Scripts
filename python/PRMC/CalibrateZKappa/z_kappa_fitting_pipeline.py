# -*- coding: utf-8 -*-
"""
Created on Thu Apr 21 19:35:01 2022

@author: nguyentd
"""

import pandas as pd
import numpy as np
import os
from scipy.optimize import curve_fit

exp_number = 'Calibrate_Z_Kappa_Treatment_0'
local_path = "D:\\plot\\Validation\\" + str(exp_number) + "\\"

data = pd.read_csv(os.path.join(local_path,str(exp_number) + ".csv"))

data['age2to10'] = data.age1/data.age9

data = data[data.eir > 0.1]

data['logEIR'] = np.log10(data['eir'])
# data['age2to10'] = np.log(data['age2to10'])

observed_EIR = np.log10([10,18,20,30,37.5,38,200,200])
observed_age2to10 = ([1.6/0.5, 0.42/0.13, 2.2/2.8, 2.1/2.7, 1.55/0.3, 0.87/0.28, 5/0.6, 5/0.5])
#%%
import seaborn as sns
from matplotlib import pyplot as plt
from numpy import mean, sqrt, square

nr = len(data.z.unique())
nc = len(data.kappa.unique())

def my_curve_fit(data):
    # p0 = [data.age2to10.max(), np.median(data.logEIR),1, data.age2to10.min()] # this is an mandatory initial guess
    # popt,pcov = curve_fit(sigmoid, data.logEIR, data.age2to10, p0, maxfev=5000, method='trf')
    fn = lambda x, a, b : a*np.exp(b*x) + data.age2to10.min()
    p0 = [1,1] # this is an mandatory initial guess
    popt,pcov = curve_fit(fn, data.logEIR, data.age2to10, p0, maxfev=15000)
    
    return fn,popt,pcov


rmsq_data = []

for i_z, z in enumerate(data.z.unique()):
    for i_kappa, kappa in enumerate(data.kappa.unique()):
        f_data = data[(data.z == z) & (data.kappa == kappa)]
        
        func, popt, pcov = my_curve_fit(f_data)
        rmsq_score = sqrt(mean(square( func(observed_EIR, *popt) - observed_age2to10)))
        
        rmsq_data.append([z, kappa, rmsq_score])
       
        
#%%
from scipy.ndimage.filters import gaussian_filter
# plt.figure(figsize=(8, 6), dpi=300)

rmsq_df = pd.DataFrame(rmsq_data)
rmsq_df.columns = ["z", "kappa", "rmsq_error"]

min_row = rmsq_df.rmsq_error.idxmin()
print(rmsq_df.iloc[min_row,:])

rmsq_df.rmsq_error = 2*np.log(rmsq_df.rmsq_error)
rmsq_df = rmsq_df.pivot("z", "kappa", "rmsq_error")

rmsq_df.columns = np.round(rmsq_df.columns,4)
rmsq_df.index = np.round(rmsq_df.index,4)

plot = sns.heatmap(rmsq_df, cmap="rocket_r", cbar_kws={'label': '2*ln_rmse'})
figure = plot.get_figure()   
figure.savefig(local_path+"heatmap.png", dpi=300)

plt.close('all')
rmsq_df_smooth =  pd.DataFrame(gaussian_filter(rmsq_df, sigma=1))
rmsq_df_smooth.columns = rmsq_df.columns
rmsq_df_smooth.index = rmsq_df.index
plot = sns.heatmap(rmsq_df_smooth, cmap="rocket_r", cbar_kws={'label': '2*ln_rmse'})
figure = plot.get_figure()   
figure.savefig(local_path+"heatmap_smooth.png", dpi=300)

#%%

import seaborn as sns
from matplotlib import pyplot as plt
from numpy import mean, sqrt, square
import math

nr = 5
nc = 8

fig, axes = plt.subplots(nr, nc, sharex=True, sharey=True,figsize=(8, 6), dpi=300)

z_len  = len(data.z.unique())
kappa_len = len(data.kappa.unique())

for i_z, z in enumerate(data.z.unique()[range(0,z_len, math.floor(z_len/nr))]):
    if (i_z >= nr):
        continue
    for i_kappa, kappa in enumerate(data.kappa.unique()[range(0,kappa_len, math.floor(kappa_len/nc))]):
        if (i_kappa >= nc):
            continue
        f_data = data[(data.z == z) & (data.kappa == kappa)]
        

        func,popt,pcov = my_curve_fit(f_data)

        xp = np.linspace(data.logEIR.min(), data.logEIR.max(), 100)
        
        sns.lineplot(x=xp, y=func(xp,*popt),ax=axes[i_z,i_kappa] )
        sns.scatterplot(x="logEIR", y="age2to10", data=f_data, ax=axes[i_z,i_kappa])
        sns.scatterplot(x=observed_EIR, y=observed_age2to10, ax=axes[i_z,i_kappa] )
        
        rmsq_score = sqrt(mean(square( func(observed_EIR,*popt) - observed_age2to10)))
        
        axes[i_z,i_kappa].set_ylim([-5,20])
        axes[i_z,i_kappa].set_ylabel("z=%.2f"%(z))
        axes[i_z,i_kappa].set_xlabel("k=%.2f"%(kappa))

fig.savefig(local_path+"curve_fit.png", dpi=300)