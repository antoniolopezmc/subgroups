*********************
Extending the library
*********************

A key advantage of the ``subgroups`` python library is that it is easily extensible. Therefore, users can add new quality measures, data structures and algorithms.

After adding new functionality to the library, it is required to implement its corresponding tests in the ``tests`` folder in order to verify that this functionality is well-implemented and works properly.

============================
Adding a new quality measure
============================

This example use the WRAcc quality measure to show how to add a new quality measure to the library.

The first step is to create a python file in the ``quality_measures`` folder whose name is the name of the specific quality measure to implement, ``wracc.py`` in this case. Note that the file name is always in lowercase.

Then, the file content must be the following:

.. code-block:: python
    :linenos:

    """This file contains the implementation of the Weighted Relative Accuracy (WRAcc) quality measure.
    """

    from subgroups.quality_measures.quality_measure import QualityMeasure
    from subgroups.exceptions import SubgroupParameterNotFoundError

    # Python annotations.
    from typing import Union

    class WRAcc(QualityMeasure):
        """This class defines the Weighted Relative Accuracy (WRAcc) quality measure.
        """
        
        _singleton = None
        __slots__ = ()
        
        def __new__(cls) -> 'WRAcc':
            if WRAcc._singleton is None:
                WRAcc._singleton = object().__new__(cls)
            return WRAcc._singleton
        
        def compute(self, dict_of_parameters : dict[str, Union[int, float]]) -> float:
            """Method to compute the WRAcc quality measure (you can also call to the instance for this purpose).
            
            :param dict_of_parameters: python dictionary which contains all the necessary parameters used to compute this quality measure.
            :return: the computed value for the WRAcc quality measure.
            """
            if type(dict_of_parameters) is not dict:
                raise TypeError("The type of the parameter 'dict_of_parameters' must be 'dict'.")
            if (QualityMeasure.TRUE_POSITIVES not in dict_of_parameters):
                raise SubgroupParameterNotFoundError("The subgroup parameter 'tp' is not in 'dict_of_parameters'.")
            if (QualityMeasure.FALSE_POSITIVES not in dict_of_parameters):
                raise SubgroupParameterNotFoundError("The subgroup parameter 'fp' is not in 'dict_of_parameters'.")
            if (QualityMeasure.TRUE_POPULATION not in dict_of_parameters):
                raise SubgroupParameterNotFoundError("The subgroup parameter 'TP' is not in 'dict_of_parameters'.")
            if (QualityMeasure.FALSE_POPULATION not in dict_of_parameters):
                raise SubgroupParameterNotFoundError("The subgroup parameter 'FP' is not in 'dict_of_parameters'.")
            tp = dict_of_parameters[QualityMeasure.TRUE_POSITIVES]
            fp = dict_of_parameters[QualityMeasure.FALSE_POSITIVES]
            TP = dict_of_parameters[QualityMeasure.TRUE_POPULATION]
            FP = dict_of_parameters[QualityMeasure.FALSE_POPULATION]
            return ( (tp+fp) / (TP+FP) ) * ( ( tp / (tp+fp) ) - ( TP / (TP+FP) ) )
        
        def get_name(self) -> str:
            """Method to get the quality measure name (equal to the class name).
            """
            return "WRAcc"
        
        def optimistic_estimate_of(self) -> dict[str, QualityMeasure]:
            """Method to get a python dictionary with the quality measures of which this one is an optimistic estimate.
            
            :return: a python dictionary in which the keys are the quality measure names and the values are the instances of those quality measures.
            """
            return dict()
        
        def __call__(self, dict_of_parameters : dict[str, Union[int, float]]) -> float:
            """Compute the WRAcc quality measure.
            
            :param dict_of_parameters: python dictionary which contains all the needed parameters with which to compute this quality measure.
            :return: the computed value for the WRAcc quality measure.
            """
            return self.compute(dict_of_parameters)

This file contains only one class, which inherits from the ``QualityMeasure`` abstract class and whose name is the name of the specific quality measure to implement, WRAcc in this case. Since this class is a singleton, it contains a class attribute called ``_singleton`` and the ``__new__`` method as indicated in the previous code. At the same time, this class also overwrite the ``compute``, ``get_name``, ``optimistic_estimate_of`` and ``__call__`` methods.

After that, the last step is to add the following line in the ``quality_measures/__init__.py`` file:

.. code-block:: python

    from subgroups.quality_measures.wracc import WRAcc

===========================
Adding a new data structure
===========================

The first step is to create a python file in the ``data_structures`` folder whose name is the name of the specific data structure to implement. Remember that the file name is always in lowercase. The only implementation restriction for this file is to have only one class.

After that, using as an example the subgroup list data structure, the last step is to add the following line in the ``data_structures/__init__.py`` file:

.. code-block:: python

    from subgroups.data_structures.subgroup_list import SubgroupList

======================
Adding a new algorithm
======================

This example use the VLSD algorithm to show how to add a new algorithm to the library.

The first step is to create a python file either in the ``algorithms/subgroup_sets`` folder or in the ``algorithms/subgroup_lists`` folder depending on the algorithm type to implement. The file name is the name of the specific algorithm to implement, ``vlsd.py`` in this case. Note that the file name is always in lowercase.

This file contains only one class, which inherits from the ``Algorithm`` abstract class and whose name is the name of the specific algorithm to implement, ``VLSD`` in this case. At the same time, this class overwrites the ``fit`` method, whose definition is as follows:

.. code-block:: python

    def fit(self, pandas_dataframe : DataFrame, target : tuple[str, str]) -> None:

After that, the last step is to add the following line in the ``algorithms/__init__.py`` file:

.. code-block:: python

    from subgroups.algorithms.subgroup_sets.vlsd import VLSD
