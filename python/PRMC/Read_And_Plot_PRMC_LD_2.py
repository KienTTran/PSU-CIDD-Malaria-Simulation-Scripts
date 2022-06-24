# -*- coding: utf-8 -*-
"""
Created on Tue May 17 15:55:41 2022

@author: kient
"""

import os
import re
import pandas as pd
import numpy as np
import math
import itertools
import os
import re
import pandas as pd
import numpy as np
import math
import seaborn as sns
import random
import matplotlib.pyplot as plt
from itertools import combinations
import yaml

exp_number = 13

a4_dims = (11.69, 8.27)

local_path = "D:\\plot\\PRMC_2_Genotypes_Exp_" + str(exp_number) + "\\"
local_path_raw = local_path + "\\raw"
local_path_bin = local_path + "\\bin"

config_df = pd.read_csv(local_path_bin + '\\configs.csv',index_col=False)
config_df.set_index('Index', inplace=True)

n_run = 10

#%%
data = []
data_plot = []


with open(os.path.join(local_path_bin, 'sim_prmc.yml'), 'r') as stream:
    content = yaml.full_load(stream)
    mutation_mask = content['mutation_mask']

for index,config in config_df.iterrows():
    for run in range(n_run):
        # if index == 140:
        # print(run)
        filename_db = "gene_db_%d.txt"%(index*1000 + run)
        filename_freq = "gene_freq_%d.txt"%(index*1000 + run)
        # print(filename_db) 
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
            csv_freq = csv_freq.drop(['temp'], axis=1)
            csv_freq['mutation_mask'] = mutation_mask
            csv_freq['month'] = csv_freq.index
            csv_freq['year'] = np.floor(csv_freq['month'] / 12)
            csv_freq['beta'] = [beta]*len(csv_freq)
            csv_freq['prmc_size'] = [prmc_size]*len(csv_freq)
            csv_freq['ifr'] = [ifr]*len(csv_freq)
            csv_freq = csv_freq.fillna(0)
            data.append(csv_freq)
        except Exception as e:
            raise
            print(file_path_freq + " error reading " + str(e))
            
data_plot = pd.concat(data,ignore_index=True, axis = 0)    
data_plot = data_plot.fillna(0)

#%%
data_plot.to_csv(local_path + "data_plot_exp_" + str(exp_number) + "_LD_2.csv",index=False)          

#%%

data_plot = pd.read_csv(local_path + "data_plot_exp_" + str(exp_number) + "_LD_2.csv")

all_genotypes = []

for column in data_plot.columns:
    if '|||' in column:
        all_genotypes.append(column)
        
print(all_genotypes)

observe_index = 6
observe_genotype = all_genotypes[observe_index]

mask = data_plot['mutation_mask'][0]
masked_loci = []

for index,locus in enumerate(mask):
    if locus == '1':
        masked_loci.append(index)

loci_3 = random.sample(masked_loci,3)
loci_3_all = list(combinations(masked_loci, 3)) 

loci_3 = [9,31,33]

loci_2 = list(combinations(loci_3, 2))  
allele_map = {}

#p_i, p_j, p_k
for locus in loci_3:
    allele_map[locus] = observe_genotype[locus]
    data_plot[str(locus) + '-' + observe_genotype[locus]] = 0

#Psi_ij, Psi_jk, Psi_ik   
for locus_pair in loci_2:
    pair = str(locus_pair[0]) + '-' + observe_genotype[locus_pair[0]] + '-' + str(locus_pair[1]) + '-' + observe_genotype[locus_pair[1]]
    data_plot[pair] = 0
 
#Psi_ijk
pair = str(loci_3[0]) + '-' + allele_map[loci_3[0]] + '-' + str(loci_3[1]) + '-' + allele_map[loci_3[1]] + '-' + str(loci_3[2]) + '-' + allele_map[loci_3[2]]
data_plot[pair] = 0

print("I J K = " + str(loci_3[0]) + " " + str(loci_3[1]) + " " + str(loci_3[2]))

