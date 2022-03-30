# -*- coding: utf-8 -*-
"""
Created on Tue Jan  4 22:35:31 2022

@author: kient
"""

from Read_Simulations import read_simulations
from Plot_Simulations_Split_Rows import plot_simulations

plot_keywords = [
            "Daily_PG",
            # "Daily_PRMC",
            # "Single_",
            # "_1M_800_",
            # "_0.99_0.3_",
            # "_0.99_0.6_",
            # "_2007_",
            # "_2017_",
            # "_2027_",
            # "_2037_",
            ]
start_year = 2007
# end_year = 2017
end_year = 2027
# end_year = 2047
# display = "Year"
display = "Month"
# display = "Day"
year_interval = 1
month_interval = 12
day_interval = 90

# local_path = "D:/plot/Simulations/"
# local_path = "D:/plot/parasite_id/10K/"
# local_path = "D:/plot/parasite_id/100K/"
# local_path = "D:/plot/parasite_id/new/"
# local_path = "D:/plot/all/parasite_id/"
# local_path = "D:/plot/all/Nguyen/"
# local_path = "D:/plot/4000/"
# local_path = "D:/plot/new/"
# local_path = "D:/plot/new/250K_500K_1M/"
# local_path = "D:/plot/new/1M/"
# local_path = "D:/plot/new/1M/Parasite"
# local_path = "D:/plot/new/1M/PRMC"
# local_path = "D:/plot/new/Test/Normal"
# local_path = "D:/plot/new/Test/PRMC"
# local_path = "D:/plot/new/1M/Test1/"
# local_path = "D:/plot/new/1M/Test/Parasite"
local_path = "D:/plot/new/1M/Test/PRMC"
plot_delay = 2

def main():    
    print("Reading simulations")   
    simulations = read_simulations(local_path, plot_keywords, plot_delay)
    if simulations == []:
        print("No simulation available")
    else:
        print("Ploting simulations")
        for simulation in simulations:
            plot_simulations(simulation, plot_delay, start_year, end_year, display, year_interval, month_interval, day_interval)  

if __name__ == "__main__":
    main()
