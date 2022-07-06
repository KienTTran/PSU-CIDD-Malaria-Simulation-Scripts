# -*- coding: utf-8 -*-
"""
Created on Tue May  3 11:07:17 2022

@author: kient
"""

import os
import re
import pandas as pd
import numpy as np
import math
import matplotlib.pyplot as plt
import seaborn as sns

a4_dims = (11.7, 8.27)

exp_number = 17

local_path = "D:\\plot\\PRMC_Exp_" + str(exp_number) + "\\"
local_path_raw = local_path + "\\raw"
local_path_bin = local_path + "\\bin"

config_df = pd.read_csv(local_path_bin + '\\configs.csv',index_col=False)
config_df.set_index('Index', inplace=True)

#%%
# n_run = 1
n_run = 10

data = []
data_plot = []

for index,config in config_df.iterrows(): 
    for run in range(n_run):
        # print(run)
        if n_run == 1:
            filename_db = "gene_db_%d.txt"%(0)
            filename_freq = "gene_freq_%d.txt"%(0)
        else:
            filename_db = "gene_db_%d.txt"%(index*1000 + run)
            filename_freq = "gene_freq_%d.txt"%(index*1000 + run)
        # print(filename) 
        beta = config.beta 
        prmc_size = config.prmc_size      
        ifr = config.ifr
        # print(beta,ifr)        
        file_path_db = os.path.join(local_path_raw, filename_db)
        file_path_freq = os.path.join(local_path_raw, filename_freq)
        try:
            csv_db = pd.read_csv(file_path_db, sep='\t', header=None,index_col=None)
            csv_db.columns = ["id","aa_sequence"]   
            genotype_names = csv_db.aa_sequence
            genotype_names = pd.concat([genotype_names, pd.Series(["temp"])], ignore_index=True)
            csv_freq = pd.read_csv(file_path_freq, sep='\t', header=None, names = genotype_names, index_col=None)
            csv_freq = csv_freq.fillna(0)
            csv_freq = csv_freq.drop(['temp'], axis=1)
            csv_freq['month'] = csv_freq.index
            csv_freq['year'] = np.floor(csv_freq['month'] / 12)
            csv_freq['beta'] = [beta]*len(csv_freq)
            csv_freq['prmc_size'] = [prmc_size]*len(csv_freq)
            csv_freq['ifr'] = [ifr]*len(csv_freq)
            # csv_freq['ld'] = csv_freq[csv_db.aa_sequence[0]]*csv_freq[csv_db.aa_sequence[1]] - csv_freq[csv_db.aa_sequence[2]]*csv_freq[csv_db.aa_sequence[3]]
            data.append(csv_freq)            
        except Exception as e:
            print(" error reading " + str(e))
        
data_plot = pd.concat(data,ignore_index=True, axis = 0)

#%%
data_plot.to_csv(local_path + "data_plot_exp" + str(exp_number) + "_res_freq.csv",index=False)  

#%%
data_plot = pd.read_csv(local_path + "data_plot_exp" + str(exp_number) + "_res_freq.csv") 

all_genotypes = []
trip_res_genotypes = []
trip_res_short_names = []
non_trip_res_genotypes = []
parameters = []
    
trip_res_alleles = [
                    [[4,'Y'],[5,'Y'],[6,'1'],[9,'T'],[31,'Y'],[33,'2']], #triple resistant DHA-PPQ-AQ
                    # [[4,'N'],[5,'F'],[6,'1'],[9,'K'],[31,'Y'],[33,'2']] #triple resistant DHA-PPQ-LUM
                    # [[31,'Y'],[33,'2']], #double resistant DHA-PPQ                                        
                    # [[4,'Y'],[5,'Y'],[6,'1'],[9,'T'],[31,'Y']], #double resistant ASAQ                    
                    # [[4,'N'],[5,'F'],[6,'1'],[9,'K'],[31,'Y']], #double resistant AL
                    ]
 