index = np.random.randint(0, len(data_plot), size=1)[0]
#Allele freq
for genotype in all_genotypes:
    print("Genotype " + str(index) + " " + genotype + " freq = " + str(data_plot[genotype][index]))
    #p_i, p_j, p_k
    for locus in loci_3:
        if genotype[locus] == allele_map[locus]:
            pair = str(locus) + '-' + allele_map[locus]
            data_plot[pair] += data_plot[genotype];
            print("  p_" + pair + " += " + str(data_plot[genotype][index]) + " = " + str(data_plot[pair][index]))
    #Psi_ij, Psi_jk, Psi_ik
    for locus_pair in loci_2:
        if genotype[locus_pair[0]] == allele_map[locus_pair[0]] and genotype[locus_pair[1]] == allele_map[locus_pair[1]]:            
            pair = str(locus_pair[0]) + '-' + allele_map[locus_pair[0]] + '-' + str(locus_pair[1]) + '-' + allele_map[locus_pair[1]]
            data_plot[pair] += data_plot[genotype]   
            print("  Psi_" + pair + " += " + str(data_plot[genotype][index]) + " = " + str(data_plot[pair][index]))
    #Psi_ijk
    if genotype[loci_3[0]] == allele_map[loci_3[0]] and genotype[loci_3[1]] == allele_map[loci_3[1]] and genotype[loci_3[2]] == allele_map[loci_3[2]]:
        pair = str(loci_3[0]) + '-' + allele_map[loci_3[0]] + '-' + str(loci_3[1]) + '-' + allele_map[loci_3[1]] + '-' + str(loci_3[2]) + '-' + allele_map[loci_3[2]]
        data_plot[pair] += data_plot[genotype]
        print("  Psi_" + pair + " += " + str(data_plot[genotype][index]) + " = " + str(data_plot[pair][index]))
 
ld_columns = data_plot.columns[-7:]

p_i = data_plot[ld_columns[0]]
p_j = data_plot[ld_columns[1]]
p_k = data_plot[ld_columns[2]]
Psi_ij = data_plot[ld_columns[3]]
Psi_ik = data_plot[ld_columns[4]]
Psi_jk = data_plot[ld_columns[5]]
Psi_ijk = data_plot[ld_columns[6]]
C_ij = Psi_ij - p_i * p_j
C_jk = Psi_jk - p_j * p_k
C_ik = Psi_ik - p_i * p_k
C_ijk = Psi_ijk - p_i*p_j*p_k
data_plot['ld-ij'] = C_ij
data_plot['ld-jk'] = C_jk
data_plot['ld-ik'] = C_ik
data_plot['ld-ijk'] = C_ijk
data_plot['ld'] = Psi_ijk - (p_i * C_jk) - (p_j * C_ik) - (p_k * C_ij) - p_i*p_j*p_k
# data_plot['ld'] = data_plot[all_genotypes[observe_index]] - (p_i * C_jk) - (p_j * C_ik) - (p_k * C_ij) - p_i*p_j*p_k
# print("Genotype " + str(index) + " LD = " 
#       + str(Psi_ijk[index])  
#       + " - " + str(p_i[index]) + "*" + str(C_jk[index]) 
#       + " - " + str(p_j[index]) + "*" + str(C_ik[index])  
#       + " - " + str(p_k[index]) + "*" + str(C_ij[index]) 
#       + " - " + str(p_i[index]) + "*" + str(p_j[index]) + "*" + str(p_k[index])
#       + " = " + str(data_plot['ld'][index]))

loci_3_str = '-'.join([str(elem) for elem in loci_3])

allele_3 = []
for locus in loci_3:
    allele_3.append(observe_genotype[locus])
    
allele_3_str = '-'.join([str(elem) for elem in allele_3])

#%%
plot = sns.relplot(data = data_plot, 
            x = 'year',
            y = 'ld',
            col = 'ifr',
            row = 'beta',
            hue = 'prmc_size',
            # style = "prmc_size",
            kind = "line",
            ci = 'sd',
            palette=sns.color_palette("husl",len(data_plot.prmc_size.unique()))[:len(data_plot.prmc_size.unique())],
            # height = a4_dims[1], aspect = 1.5
            )

