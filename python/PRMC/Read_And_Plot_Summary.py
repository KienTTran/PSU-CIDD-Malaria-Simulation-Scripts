# -*- coding: utf-8 -*-
"""
Created on Tue Apr 19 21:02:18 2022

@author: kient
"""
import os
import re
import pandas as pd
import numpy as np
import math

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

n_run = 10

data = []

for index,config in enumerate(configs):    
    for run in range(n_run):
        # print(run)
        filename = "summary_%d.txt"%(run + index*1000)
        # print(filename)        
        kappa = re.findall("\d+\.\d+",config)[0]
        z = re.findall("\d+\.\d+",config)[1]
        beta = re.findall("\d+\.\d+",config)[2]
        # print(beta,ifr)        
        file_path = os.path.join(local_path, filename)
        try:
            csv = pd.read_csv(file_path,sep='\t',header=None,index_col=None)
            row = csv.iloc[0,[4,6] + [*range(13,73)]]            
            r = row.to_list()
            r.append((float)(kappa))
            r.append((float)(z))
            r.append((float)(beta))
            data.append(r)        
        except Exception as e:
            print(filename + " error reading " + str(e))
            
data_plot = pd.DataFrame(data)
data_plot.columns = ["eir","pfpr",*["age"+str(x) for x in range(60)],"kappa","z","beta"]

#data_plot["eir_log10"] = math.log10(data_plot.eir)
# data_plot.to_csv("data.csv",index=False)
#%%
import seaborn as sns
from matplotlib import pyplot as plt
import math

kappas = [0.1,0.5,1.0,2,4]
data_plot_by_kappa = []

for kappa in kappas:
    data_plot_by_kappa.append(data_plot[data_plot.kappa == kappa])
    
fig, axes = plt.subplots(3,3,sharex=True,sharey=True, squeeze=True)
for index,data_by_kappa in enumerate(data_plot_by_kappa):
    # data_by_kappa_plot = data_by_kappa[(data_by_kappa.eir > 19) & (data_by_kappa.eir < 20)]
    r = index//3
    c = index % 3
    sns.scatterplot(data=data_by_kappa,x="eir",y="age2",hue="z", ax=axes[r,c])
    