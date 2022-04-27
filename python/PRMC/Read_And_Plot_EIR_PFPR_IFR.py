# -*- coding: utf-8 -*-
"""
Created on Tue Apr  5 11:04:48 2022

@author: kient
"""
import os
import re
import pandas as pd
import numpy as np

local_path = "D:\\plot\\PRMC_2_Genotypes_Exp_5\\raw"

configs = [
"sim_prmc_pop_500000_beta_0.050_ifr_0.000_prmc_size_400.yml",
"sim_prmc_pop_500000_beta_0.050_ifr_0.040_prmc_size_400.yml",
"sim_prmc_pop_500000_beta_0.050_ifr_0.080_prmc_size_400.yml",
"sim_prmc_pop_500000_beta_0.050_ifr_0.120_prmc_size_400.yml",
"sim_prmc_pop_500000_beta_0.050_ifr_0.160_prmc_size_400.yml",
"sim_prmc_pop_500000_beta_0.050_ifr_0.200_prmc_size_400.yml",
"sim_prmc_pop_500000_beta_0.078_ifr_0.000_prmc_size_400.yml",
"sim_prmc_pop_500000_beta_0.078_ifr_0.040_prmc_size_400.yml",
"sim_prmc_pop_500000_beta_0.078_ifr_0.080_prmc_size_400.yml",
"sim_prmc_pop_500000_beta_0.078_ifr_0.120_prmc_size_400.yml",
"sim_prmc_pop_500000_beta_0.078_ifr_0.160_prmc_size_400.yml",
"sim_prmc_pop_500000_beta_0.078_ifr_0.200_prmc_size_400.yml",
"sim_prmc_pop_500000_beta_0.120_ifr_0.000_prmc_size_400.yml",
"sim_prmc_pop_500000_beta_0.120_ifr_0.040_prmc_size_400.yml",
"sim_prmc_pop_500000_beta_0.120_ifr_0.080_prmc_size_400.yml",
"sim_prmc_pop_500000_beta_0.120_ifr_0.120_prmc_size_400.yml",
"sim_prmc_pop_500000_beta_0.120_ifr_0.160_prmc_size_400.yml",
"sim_prmc_pop_500000_beta_0.120_ifr_0.200_prmc_size_400.yml",
"sim_prmc_pop_500000_beta_0.186_ifr_0.000_prmc_size_400.yml",
"sim_prmc_pop_500000_beta_0.186_ifr_0.040_prmc_size_400.yml",
"sim_prmc_pop_500000_beta_0.186_ifr_0.080_prmc_size_400.yml",
"sim_prmc_pop_500000_beta_0.186_ifr_0.120_prmc_size_400.yml",
"sim_prmc_pop_500000_beta_0.186_ifr_0.160_prmc_size_400.yml",
"sim_prmc_pop_500000_beta_0.186_ifr_0.200_prmc_size_400.yml",
"sim_prmc_pop_500000_beta_0.289_ifr_0.000_prmc_size_400.yml",
"sim_prmc_pop_500000_beta_0.289_ifr_0.040_prmc_size_400.yml",
"sim_prmc_pop_500000_beta_0.289_ifr_0.080_prmc_size_400.yml",
"sim_prmc_pop_500000_beta_0.289_ifr_0.120_prmc_size_400.yml",
"sim_prmc_pop_500000_beta_0.289_ifr_0.160_prmc_size_400.yml",
"sim_prmc_pop_500000_beta_0.289_ifr_0.200_prmc_size_400.yml",
"sim_prmc_pop_500000_beta_0.448_ifr_0.000_prmc_size_400.yml",
"sim_prmc_pop_500000_beta_0.448_ifr_0.040_prmc_size_400.yml",
"sim_prmc_pop_500000_beta_0.448_ifr_0.080_prmc_size_400.yml",
"sim_prmc_pop_500000_beta_0.448_ifr_0.120_prmc_size_400.yml",
"sim_prmc_pop_500000_beta_0.448_ifr_0.160_prmc_size_400.yml",
"sim_prmc_pop_500000_beta_0.448_ifr_0.200_prmc_size_400.yml",
"sim_prmc_pop_500000_beta_0.694_ifr_0.000_prmc_size_400.yml",
"sim_prmc_pop_500000_beta_0.694_ifr_0.040_prmc_size_400.yml",
"sim_prmc_pop_500000_beta_0.694_ifr_0.080_prmc_size_400.yml",
"sim_prmc_pop_500000_beta_0.694_ifr_0.120_prmc_size_400.yml",
"sim_prmc_pop_500000_beta_0.694_ifr_0.160_prmc_size_400.yml",
"sim_prmc_pop_500000_beta_0.694_ifr_0.200_prmc_size_400.yml",
"sim_prmc_pop_500000_beta_1.076_ifr_0.000_prmc_size_400.yml",
"sim_prmc_pop_500000_beta_1.076_ifr_0.040_prmc_size_400.yml",
"sim_prmc_pop_500000_beta_1.076_ifr_0.080_prmc_size_400.yml",
"sim_prmc_pop_500000_beta_1.076_ifr_0.120_prmc_size_400.yml",
"sim_prmc_pop_500000_beta_1.076_ifr_0.160_prmc_size_400.yml",
"sim_prmc_pop_500000_beta_1.076_ifr_0.200_prmc_size_400.yml",
"sim_prmc_pop_500000_beta_1.668_ifr_0.000_prmc_size_400.yml",
"sim_prmc_pop_500000_beta_1.668_ifr_0.040_prmc_size_400.yml",
"sim_prmc_pop_500000_beta_1.668_ifr_0.080_prmc_size_400.yml",
"sim_prmc_pop_500000_beta_1.668_ifr_0.120_prmc_size_400.yml",
"sim_prmc_pop_500000_beta_1.668_ifr_0.160_prmc_size_400.yml",
"sim_prmc_pop_500000_beta_1.668_ifr_0.200_prmc_size_400.yml",
"sim_prmc_pop_500000_beta_2.587_ifr_0.000_prmc_size_400.yml",
"sim_prmc_pop_500000_beta_2.587_ifr_0.040_prmc_size_400.yml",
"sim_prmc_pop_500000_beta_2.587_ifr_0.080_prmc_size_400.yml",
"sim_prmc_pop_500000_beta_2.587_ifr_0.120_prmc_size_400.yml",
"sim_prmc_pop_500000_beta_2.587_ifr_0.160_prmc_size_400.yml",
"sim_prmc_pop_500000_beta_2.587_ifr_0.200_prmc_size_400.yml",
"sim_prmc_pop_500000_beta_0.050_ifr_0.000_prmc_size_800.yml",
"sim_prmc_pop_500000_beta_0.050_ifr_0.040_prmc_size_800.yml",
"sim_prmc_pop_500000_beta_0.050_ifr_0.080_prmc_size_800.yml",
"sim_prmc_pop_500000_beta_0.050_ifr_0.120_prmc_size_800.yml",
"sim_prmc_pop_500000_beta_0.050_ifr_0.160_prmc_size_800.yml",
"sim_prmc_pop_500000_beta_0.050_ifr_0.200_prmc_size_800.yml",
"sim_prmc_pop_500000_beta_0.078_ifr_0.000_prmc_size_800.yml",
"sim_prmc_pop_500000_beta_0.078_ifr_0.040_prmc_size_800.yml",
"sim_prmc_pop_500000_beta_0.078_ifr_0.080_prmc_size_800.yml",
"sim_prmc_pop_500000_beta_0.078_ifr_0.120_prmc_size_800.yml",
"sim_prmc_pop_500000_beta_0.078_ifr_0.160_prmc_size_800.yml",
"sim_prmc_pop_500000_beta_0.078_ifr_0.200_prmc_size_800.yml",
"sim_prmc_pop_500000_beta_0.120_ifr_0.000_prmc_size_800.yml",
"sim_prmc_pop_500000_beta_0.120_ifr_0.040_prmc_size_800.yml",
"sim_prmc_pop_500000_beta_0.120_ifr_0.080_prmc_size_800.yml",
"sim_prmc_pop_500000_beta_0.120_ifr_0.120_prmc_size_800.yml",
"sim_prmc_pop_500000_beta_0.120_ifr_0.160_prmc_size_800.yml",
"sim_prmc_pop_500000_beta_0.120_ifr_0.200_prmc_size_800.yml",
"sim_prmc_pop_500000_beta_0.186_ifr_0.000_prmc_size_800.yml",
"sim_prmc_pop_500000_beta_0.186_ifr_0.040_prmc_size_800.yml",
"sim_prmc_pop_500000_beta_0.186_ifr_0.080_prmc_size_800.yml",
"sim_prmc_pop_500000_beta_0.186_ifr_0.120_prmc_size_800.yml",
"sim_prmc_pop_500000_beta_0.186_ifr_0.160_prmc_size_800.yml",
"sim_prmc_pop_500000_beta_0.186_ifr_0.200_prmc_size_800.yml",
"sim_prmc_pop_500000_beta_0.289_ifr_0.000_prmc_size_800.yml",
"sim_prmc_pop_500000_beta_0.289_ifr_0.040_prmc_size_800.yml",
"sim_prmc_pop_500000_beta_0.289_ifr_0.080_prmc_size_800.yml",
"sim_prmc_pop_500000_beta_0.289_ifr_0.120_prmc_size_800.yml",
"sim_prmc_pop_500000_beta_0.289_ifr_0.160_prmc_size_800.yml",
"sim_prmc_pop_500000_beta_0.289_ifr_0.200_prmc_size_800.yml",
"sim_prmc_pop_500000_beta_0.448_ifr_0.000_prmc_size_800.yml",
"sim_prmc_pop_500000_beta_0.448_ifr_0.040_prmc_size_800.yml",
"sim_prmc_pop_500000_beta_0.448_ifr_0.080_prmc_size_800.yml",
"sim_prmc_pop_500000_beta_0.448_ifr_0.120_prmc_size_800.yml",
"sim_prmc_pop_500000_beta_0.448_ifr_0.160_prmc_size_800.yml",
"sim_prmc_pop_500000_beta_0.448_ifr_0.200_prmc_size_800.yml",
"sim_prmc_pop_500000_beta_0.694_ifr_0.000_prmc_size_800.yml",
"sim_prmc_pop_500000_beta_0.694_ifr_0.040_prmc_size_800.yml",
"sim_prmc_pop_500000_beta_0.694_ifr_0.080_prmc_size_800.yml",
"sim_prmc_pop_500000_beta_0.694_ifr_0.120_prmc_size_800.yml",
"sim_prmc_pop_500000_beta_0.694_ifr_0.160_prmc_size_800.yml",
"sim_prmc_pop_500000_beta_0.694_ifr_0.200_prmc_size_800.yml",
"sim_prmc_pop_500000_beta_1.076_ifr_0.000_prmc_size_800.yml",
"sim_prmc_pop_500000_beta_1.076_ifr_0.040_prmc_size_800.yml",
"sim_prmc_pop_500000_beta_1.076_ifr_0.080_prmc_size_800.yml",
"sim_prmc_pop_500000_beta_1.076_ifr_0.120_prmc_size_800.yml",
"sim_prmc_pop_500000_beta_1.076_ifr_0.160_prmc_size_800.yml",
"sim_prmc_pop_500000_beta_1.076_ifr_0.200_prmc_size_800.yml",
"sim_prmc_pop_500000_beta_1.668_ifr_0.000_prmc_size_800.yml",
"sim_prmc_pop_500000_beta_1.668_ifr_0.040_prmc_size_800.yml",
"sim_prmc_pop_500000_beta_1.668_ifr_0.080_prmc_size_800.yml",
"sim_prmc_pop_500000_beta_1.668_ifr_0.120_prmc_size_800.yml",
"sim_prmc_pop_500000_beta_1.668_ifr_0.160_prmc_size_800.yml",
"sim_prmc_pop_500000_beta_1.668_ifr_0.200_prmc_size_800.yml",
"sim_prmc_pop_500000_beta_2.587_ifr_0.000_prmc_size_800.yml",
"sim_prmc_pop_500000_beta_2.587_ifr_0.040_prmc_size_800.yml",
"sim_prmc_pop_500000_beta_2.587_ifr_0.080_prmc_size_800.yml",
"sim_prmc_pop_500000_beta_2.587_ifr_0.120_prmc_size_800.yml",
"sim_prmc_pop_500000_beta_2.587_ifr_0.160_prmc_size_800.yml",
"sim_prmc_pop_500000_beta_2.587_ifr_0.200_prmc_size_800.yml",
"sim_prmc_pop_500000_beta_0.050_ifr_0.000_prmc_size_1200.yml",
"sim_prmc_pop_500000_beta_0.050_ifr_0.040_prmc_size_1200.yml",
"sim_prmc_pop_500000_beta_0.050_ifr_0.080_prmc_size_1200.yml",
"sim_prmc_pop_500000_beta_0.050_ifr_0.120_prmc_size_1200.yml",
"sim_prmc_pop_500000_beta_0.050_ifr_0.160_prmc_size_1200.yml",
"sim_prmc_pop_500000_beta_0.050_ifr_0.200_prmc_size_1200.yml",
"sim_prmc_pop_500000_beta_0.078_ifr_0.000_prmc_size_1200.yml",
"sim_prmc_pop_500000_beta_0.078_ifr_0.040_prmc_size_1200.yml",
"sim_prmc_pop_500000_beta_0.078_ifr_0.080_prmc_size_1200.yml",
"sim_prmc_pop_500000_beta_0.078_ifr_0.120_prmc_size_1200.yml",
"sim_prmc_pop_500000_beta_0.078_ifr_0.160_prmc_size_1200.yml",
"sim_prmc_pop_500000_beta_0.078_ifr_0.200_prmc_size_1200.yml",
"sim_prmc_pop_500000_beta_0.120_ifr_0.000_prmc_size_1200.yml",
"sim_prmc_pop_500000_beta_0.120_ifr_0.040_prmc_size_1200.yml",
"sim_prmc_pop_500000_beta_0.120_ifr_0.080_prmc_size_1200.yml",
"sim_prmc_pop_500000_beta_0.120_ifr_0.120_prmc_size_1200.yml",
"sim_prmc_pop_500000_beta_0.120_ifr_0.160_prmc_size_1200.yml",
"sim_prmc_pop_500000_beta_0.120_ifr_0.200_prmc_size_1200.yml",
"sim_prmc_pop_500000_beta_0.186_ifr_0.000_prmc_size_1200.yml",
"sim_prmc_pop_500000_beta_0.186_ifr_0.040_prmc_size_1200.yml",
"sim_prmc_pop_500000_beta_0.186_ifr_0.080_prmc_size_1200.yml",
"sim_prmc_pop_500000_beta_0.186_ifr_0.120_prmc_size_1200.yml",
"sim_prmc_pop_500000_beta_0.186_ifr_0.160_prmc_size_1200.yml",
"sim_prmc_pop_500000_beta_0.186_ifr_0.200_prmc_size_1200.yml",
"sim_prmc_pop_500000_beta_0.289_ifr_0.000_prmc_size_1200.yml",
"sim_prmc_pop_500000_beta_0.289_ifr_0.040_prmc_size_1200.yml",
"sim_prmc_pop_500000_beta_0.289_ifr_0.080_prmc_size_1200.yml",
"sim_prmc_pop_500000_beta_0.289_ifr_0.120_prmc_size_1200.yml",
"sim_prmc_pop_500000_beta_0.289_ifr_0.160_prmc_size_1200.yml",
"sim_prmc_pop_500000_beta_0.289_ifr_0.200_prmc_size_1200.yml",
"sim_prmc_pop_500000_beta_0.448_ifr_0.000_prmc_size_1200.yml",
"sim_prmc_pop_500000_beta_0.448_ifr_0.040_prmc_size_1200.yml",
"sim_prmc_pop_500000_beta_0.448_ifr_0.080_prmc_size_1200.yml",
"sim_prmc_pop_500000_beta_0.448_ifr_0.120_prmc_size_1200.yml",
"sim_prmc_pop_500000_beta_0.448_ifr_0.160_prmc_size_1200.yml",
"sim_prmc_pop_500000_beta_0.448_ifr_0.200_prmc_size_1200.yml",
"sim_prmc_pop_500000_beta_0.694_ifr_0.000_prmc_size_1200.yml",
"sim_prmc_pop_500000_beta_0.694_ifr_0.040_prmc_size_1200.yml",
"sim_prmc_pop_500000_beta_0.694_ifr_0.080_prmc_size_1200.yml",
"sim_prmc_pop_500000_beta_0.694_ifr_0.120_prmc_size_1200.yml",
"sim_prmc_pop_500000_beta_0.694_ifr_0.160_prmc_size_1200.yml",
"sim_prmc_pop_500000_beta_0.694_ifr_0.200_prmc_size_1200.yml",
"sim_prmc_pop_500000_beta_1.076_ifr_0.000_prmc_size_1200.yml",
"sim_prmc_pop_500000_beta_1.076_ifr_0.040_prmc_size_1200.yml",
"sim_prmc_pop_500000_beta_1.076_ifr_0.080_prmc_size_1200.yml",
"sim_prmc_pop_500000_beta_1.076_ifr_0.120_prmc_size_1200.yml",
"sim_prmc_pop_500000_beta_1.076_ifr_0.160_prmc_size_1200.yml",
"sim_prmc_pop_500000_beta_1.076_ifr_0.200_prmc_size_1200.yml",
"sim_prmc_pop_500000_beta_1.668_ifr_0.000_prmc_size_1200.yml",
"sim_prmc_pop_500000_beta_1.668_ifr_0.040_prmc_size_1200.yml",
"sim_prmc_pop_500000_beta_1.668_ifr_0.080_prmc_size_1200.yml",
"sim_prmc_pop_500000_beta_1.668_ifr_0.120_prmc_size_1200.yml",
"sim_prmc_pop_500000_beta_1.668_ifr_0.160_prmc_size_1200.yml",
"sim_prmc_pop_500000_beta_1.668_ifr_0.200_prmc_size_1200.yml",
"sim_prmc_pop_500000_beta_2.587_ifr_0.000_prmc_size_1200.yml",
"sim_prmc_pop_500000_beta_2.587_ifr_0.040_prmc_size_1200.yml",
"sim_prmc_pop_500000_beta_2.587_ifr_0.080_prmc_size_1200.yml",
"sim_prmc_pop_500000_beta_2.587_ifr_0.120_prmc_size_1200.yml",
"sim_prmc_pop_500000_beta_2.587_ifr_0.160_prmc_size_1200.yml",
"sim_prmc_pop_500000_beta_2.587_ifr_0.200_prmc_size_1200.yml",
"sim_prmc_pop_500000_beta_0.050_ifr_0.000_prmc_size_1600.yml",
"sim_prmc_pop_500000_beta_0.050_ifr_0.040_prmc_size_1600.yml",
"sim_prmc_pop_500000_beta_0.050_ifr_0.080_prmc_size_1600.yml",
"sim_prmc_pop_500000_beta_0.050_ifr_0.120_prmc_size_1600.yml",
"sim_prmc_pop_500000_beta_0.050_ifr_0.160_prmc_size_1600.yml",
"sim_prmc_pop_500000_beta_0.050_ifr_0.200_prmc_size_1600.yml",
"sim_prmc_pop_500000_beta_0.078_ifr_0.000_prmc_size_1600.yml",
"sim_prmc_pop_500000_beta_0.078_ifr_0.040_prmc_size_1600.yml",
"sim_prmc_pop_500000_beta_0.078_ifr_0.080_prmc_size_1600.yml",
"sim_prmc_pop_500000_beta_0.078_ifr_0.120_prmc_size_1600.yml",
"sim_prmc_pop_500000_beta_0.078_ifr_0.160_prmc_size_1600.yml",
"sim_prmc_pop_500000_beta_0.078_ifr_0.200_prmc_size_1600.yml",
"sim_prmc_pop_500000_beta_0.120_ifr_0.000_prmc_size_1600.yml",
"sim_prmc_pop_500000_beta_0.120_ifr_0.040_prmc_size_1600.yml",
"sim_prmc_pop_500000_beta_0.120_ifr_0.080_prmc_size_1600.yml",
"sim_prmc_pop_500000_beta_0.120_ifr_0.120_prmc_size_1600.yml",
"sim_prmc_pop_500000_beta_0.120_ifr_0.160_prmc_size_1600.yml",
"sim_prmc_pop_500000_beta_0.120_ifr_0.200_prmc_size_1600.yml",
"sim_prmc_pop_500000_beta_0.186_ifr_0.000_prmc_size_1600.yml",
"sim_prmc_pop_500000_beta_0.186_ifr_0.040_prmc_size_1600.yml",
"sim_prmc_pop_500000_beta_0.186_ifr_0.080_prmc_size_1600.yml",
"sim_prmc_pop_500000_beta_0.186_ifr_0.120_prmc_size_1600.yml",
"sim_prmc_pop_500000_beta_0.186_ifr_0.160_prmc_size_1600.yml",
"sim_prmc_pop_500000_beta_0.186_ifr_0.200_prmc_size_1600.yml",
"sim_prmc_pop_500000_beta_0.289_ifr_0.000_prmc_size_1600.yml",
"sim_prmc_pop_500000_beta_0.289_ifr_0.040_prmc_size_1600.yml",
"sim_prmc_pop_500000_beta_0.289_ifr_0.080_prmc_size_1600.yml",
"sim_prmc_pop_500000_beta_0.289_ifr_0.120_prmc_size_1600.yml",
"sim_prmc_pop_500000_beta_0.289_ifr_0.160_prmc_size_1600.yml",
"sim_prmc_pop_500000_beta_0.289_ifr_0.200_prmc_size_1600.yml",
"sim_prmc_pop_500000_beta_0.448_ifr_0.000_prmc_size_1600.yml",
"sim_prmc_pop_500000_beta_0.448_ifr_0.040_prmc_size_1600.yml",
"sim_prmc_pop_500000_beta_0.448_ifr_0.080_prmc_size_1600.yml",
"sim_prmc_pop_500000_beta_0.448_ifr_0.120_prmc_size_1600.yml",
"sim_prmc_pop_500000_beta_0.448_ifr_0.160_prmc_size_1600.yml",
"sim_prmc_pop_500000_beta_0.448_ifr_0.200_prmc_size_1600.yml",
"sim_prmc_pop_500000_beta_0.694_ifr_0.000_prmc_size_1600.yml",
"sim_prmc_pop_500000_beta_0.694_ifr_0.040_prmc_size_1600.yml",
"sim_prmc_pop_500000_beta_0.694_ifr_0.080_prmc_size_1600.yml",
"sim_prmc_pop_500000_beta_0.694_ifr_0.120_prmc_size_1600.yml",
"sim_prmc_pop_500000_beta_0.694_ifr_0.160_prmc_size_1600.yml",
"sim_prmc_pop_500000_beta_0.694_ifr_0.200_prmc_size_1600.yml",
"sim_prmc_pop_500000_beta_1.076_ifr_0.000_prmc_size_1600.yml",
"sim_prmc_pop_500000_beta_1.076_ifr_0.040_prmc_size_1600.yml",
"sim_prmc_pop_500000_beta_1.076_ifr_0.080_prmc_size_1600.yml",
"sim_prmc_pop_500000_beta_1.076_ifr_0.120_prmc_size_1600.yml",
"sim_prmc_pop_500000_beta_1.076_ifr_0.160_prmc_size_1600.yml",
"sim_prmc_pop_500000_beta_1.076_ifr_0.200_prmc_size_1600.yml",
"sim_prmc_pop_500000_beta_1.668_ifr_0.000_prmc_size_1600.yml",
"sim_prmc_pop_500000_beta_1.668_ifr_0.040_prmc_size_1600.yml",
"sim_prmc_pop_500000_beta_1.668_ifr_0.080_prmc_size_1600.yml",
"sim_prmc_pop_500000_beta_1.668_ifr_0.120_prmc_size_1600.yml",
"sim_prmc_pop_500000_beta_1.668_ifr_0.160_prmc_size_1600.yml",
"sim_prmc_pop_500000_beta_1.668_ifr_0.200_prmc_size_1600.yml",
"sim_prmc_pop_500000_beta_2.587_ifr_0.000_prmc_size_1600.yml",
"sim_prmc_pop_500000_beta_2.587_ifr_0.040_prmc_size_1600.yml",
"sim_prmc_pop_500000_beta_2.587_ifr_0.080_prmc_size_1600.yml",
"sim_prmc_pop_500000_beta_2.587_ifr_0.120_prmc_size_1600.yml",
"sim_prmc_pop_500000_beta_2.587_ifr_0.160_prmc_size_1600.yml",
"sim_prmc_pop_500000_beta_2.587_ifr_0.200_prmc_size_1600.yml"
]

