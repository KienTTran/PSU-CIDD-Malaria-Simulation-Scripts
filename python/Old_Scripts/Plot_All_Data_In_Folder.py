# -*- coding: utf-8 -*-
"""
Created on Sat Dec 25 12:42:28 2021

@author: kient
"""

from glob import glob
import os
from Plot_Simulations import plot_rep_from_file

# path = 'D:/plot/Nguyen/'
# path = 'D:/plot/2007_2017_2067_2167/'
# path = 'D:/plot/2037_2137/'
# path = 'D:/plot/2037_2137/parasite/'
# path = 'D:/plot/2037_2137/prmc/'
# path = 'D:/plot/local/'
# path = 'D:/plot/parasite_id/100K'
path = 'D:/plot/parasite_id/10K'
# path = 'D:/plot/prmc/'
keywords = [
            "Daily_PG",
            # "Daily_PRMC",
            # "Single_",
            # "_4000_",
            "_0.19_0.15",
            # "_2037_",
            # "_2537_",
            ]
rep_files = []
    
for root, folders, files in os.walk(path, topdown=False):
    for file in files:
        if file.endswith(".txt") and all(x in file for x in keywords):
            rep_files.append(os.path.join(root, file))


for rep_file in rep_files:
    plot_rep_from_file(rep_file,5)