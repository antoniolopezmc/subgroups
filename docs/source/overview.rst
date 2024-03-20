********
Overview
********

``subgroups`` is a public, accessible and open-source python library created to work with the Subgroup Discovery (SD) technique. This library implements the necessary components related to the SD technique and contains a collection of SD algorithms and other data analysis utilities.

----------------------------
Subgroup Discovery technique
----------------------------

Subgroup Discovery [`1`_] (SD) is a supervised machine learning (ML) technique that is widely used for descriptive and exploratory data analysis and whose main purpose is to mine a set of relations (denominated as *subgroups*) between attributes from a dataset with respect to a target attribute of interest.

One key aspect of this technique is the assessment of the quality of a subgroup extracted by an SD algorithm. For that, there is a wide variety of metrics (called *quality measures*). A quality measure is, in general, a function that assigns one numeric value to a subgroup according to certain specific properties [`2`_]. 

----------
Motivation
----------

Despite the utility of the SD technique and the great variety of SD algorithms that appear in literature, few implementations are available for scientists, researchers and developers. Present-day data scientists and ML researchers often depend on highly reliable libraries to test and compare state-of-the-art algorithms such as the classical ML tool Weka, scikit-learn, or Keras or PyTorch in the Deep Learning area. This is not the case in the SD field, in which no community supports the few available libraries.

The aforementioned disadvantages signify that it is necessary to use different libraries and tools when working with different SD algorithms and that there is no single reference library that implements and brings together a large number of SD algorithms, not even the most popular ones.

Therefore, it is necessary to have a complete library available that implements the most popular algorithms in a faithful form with respect to the original definition without adding modifications, along with a complete documentation of use with different examples. This is precisely the main motivation behind the development of this library.

----------
Objectives
----------

-------------------
Who uses subgroups?
-------------------

The potential users for ``subgroups`` are scientists, researchers, developers and, in general, all those who wish to work with the SD technique.

--------------
General design
--------------

-------------
Free software
-------------


.. _`1`: https://doi.org/10.1002/widm.1144
.. _`2`: https://www.mdpi.com/1999-4893/16/6/274