n_run = 2

data = []

for index,config in enumerate(configs):
    # print(index,config)
    for run in range(n_run):
        # print(run)
        filename = "monthly_data_%d.txt"%(run + index*1000)
        # print(filename)
        beta = re.findall("\d+\.\d+",config)[0]
        ifr = re.findall("\d+\.\d+",config)[1]
        prmc_size = re.findall("\d+",config)[5]
        # print(beta,ifr)        
        file_path = os.path.join(local_path, filename)
        try:
            csv = pd.read_csv(file_path,sep='\t',header=None,index_col=None)
            row = csv.iloc[120,[10,12] + [*range(22,32)]]            
            r = row.to_list()
            r.append(120)
            r.append((float)(beta))
            r.append((float)(ifr))
            r.append((float)(prmc_size))
            data.append(r)
            row = csv.iloc[360,[10,12] + [*range(22,32)]]
            r = row.to_list()
            r.append(360)
            r.append((float)(beta))
            r.append((float)(ifr))
            r.append((float)(prmc_size))
            data.append(r)        
        except Exception as e:
            print(filename + " error reading " + str(e))
        
data_plot = pd.DataFrame(data)
data_plot.columns = ["eir","pfpr",*["moi"+str(x) for x in range(10)],"month","beta","ifr","prmc_size"]

