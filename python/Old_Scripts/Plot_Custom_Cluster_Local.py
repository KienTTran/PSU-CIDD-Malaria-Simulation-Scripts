# -*- coding: utf-8 -*-
"""
Created on Fri Jul 30 14:26:57 2021

@author: ktt5121
"""

import pandas as pd
import seaborn as sns
import matplotlib
import matplotlib.pyplot as plt
import math

data_raw = pd.read_csv('../analysis/local/monthly_custom_data_0.txt')

#data_raw['Calendar']

fig = plt.figure(figsize=(20,10))
fig.subplots_adjust(hspace=0.5)

#sns.set(rc={'figure.figsize':(11.7,8.27)})
#sns.lineplot(data=data_raw.reset_index(),
#             x='Calendar',
#             y='MonthlyTreatmentFailure0',
#             )

Total_Loc = 1;

#  subplot #1
plt.subplot(221)
#plt.title('subplot: 241')
for i in range(Total_Loc):
    sns.lineplot(data = data_raw, x='Calendar',y='Positive'+str(i))

#  subplot #2
plt.subplot(222)
#plt.title('subplot: 242')
for i in range(Total_Loc):
    sns.lineplot(data = data_raw, x='Calendar',y='Prevalence'+str(i))

# #  subplot #3
# plt.subplot(423)
# #plt.title('subplot: 243')
# for i in range(Total_Loc):
#     sns.lineplot(data = data_raw, x='Calendar',y='MonthlyClinicalEpisole'+str(i))

# #  subplot #4
# plt.subplot(424)
# #plt.title('subplot: 2,4,4')
# for i in range(Total_Loc):
#     sns.lineplot(data = data_raw, x='Calendar',y='MonthlyNewInfect'+str(i))

# #  subplot #5
# plt.subplot(425)
# #plt.title('subplot: 2,4,5')
# for i in range(Total_Loc):
#     sns.lineplot(data = data_raw, x='Calendar',y='MonthlyTreatment'+str(i))


# #  subplot #6
# plt.subplot(426)
# #plt.title('subplot: 2,4,6')
# for i in range(Total_Loc):
#     sns.lineplot(data = data_raw, x='Calendar',y='MonthlyTreatmentFailure'+str(i))


#  subplot #7
plt.subplot(223)
#plt.title('subplot: 2,4,7')
for i in range(Total_Loc):
    sns.scatterplot(data = data_raw, x='EIR'+str(i),y='Prevalence'+str(i))


#  subplot #8
plt.subplot(224)
#plt.title('subplot: 2,4,8')
for i in range(Total_Loc):
    sns.scatterplot(data = data_raw, x='EIRLog10'+str(i),y='Prevalence'+str(i))
    
plt.legend(labels=['0','1','2','3'])
plt.show()