# plot.set(xlim=(0, 30))
# plot.set(ylim=(-0.05, 0.05))
# plot.set(xticks=range(0,30,5))
# plot.set(yticks=np.arange(-0.05,0.05,0.025))
# for ax,beta,prmc_size in zip(plot.axes.flat,data_plot.beta.unique(),data_plot.prmc_size.unique()):
#     ax.set_title('beta: %.2f prmc_size: %.2f'%(beta,prmc_size),y=0.7)
plt.subplots_adjust(hspace = 0.05, wspace = 0.05)
plot.fig.suptitle('LD')
plot.savefig(local_path + "data_plot_exp_" + str(exp_number) + "_LD_2_beta_ifr_" + str(observe_index) + '_' + str(loci_3_str) + "_" + str(allele_3_str) + ".png", dpi=300)
plt.close()

plot = sns.relplot(data = data_plot, 
            x = 'year',
            y = 'ld',
            col = 'ifr',
            row = 'beta',
            hue = 'prmc_size',
            # style = "prmc_size",
            kind = "line",
            ci = 'sd',
            palette=sns.color_palette("husl",len(data_plot.prmc_size.unique()))[:len(data_plot.prmc_size.unique())],
            # height = a4_dims[1], aspect = 1.5
            )

# plot.set(xlim=(0, 30))
plot.set(ylim=(-0.025, 0.025))
# plot.set(xticks=range(0,30,5))
plot.set(yticks=np.arange(-0.025,0.025,0.0125))
# for ax,beta,prmc_size in zip(plot.axes.flat,data_plot.beta.unique(),data_plot.prmc_size.unique()):
#     ax.set_title('beta: %.2f prmc_size: %.2f'%(beta,prmc_size),y=0.7)
plt.subplots_adjust(hspace = 0.05, wspace = 0.05)
plot.fig.suptitle('LD')
plot.savefig(local_path + "data_plot_exp_" + str(exp_number) + "_LD_2_beta_ifr_" + str(observe_index) + '_' + str(loci_3_str) + "_" + str(allele_3_str) + "_detail.png", dpi=300)
plt.close()

plot = sns.relplot(data = data_plot, 
            x = 'year',
            y = 'ld-ij',
            col = 'ifr',
            row = 'beta',
            hue = 'prmc_size',
            # style = "prmc_size",
            kind = "line",
            ci = 'sd',
            palette=sns.color_palette("husl",len(data_plot.ifr.unique()))[:len(data_plot.ifr.unique())],
            # height = a4_dims[1], aspect = 1.5
            )

# plot.set(xlim=(0, 30))
# plot.set(ylim=(np.min(data_plot['ld']), np.max(data_plot['ld'])))
# plot.set(xticks=range(0,30,5))
# plot.set(yticks=np.arange(np.min(data_plot['ld']), np.max(data_plot['ld']),0.5))
plt.subplots_adjust(hspace = 0.05, wspace = 0.05)
plot.fig.suptitle('LD-IJ')
plot.savefig(local_path + "data_plot_exp_" + str(exp_number) + "_LD_2_beta_ifr_" + str(observe_index) + '_' + str(loci_3_str) + "_" + str(allele_3_str) + "-IJ.png", dpi=300)
plt.close()

plot = sns.relplot(data = data_plot, 
            x = 'year',
            y = 'ld-jk',
            col = 'ifr',
            row = 'beta',
            hue = 'prmc_size',
            # style = "prmc_size",
            kind = "line",
            ci = 'sd',
            palette=sns.color_palette("husl",len(data_plot.ifr.unique()))[:len(data_plot.ifr.unique())],
            # height = a4_dims[1], aspect = 1.5
            )

# plot.set(xlim=(0, 30))
# plot.set(ylim=(np.min(data_plot['ld']), np.max(data_plot['ld'])))
# plot.set(xticks=range(0,30,5))
# plot.set(yticks=np.arange(np.min(data_plot['ld']), np.max(data_plot['ld']),0.5))
plt.subplots_adjust(hspace = 0.05, wspace = 0.05)
plot.fig.suptitle('LD-JK')
plot.savefig(local_path + "data_plot_exp_" + str(exp_number) + "_LD_2_beta_ifr_" + str(observe_index) + '_' + str(loci_3_str) + "_" + str(allele_3_str) + "-JK.png", dpi=300)
plt.close()