for column in data_plot.columns:
    if '|||' in column:
        all_genotypes.append(column)
        for item_list in trip_res_alleles:
            all_true = 0
            for item in item_list:
                if column[item[0]] == item[1]:
                    all_true += 0
                else:
                    all_true += 1 
            short_name = ''           
            if all_true == 0 and data_plot[column].sum() != 0.0:
                trip_res_genotypes.append(column)  
                for item in item_list:
                    short_name += (column[item[0]])
                trip_res_short_names.append(short_name)  
    else:
        parameters.append(column)
        
for column in data_plot.columns:
     if '|||' in column and column not in trip_res_genotypes:
         non_trip_res_genotypes.append(column)
         
print('Triple resistant genotype: ')
print(trip_res_genotypes)
print(trip_res_short_names)
#%%
#Plot all genotypes
data_plot_melt = data_plot.melt(id_vars=[*parameters
                                         ], var_name='genotypes', value_name='freq')

plot = sns.relplot(data = data_plot_melt, 
            x = 'year',
            y = 'freq',
            # col = 'cols',
            # row = 'beta',
            hue = 'genotypes',
            style = 'genotypes',
            kind = "line",
            ci = "sd",
            palette=sns.color_palette("husl",len(data_plot_melt.genotypes.unique()))[:len(data_plot_melt.genotypes.unique())],
            height = a4_dims[1], aspect = 1.5
            )

plot.set(xlim=(0, 30))
# plot.set(ylim=(0, 0.2))
plot.set(xticks=range(0,30,2))
# plot.set(yticks=np.arange(0,0.2,0.05))
# plot.map(plt.axhline, y=0.01, ls='--', linewidth=2, color='red')
plot.fig.subplots_adjust(bottom=0.1);    
plt.subplots_adjust(hspace = 0.2, wspace = 0.1) 

plot.savefig(local_path + "data_plot_exp_" + str(exp_number) + "_res_freq_all.png", dpi=300)
plt.close()
#%%
#Plot triple resistant genotypes
data_plot_melt = data_plot.melt([*parameters
                                ],var_name='genotypes', value_name='freq')

plot = sns.relplot(data = data_plot_melt, 
            x = 'year',
            y = 'freq',
            # col = 'cols',
            # row = 'beta',
            hue = 'genotypes',
            style = 'genotypes',
            kind = "line",
            ci = "sd",
            palette=sns.color_palette("husl",len(data_plot_melt.genotypes.unique()))[:len(data_plot_melt.genotypes.unique())],
            # height = a4_dims[1], aspect = 1.5
            )

plot.set(ylim=(0, 0.02))
plot.set(yticks=np.arange(0,0.02,0.005))
plot.set(xlim=(0, 30))
plot.set(xticks=range(0,30,2))
plot.map(plt.axhline, y=0.01, ls='--', linewidth=2, color='red')
plot.fig.subplots_adjust(bottom=0.1);    
plt.subplots_adjust(hspace = 0.2, wspace = 0.1) 

plot.savefig(local_path + "data_plot_exp_" + str(exp_number) + "_res_freq_all_freq_0.01.png", dpi=300)
plt.close()

#%%
#Plot triple resistant genotypes
data_plot_melt = data_plot.melt([*parameters
                                 ,*non_trip_res_genotypes
                                ],var_name='genotypes', value_name='freq')

color_pallete = sns.color_palette("husl",len(data_plot_melt.ifr.unique()))[:len(data_plot_melt.ifr.unique())]
plot = sns.relplot(data = data_plot_melt, 
            x = 'year',
            y = 'freq',
            col = 'prmc_size',
            row = 'beta',
            hue = 'ifr',
            # style = 'genotypes',
            kind = "line",
            ci = "sd",
            facet_kws=dict(sharex=False),
            palette=sns.color_palette("husl",len(data_plot_melt.ifr.unique()))[:len(data_plot_melt.ifr.unique())],
            # height = a4_dims[1], aspect = 1.5
            )

