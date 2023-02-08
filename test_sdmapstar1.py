# -*- coding: utf-8 -*-

# Contributors:
#    Paco Mora Caselles <pacomoracaselles@gmail.com>

"""Tests of the functionality contained in the file 'algorithms/sdmapstar.py'.
"""

from pandas import DataFrame
from subgroups.algorithms.individual_subgroups.nominal_target.sdmapstar import SDMapStar
from subgroups.quality_measures.wracc import WRAcc
from subgroups.quality_measures.wracc_optimistic_estimate_1 import WRAccOptimisticEstimate1
from subgroups.quality_measures.qg import Qg
from subgroups.exceptions import InconsistentMethodParametersError, DatasetAttributeTypeError, ParameterNotFoundError
from subgroups.data_structures.fp_tree_for_sdmap import FPTreeForSDMap
from subgroups.core.subgroup import Subgroup
from os import remove
import unittest

df = DataFrame({"a1" : ["a","b","c","c"], "a2" : ["q","q","s","q"], "a3" : ["f","g","h","k"], "class" : ["n","y","n","y"]})
target = ("class", "y")
# IMPORTANT: WRAcc quality measure is defined between -1 and 1.
sdmap = SDMapStar(WRAcc(), WRAccOptimisticEstimate1(),-1, minimum_n=0, write_results_in_file=True, file_path="./results.txt",num_subgroups=25)
sdmap.fit(df, target)
print(sdmap.visited_nodes)
print(sdmap.unselected_subgroups)
print(sdmap.conditional_pruned_branches) #Problema aquí, ver duda 3 del txt