sum_moi = data_plot[["moi"+str(x) for x in range(1,10)]].sum(axis=1)
for x in range(1,10):
    data_plot["moi"+str(x)] = data_plot["moi"+str(x)]/sum_moi   


#%%
import seaborn as sns
from matplotlib import pyplot as plt

plt.close("all")   
plot = sns.scatterplot(data=data_plot, x="eir", y="pfpr", hue="month") 
plot.set(xscale="log")
        
#%%
import seaborn as sns
from matplotlib import pyplot as plt
import math

g = sns.FacetGrid(data_plot, col="ifr", row="month")
g.map_dataframe(sns.scatterplot, x="eir", y ="pfpr", hue="prmc_size")

#%%
import seaborn as sns
from matplotlib import pyplot as plt
import math


# plt.close("all")

data_120 = data_plot[data_plot.month == 120]   
betas = data_120.beta.unique()
ifrs = data_120.ifr.unique()
sizes = data_120.prmc_size.unique()

fig, axes = plt.subplots(len(ifrs),len(betas),sharex=True,sharey=True)

for i_index,ifr in enumerate(ifrs):
    for b_index,beta in enumerate(betas):
        r = i_index
        c = b_index
        data_beta = data_120[((data_120.beta == beta) & (data_120.ifr == ifr))]
        data_moi = data_beta[["moi"+str(x) for x in range(1,10)]]
        data_moi.columns=[*range(1,10)]
        data_moi_melt = pd.melt(data_moi)
        data_moi_melt.columns = ["MOI","freq"]
        sns.boxplot(data=data_moi_melt,x="MOI",y="freq",ax=axes[r,c])
        
        eir_percentile = np.percentile(data_beta["eir"],[25,50,75])
        pfpr_percentile = np.percentile(data_beta["pfpr"],[25,50,75])
        
        if r < len(ifrs) - 1:
            axes[r,c].set_xlabel("")
        if c > 0:
            axes[r,c].set_ylabel("")
        
        axes[r,c].set_title("EIR: %.2f - PFPR: %.2f - IFR: %.2f"%(eir_percentile[1],pfpr_percentile[1],(float)(ifr)))
        axes[r,c].grid(True, axis='both')