for ax in plot.axes.flatten():
    beta = float(ax.get_title().split(' | ')[0].split(' = ')[1])
    prmc_size = float(ax.get_title().split(' | ')[1].split(' = ')[1])
    data_res = data_plot_melt[(data_plot_melt.beta == beta ) & (data_plot_melt.prmc_size == prmc_size)
                                        & (data_plot_melt['genotypes'] == trip_res_genotypes[0])]

    data_res_freq = data_res.groupby(['year','ifr']).freq.mean()
    
    for index,ifr in enumerate(data_res.ifr.unique()):
        xi = data_res.year.unique()
        yi = data_res_freq.xs(ifr, level=1, drop_level=False).values
        x_res = np.interp(0.010, yi, xi, period = np.inf)
        ax.axhline(y=0.010, ls='--', lw=2, color='red')  
        ax.axvline(x = x_res, ls='--', lw=2, color=color_pallete[index]) 
        
plot.set(xlim=(5, 30))
plot.set(ylim=(0, 0.015))
plot.set(xticks=range(5,30,2))
plot.set(yticks=np.arange(0,0.015,0.005))
plt.subplots_adjust(hspace = 0.1, wspace = 0.05)

plot.savefig(local_path + "data_plot_exp_" + str(exp_number)  + "_" + str(trip_res_short_names[0]) + "_res_freq_triple_beta_prmc_size.png", dpi=300)
plt.close()
#%%
#Plot triple resistant genotypes
data_plot_melt = data_plot.melt([*parameters
                                 ,*non_trip_res_genotypes
                                ],var_name='genotypes', value_name='freq')

data_plot_melt = data_plot_melt[(data_plot_melt.ifr == 0.0) | (data_plot_melt.ifr == 0.05) | (data_plot_melt.ifr == 0.2)]

color_pallete = sns.color_palette("husl",len(data_plot_melt.ifr.unique()))[:len(data_plot_melt.ifr.unique())]
plot = sns.relplot(data = data_plot_melt, 
            x = 'year',
            y = 'freq',
            col = 'prmc_size',
            row = 'beta',
            hue = 'ifr',
            # style = 'genotypes',
            kind = "line",
            ci = "sd",
            facet_kws=dict(sharex=False),
            palette=sns.color_palette("husl",len(data_plot_melt.ifr.unique()))[:len(data_plot_melt.ifr.unique())],
            # height = a4_dims[1], aspect = 1.5
            )

for ax in plot.axes.flatten():
    beta = float(ax.get_title().split(' | ')[0].split(' = ')[1])
    prmc_size = float(ax.get_title().split(' | ')[1].split(' = ')[1])
    data_res = data_plot_melt[(data_plot_melt.beta == beta ) & (data_plot_melt.prmc_size == prmc_size)
                                        & (data_plot_melt['genotypes'] == trip_res_genotypes[0])]

    # data_res_freq = data_res.groupby(['year','ifr']).freq.mean()
    
    for index,ifr in enumerate(data_res.ifr.unique()):
        # xi = data_res.year.unique()
        # yi = data_res_freq.xs(ifr, level=1, drop_level=False).values
        # x_res = np.interp(0.010, yi, xi, period = np.inf)
        ax.axhline(y=0.010, ls='--', lw=2, color='red')  
        # ax.axvline(x = x_res, ls='--', lw=2, color=color_pallete[index]) 
        
plot.set(xlim=(5, 30))
plot.set(ylim=(0, 0.015))
plot.set(xticks=range(5,30,2))
plot.set(yticks=np.arange(0,0.015,0.005))
plt.subplots_adjust(hspace = 0.1, wspace = 0.05)

plot.savefig(local_path + "data_plot_exp_" + str(exp_number)  + "_" + str(trip_res_short_names[0]) +  "_res_freq_triple_ifr_0.0_0.05_0.2.png", dpi=300)
plt.close()

#%%
#Plot triple resistant genotypes
data_plot_melt = data_plot.melt([*parameters
                                 ,*non_trip_res_genotypes
                                ],var_name='genotypes', value_name='freq')