plot = sns.relplot(data = data_plot, 
            x = 'year',
            y = 'ld-ik',
            col = 'ifr',
            row = 'beta',
            hue = 'prmc_size',
            # style = "prmc_size",
            kind = "line",
            ci = 'sd',
            palette=sns.color_palette("husl",len(data_plot.ifr.unique()))[:len(data_plot.ifr.unique())],
            # height = a4_dims[1], aspect = 1.5
            )

# plot.set(xlim=(0, 30))
# plot.set(ylim=(np.min(data_plot['ld']), np.max(data_plot['ld'])))
# plot.set(xticks=range(0,30,5))
# plot.set(yticks=np.arange(np.min(data_plot['ld']), np.max(data_plot['ld']),0.5))
plt.subplots_adjust(hspace = 0.1, wspace = 0.1) 
plot.fig.suptitle('LD-IK')
plot.savefig(local_path + "data_plot_exp_" + str(exp_number) + "_LD_2_beta_ifr_" + str(observe_index) + '_' + str(loci_3_str) + "_" + str(allele_3_str) + "-IK.png", dpi=300)
plt.close()

plot = sns.relplot(data = data_plot, 
            x = 'year',
            y = 'ld-ijk',
            col = 'ifr',
            row = 'beta',
            hue = 'prmc_size',
            # style = "prmc_size",
            kind = "line",
            ci = 'sd',
            palette=sns.color_palette("husl",len(data_plot.ifr.unique()))[:len(data_plot.ifr.unique())],
            # height = a4_dims[1], aspect = 1.5
            )

# plot.set(xlim=(0, 30))
# plot.set(ylim=(np.min(data_plot['ld']), np.max(data_plot['ld'])))
# plot.set(xticks=range(0,30,5))
# plot.set(yticks=np.arange(np.min(data_plot['ld']), np.max(data_plot['ld']),0.5))
plt.subplots_adjust(hspace = 0.05, wspace = 0.05)
plot.fig.suptitle('LD-IJK')

plot.savefig(local_path + "data_plot_exp_" + str(exp_number) + "_LD_2_beta_ifr_" + str(observe_index) + '_' + str(loci_3_str) + "_" + str(allele_3_str) + "-IJK.png", dpi=300)
plt.close()


#%%
plot = sns.relplot(data = data_plot, 
            x = 'year',
            y = 'ld',
            col = 'prmc_size',
            row = 'beta',
            hue = 'ifr',
            # style = "ifr",
            kind = "line",
            ci = 'sd',
            palette=sns.color_palette("husl",len(data_plot.ifr.unique()))[:len(data_plot.ifr.unique())],
            # height = a4_dims[1], aspect = 1.5
            )

# plot.set(xlim=(0, 30))
# plot.set(ylim=(-0.025, 0.025))
# plot.set(xticks=range(0,30,5))
# plot.set(yticks=np.arange(-0.025,0.025,0.0125))
# plot.set(yticks=np.arange(np.min(data_plot['ld']), np.max(data_plot['ld']),0.5))
for ax,beta,prmc_size in zip(plot.axes.flat,data_plot.beta.unique(),data_plot.prmc_size.unique()):
    ax.set_title('beta: %.2f prmc_size: %.2f'%(beta,prmc_size),y=0.7)
plt.subplots_adjust(hspace = 0.05, wspace = 0.05)
plot.fig.suptitle('LD')
plot.savefig(local_path + "data_plot_exp_" + str(exp_number) + "_LD_2_beta_prmc_size_" + str(observe_index) + '_' + str(loci_3_str) + "_" + str(allele_3_str) + ".png", dpi=300)
plt.close()