#%%
import seaborn as sns
from matplotlib import pyplot as plt
import math


# plt.close("all")

data_360 = data_plot[data_plot.month == 360]   
betas = data_360.beta.unique()
ifrs = data_360.ifr.unique()
sizes = data_360.prmc_size.unique()

fig, axes = plt.subplots(len(ifrs),len(betas),sharex=True,sharey=True)

for i_index,ifr in enumerate(ifrs):
    for b_index,beta in enumerate(betas):
        r = i_index
        c = b_index
        data_beta = data_360[((data_360.beta == beta) & (data_360.ifr == ifr))]
        data_moi = data_beta[["moi"+str(x) for x in range(1,10)]]
        data_moi.columns=[*range(1,10)]
        data_moi_melt = pd.melt(data_moi)
        data_moi_melt.columns = ["MOI","freq"]
        sns.boxplot(data=data_moi_melt,x="MOI",y="freq",ax=axes[r,c])
        
        eir_percentile = np.percentile(data_beta["eir"],[25,50,75])
        pfpr_percentile = np.percentile(data_beta["pfpr"],[25,50,75])
        
        if r < len(ifrs) - 1:
            axes[r,c].set_xlabel("")
        if c > 0:
            axes[r,c].set_ylabel("")
        
        axes[r,c].set_title("EIR: %.2f - PFPR: %.2f - IFR: %.2f"%(eir_percentile[1],pfpr_percentile[1],(float)(ifr)))
        axes[r,c].grid(True, axis='both')
        