data_plot_melt = data_plot_melt[(data_plot_melt.prmc_size == 80) | (data_plot_melt.prmc_size == 120) 
                                | (data_plot_melt.prmc_size == 160) | (data_plot_melt.prmc_size == 200)]

color_pallete = sns.color_palette("husl",len(data_plot_melt.ifr.unique()))[:len(data_plot_melt.ifr.unique())]
plot = sns.relplot(data = data_plot_melt, 
            x = 'year',
            y = 'freq',
            col = 'ifr',
            row = 'beta',
            hue = 'prmc_size',
            # style = 'genotypes',
            kind = "line",
            ci = "sd",
            facet_kws=dict(sharex=False),
            palette=sns.color_palette("husl",len(data_plot_melt.prmc_size.unique()))[:len(data_plot_melt.prmc_size.unique())],
            # height = a4_dims[1], aspect = 1.5
            )

for ax in plot.axes.flatten():
    beta = float(ax.get_title().split(' | ')[0].split(' = ')[1])
    ifr = float(ax.get_title().split(' | ')[1].split(' = ')[1])
    data_res = data_plot_melt[(data_plot_melt.beta == beta ) & (data_plot_melt.ifr == ifr)
                                        & (data_plot_melt['genotypes'] == trip_res_genotypes[0])]

    # data_res_freq = data_res.groupby(['year','ifr']).freq.mean()
    
    for index,size in enumerate(data_res.prmc_size.unique()):
        # xi = data_res.year.unique()
        # yi = data_res_freq.xs(ifr, level=1, drop_level=False).values
        # x_res = np.interp(0.010, yi, xi, period = np.inf)
        ax.axhline(y=0.010, ls='--', lw=2, color='red')  
        # ax.axvline(x = x_res, ls='--', lw=2, color=color_pallete[index]) 
        
plot.set(xlim=(5, 30))
plot.set(ylim=(0, 0.015))
plot.set(xticks=range(5,30,2))
plot.set(yticks=np.arange(0,0.015,0.005))
plt.subplots_adjust(hspace = 0.1, wspace = 0.05)

plot.savefig(local_path + "data_plot_exp_" + str(exp_number)  + "_" + str(trip_res_short_names[0]) +  "_res_freq_triple_prmc_size_80_120_160_200.png", dpi=300)
plt.close()
#%%
# #Plot triple resistant genotypes
# data_plot_melt = data_plot.melt([*parameters
#                                  ,*non_trip_res_genotypes
#                                 ],var_name='genotypes', value_name='freq')

# data_plot_melt = data_plot_melt[((data_plot_melt.ifr == 0.0) | (data_plot_melt.ifr == 0.05) | (data_plot_melt.ifr == 0.2))
#                                 & ((data_plot_melt.beta == 0.08) | (data_plot_melt.beta == 0.7))]

# color_pallete = sns.color_palette("husl",len(data_plot_melt.ifr.unique()))[:len(data_plot_melt.ifr.unique())]
# plot = sns.relplot(data = data_plot_melt, 
#             x = 'year',
#             y = 'freq',
#             col = 'prmc_size',
#             row = 'beta',
#             hue = 'ifr',
#             # style = 'genotypes',
#             kind = "line",
#             ci = "sd",
#             facet_kws=dict(sharex=False),
#             palette=sns.color_palette("husl",len(data_plot_melt.ifr.unique()))[:len(data_plot_melt.ifr.unique())],
#             # height = a4_dims[1], aspect = 1.5
#             )

# for ax in plot.axes.flatten():
#     beta = float(ax.get_title().split(' | ')[0].split(' = ')[1])
#     prmc_size = float(ax.get_title().split(' | ')[1].split(' = ')[1])
#     data_res = data_plot_melt[(data_plot_melt.beta == beta ) & (data_plot_melt.prmc_size == prmc_size)
#                                         & (data_plot_melt['genotypes'] == trip_res_genotypes[0])]

