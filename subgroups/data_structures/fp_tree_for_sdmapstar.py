# -*- coding: utf-8 -*-

# Contributors:
#    Paco Mora Caselles <pacomoracaselles@gmail.com>

"""This file contains the implementation of the FPTree data structure used in the SDMapStar algorithm.
"""

from subgroups.data_structures.fp_tree_node import FPTreeNode
from subgroups.core.selector import Selector
from subgroups.core.operator import Operator
from pandas import DataFrame
from numpy import size, sum
from subgroups.exceptions import InconsistentMethodParametersError
from subgroups.data_structures.fp_tree_for_sdmap import FPTreeForSDMap

# Python annotations.
from typing import Union

class FPTreeForSDMapStar(FPTreeForSDMap):
    """This class represents the FPTree data structure used in the SDMapStar algorithm.
    """

    def generate_conditional_fp_tree (self, list_of_selectors : list[Selector], minimum_tp : Union[int, None] = None, minimum_fp : Union[int, None] = None, minimum_n : Union[int, None] = None) -> 'FPTreeForSDMapStar':
        raise NotImplementedError("The conditional FP-tree generation is not implemented for the SDMapStar algorithm.")