#%%
import seaborn as sns
from matplotlib import pyplot as plt
import math


# plt.close("all")

data_360 = data_plot[data_plot.month == 360]   
betas = data_360.beta.unique()
ifrs = data_360.ifr.unique()
sizes = data_360.prmc_size.unique()

fig, axes = plt.subplots(len(sizes),len(betas),sharex=True,sharey=True)

for i_index,p_size in enumerate(sizes):
    for b_index,beta in enumerate(betas):
        r = i_index
        c = b_index
        data_beta = data_360[((data_360.beta == beta) & (data_360.prmc_size == p_size))]
        data_moi = data_beta[["moi"+str(x) for x in range(1,10)]]
        data_moi.columns=[*range(1,10)]
        data_moi_melt = pd.melt(data_moi)
        data_moi_melt.columns = ["MOI","freq"]
        sns.boxplot(data=data_moi_melt,x="MOI",y="freq",ax=axes[r,c])
        
        eir_percentile = np.percentile(data_beta["eir"],[25,50,75])
        pfpr_percentile = np.percentile(data_beta["pfpr"],[25,50,75])
        
        if r < len(ifrs) - 1:
            axes[r,c].set_xlabel("")
        if c > 0:
            axes[r,c].set_ylabel("")
        
        axes[r,c].set_title("PFPR: %.2f - PRMC Size: %.2f"%(pfpr_percentile[1],(float)(p_size)))
        axes[r,c].grid(True, axis='both')