#     # data_res_freq = data_res.groupby(['year','ifr']).freq.mean()
    
#     for index,ifr in enumerate(data_res.ifr.unique()):
#         # xi = data_res.year.unique()
#         # yi = data_res_freq.xs(ifr, level=1, drop_level=False).values
#         # x_res = np.interp(0.010, yi, xi, period = np.inf)
#         ax.axhline(y=0.010, ls='--', lw=2, color='red')  
#         # ax.axvline(x = x_res, ls='--', lw=2, color=color_pallete[index]) 
        
# plot.set(xlim=(5, 30))
# plot.set(ylim=(0, 0.015))
# plot.set(xticks=range(5,30,2))
# plot.set(yticks=np.arange(0,0.015,0.005))
# plt.subplots_adjust(hspace = 0.1, wspace = 0.05)

# plot.savefig(local_path + "data_plot_exp_" + str(exp_number)  + "_" + str(trip_res_short_names[0]) +  "_res_freq_triple_beta_0.08_0.7_ifr_0.0_0.05_0.2.png", dpi=300)
# plt.close()

#Plot triple resistant genotypes
data_plot_melt = data_plot[data_plot.prmc_size == 80].melt([*parameters
                                 ,*non_trip_res_genotypes
                                ],var_name='genotypes', value_name='freq')

color_pallete = sns.color_palette("husl",len(data_plot_melt.ifr.unique()))[:len(data_plot_melt.ifr.unique())]
plot = sns.relplot(data = data_plot_melt, 
            x = 'year',
            y = 'freq',
            col = 'beta',
            hue = 'ifr',
            # style = 'prmc_size',
            kind = "line",
            ci = "sd",
            facet_kws=dict(sharex=False),
            palette=sns.color_palette("husl",len(data_plot_melt.ifr.unique()))[:len(data_plot_melt.ifr.unique())],
            # height = a4_dims[1], aspect = 1.5
            )
for index,ax in enumerate(plot.axes.flatten()):
    # beta = float(ax.get_title().split(' | ')[0].split(' = ')[1])
    # ifr = float(ax.get_title().split(' | ')[1].split(' = ')[1])
    # data_res = data_plot_melt[(data_plot_melt.beta == beta ) 
    #                           # & (data_plot_melt.ifr == ifr)
    #                           & (data_plot_melt['genotypes'] == trip_res_genotypes[0])]

    # data_res_freq = data_res.groupby(['year']).freq.mean()
    # xi = data_res.year.unique()
    # yi = data_res_freq
    # sns.lineplot(data = data_res_freq, x=xi, y=yi, ax=ax, color='red', lw=2,ls='--')
    # x_res = np.interp(0.010, yi, xi, period = np.inf)
    # ax.axvline(x = x_res, ls='--', lw=2, color='red')
    ax.axhline(y=0.010, ls='--', lw=2, color='red') 
    
plot.set(xlim=(5, 30))
plot.set(ylim=(0, 0.015))
plot.set(xticks=range(5,30,2))
plot.set(yticks=np.arange(0,0.015,0.005))
plt.subplots_adjust(hspace = 0.1, wspace = 0.05)

plot.savefig(local_path + "data_plot_exp_" + str(exp_number)  + "_" + str(trip_res_short_names[0]) +  "_res_freq_triple-size_80_0.0_0.05_0.2.png", dpi=300)
plt.close()

#Plot triple resistant genotypes
data_plot_melt = data_plot[data_plot.prmc_size == 120].melt([*parameters
                                 ,*non_trip_res_genotypes
                                ],var_name='genotypes', value_name='freq')

color_pallete = sns.color_palette("husl",len(data_plot_melt.ifr.unique()))[:len(data_plot_melt.ifr.unique())]

plot = sns.relplot(data = data_plot_melt, 
            x = 'year',
            y = 'freq',
            col = 'beta',
            hue = 'ifr',
            # hue = 'prmc_size',
            # style = 'prmc_size',
            kind = "line",
            ci = "sd",
            facet_kws=dict(sharex=False),
            palette=sns.color_palette("husl",len(data_plot_melt.ifr.unique()))[:len(data_plot_melt.ifr.unique())],
            # height = a4_dims[1], aspect = 1.5
            )