plot = sns.relplot(data = data_plot, 
            x = 'year',
            y = 'ld',
            col = 'prmc_size',
            row = 'beta',
            hue = 'ifr',
            # style = "ifr",
            kind = "line",
            ci = 'sd',
            palette=sns.color_palette("husl",len(data_plot.ifr.unique()))[:len(data_plot.ifr.unique())],
            # height = a4_dims[1], aspect = 1.5
            )

# plot.set(xlim=(0, 30))
plot.set(ylim=(-0.025, 0.025))
# plot.set(xticks=range(0,30,5))
plot.set(yticks=np.arange(-0.025,0.025,0.0125))
# plot.set(yticks=np.arange(np.min(data_plot['ld']), np.max(data_plot['ld']),0.5))
for ax,beta,prmc_size in zip(plot.axes.flat,data_plot.beta.unique(),data_plot.prmc_size.unique()):
    ax.set_title('beta: %.2f prmc_size: %.2f'%(beta,prmc_size),y=0.7)
plt.subplots_adjust(hspace = 0.05, wspace = 0.05)
plot.fig.suptitle('LD')
plot.savefig(local_path + "data_plot_exp_" + str(exp_number) + "_LD_2_beta_prmc_size_" + str(observe_index) + '_' + str(loci_3_str) + "_" + str(allele_3_str) + "_detail.png", dpi=300)
plt.close()

plot = sns.relplot(data = data_plot, 
            x = 'year',
            y = 'ld-ij',
            col = 'prmc_size',
            row = 'beta',
            hue = 'ifr',
            # style = "ifr",
            kind = "line",
            ci = 'sd',
            palette=sns.color_palette("husl",len(data_plot.ifr.unique()))[:len(data_plot.ifr.unique())],
            # height = a4_dims[1], aspect = 1.5
            )

# plot.set(xlim=(0, 30))
# plot.set(ylim=(np.min(data_plot['ld']), np.max(data_plot['ld'])))
# plot.set(xticks=range(0,30,5))
# plot.set(yticks=np.arange(np.min(data_plot['ld']), np.max(data_plot['ld']),0.5))
plt.subplots_adjust(hspace = 0.05, wspace = 0.05)
plot.fig.suptitle('LD-IJ')
plot.savefig(local_path + "data_plot_exp_" + str(exp_number) + "_LD_2_beta_prmc_size_" + str(observe_index) + '_' + str(loci_3_str) + "_" + str(allele_3_str) + "-IJ.png", dpi=300)
plt.close()

plot = sns.relplot(data = data_plot, 
            x = 'year',
            y = 'ld-jk',
            col = 'prmc_size',
            row = 'beta',
            hue = 'ifr',
            # style = "ifr",
            kind = "line",
            ci = 'sd',
            palette=sns.color_palette("husl",len(data_plot.ifr.unique()))[:len(data_plot.ifr.unique())],
            # height = a4_dims[1], aspect = 1.5
            )

# plot.set(xlim=(0, 30))
# plot.set(ylim=(np.min(data_plot['ld']), np.max(data_plot['ld'])))
# plot.set(xticks=range(0,30,5))
# plot.set(yticks=np.arange(np.min(data_plot['ld']), np.max(data_plot['ld']),0.5))
plt.subplots_adjust(hspace = 0.05, wspace = 0.05)
plot.fig.suptitle('LD-JK')
plot.savefig(local_path + "data_plot_exp_" + str(exp_number) + "_LD_2_beta_prmc_size_" + str(observe_index) + '_' + str(loci_3_str) + "_" + str(allele_3_str) + "-JK.png", dpi=300)
plt.close()

plot = sns.relplot(data = data_plot, 
            x = 'year',
            y = 'ld-ik',
            col = 'prmc_size',
            row = 'beta',
            hue = 'ifr',
            # style = "ifr",
            kind = "line",
            ci = 'sd',
            palette=sns.color_palette("husl",len(data_plot.ifr.unique()))[:len(data_plot.ifr.unique())],
            # height = a4_dims[1], aspect = 1.5
            )