for index,ax in enumerate(plot.axes.flatten()):
    # beta = float(ax.get_title().split(' | ')[0].split(' = ')[1])
    # ifr = float(ax.get_title().split(' | ')[1].split(' = ')[1])
    # data_res = data_plot_melt[(data_plot_melt.beta == beta ) 
    #                           # & (data_plot_melt.ifr == ifr)
    #                           & (data_plot_melt['genotypes'] == trip_res_genotypes[0])]

    # data_res_freq = data_res.groupby(['year']).freq.mean()
    # xi = data_res.year.unique()
    # yi = data_res_freq
    # sns.lineplot(data = data_res_freq, x=xi, y=yi, ax=ax, color='red', lw=2,ls='--')
    # x_res = np.interp(0.010, yi, xi, period = np.inf)
    # ax.axvline(x = x_res, ls='--', lw=2, color='red')
    ax.axhline(y=0.010, ls='--', lw=2, color='red') 
    
plot.set(xlim=(5, 30))
plot.set(ylim=(0, 0.015))
plot.set(xticks=range(5,30,2))
plot.set(yticks=np.arange(0,0.015,0.005))
plt.subplots_adjust(hspace = 0.1, wspace = 0.05)

plot.savefig(local_path + "data_plot_exp_" + str(exp_number)  + "_" + str(trip_res_short_names[0]) +  "_res_freq_triple-size_120_0.0_0.05_0.2.png", dpi=300)
plt.close()

#Plot triple resistant genotypes
data_plot_melt = data_plot[data_plot.prmc_size == 160].melt([*parameters
                                 ,*non_trip_res_genotypes
                                ],var_name='genotypes', value_name='freq')

color_pallete = sns.color_palette("husl",len(data_plot_melt.ifr.unique()))[:len(data_plot_melt.ifr.unique())]

plot = sns.relplot(data = data_plot_melt, 
            x = 'year',
            y = 'freq',
            col = 'beta',
            hue = 'ifr',
            # hue = 'prmc_size',
            # style = 'prmc_size',
            kind = "line",
            ci = "sd",
            facet_kws=dict(sharex=False),
            palette=sns.color_palette("husl",len(data_plot_melt.ifr.unique()))[:len(data_plot_melt.ifr.unique())],
            # height = a4_dims[1], aspect = 1.5
            )

for index,ax in enumerate(plot.axes.flatten()):
    # beta = float(ax.get_title().split(' | ')[0].split(' = ')[1])
    # ifr = float(ax.get_title().split(' | ')[1].split(' = ')[1])
    # data_res = data_plot_melt[(data_plot_melt.beta == beta ) 
    #                           # & (data_plot_melt.ifr == ifr)
    #                           & (data_plot_melt['genotypes'] == trip_res_genotypes[0])]

    # data_res_freq = data_res.groupby(['year']).freq.mean()
    # xi = data_res.year.unique()
    # yi = data_res_freq
    # sns.lineplot(data = data_res_freq, x=xi, y=yi, ax=ax, color='red', lw=2,ls='--')
    # x_res = np.interp(0.010, yi, xi, period = np.inf)
    # ax.axvline(x = x_res, ls='--', lw=2, color='red')
    ax.axhline(y=0.010, ls='--', lw=2, color='red') 
    
plot.set(xlim=(5, 30))
plot.set(ylim=(0, 0.015))
plot.set(xticks=range(5,30,2))
plot.set(yticks=np.arange(0,0.015,0.005))
plt.subplots_adjust(hspace = 0.1, wspace = 0.05)

plot.savefig(local_path + "data_plot_exp_" + str(exp_number) + "_" + str(trip_res_short_names[0]) + "_res_freq_triple-size_160_0.0_0.05_0.2.png", dpi=300)
plt.close()