# plot.set(xlim=(0, 30))
# plot.set(ylim=(np.min(data_plot['ld']), np.max(data_plot['ld'])))
# plot.set(xticks=range(0,30,5))
# plot.set(yticks=np.arange(np.min(data_plot['ld']), np.max(data_plot['ld']),0.5))
plt.subplots_adjust(hspace = 0.1, wspace = 0.1) 
plot.fig.suptitle('LD-IK')
plot.savefig(local_path + "data_plot_exp_" + str(exp_number) + "_LD_2_beta_prmc_size_" + str(observe_index) + '_' + str(loci_3_str) + "_" + str(allele_3_str) + "-IK.png", dpi=300)
plt.close()

plot = sns.relplot(data = data_plot, 
            x = 'year',
            y = 'ld-ijk',
            col = 'prmc_size',
            row = 'beta',
            hue = 'ifr',
            # style = "ifr",
            kind = "line",
            ci = 'sd',
            palette=sns.color_palette("husl",len(data_plot.ifr.unique()))[:len(data_plot.ifr.unique())],
            # height = a4_dims[1], aspect = 1.5
            )

# plot.set(xlim=(0, 30))
# plot.set(ylim=(np.min(data_plot['ld']), np.max(data_plot['ld'])))
# plot.set(xticks=range(0,30,5))
# plot.set(yticks=np.arange(np.min(data_plot['ld']), np.max(data_plot['ld']),0.5))
plt.subplots_adjust(hspace = 0.05, wspace = 0.05)
plot.fig.suptitle('LD-IJK')

plot.savefig(local_path + "data_plot_exp_" + str(exp_number) + "_LD_2_beta_prmc_size_" + str(observe_index) + '_' + str(loci_3_str) + "_" + str(allele_3_str) + "-IJK.png", dpi=300)
plt.close()

#%%
import os
import re
import pandas as pd
import numpy as np
import math
import seaborn as sns

a4_dims = (13, 8.27)

data_plot = pd.read_csv(local_path + "data_plot_exp_" + str(exp_number) + "_LD_2.csv")

data_plot_melt = data_plot.melt(id_vars=['beta', 'mutation_mask', 'prmc_size', 'ifr','month','year'], var_name='genotypes', value_name='freq')

plot = sns.relplot(data = data_plot_melt, 
            x = 'year',
            y = 'freq',
            # col = 'prmc_size',
            # row = 'beta',
            hue = 'genotypes',
            # style = "genotypes",
            kind = "line",
            ci = 'sd',
            palette=sns.color_palette("husl",len(data_plot_melt.genotypes.unique()))[:len(data_plot_melt.genotypes.unique())],
            height = a4_dims[1], aspect = 1.5
            )

plot.fig.subplots_adjust(bottom=0.1)
plt.subplots_adjust(hspace = 0.1, wspace = 0.1) 
# sns.move_legend(plot, "lower center", ncol = 4)

plot.savefig(local_path + "data_plot_exp_" + str(exp_number) + "_freq_all.png", dpi=300)    

#%%
import os
import re
import pandas as pd
import numpy as np
import math
import seaborn as sns

a4_dims = (15, 8.27)

data_plot = pd.read_csv(local_path + "data_plot_exp_" + str(exp_number) + "_LD_2.csv")

data_plot_melt = data_plot.melt(id_vars=['beta', 'mutation_mask', 'prmc_size', 'ifr','month','year'], var_name='genotypes', value_name='freq')

plot = sns.relplot(data = data_plot_melt, 
            x = 'year',
            y = 'freq',
            col = 'ifr',
            row = 'beta',
            hue = 'genotypes',
            # style = "genotypes",
            kind = "line",
            ci = 'sd',
            palette = sns.color_palette("husl",len(data_plot_melt.genotypes.unique()))[:len(data_plot_melt.genotypes.unique())],
            height = a4_dims[1], aspect = 1.5
            )

plot.fig.subplots_adjust(bottom=0.1)
plt.subplots_adjust(hspace = 0.1, wspace = 0.1) 
sns.move_legend(plot, "lower center", ncol = 6)

plot.savefig(local_path + "data_plot_exp_" + str(exp_number) + "_freq_split.png", dpi=300)            