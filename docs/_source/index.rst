.. neonutilities documentation master file, created by
   sphinx-quickstart on Sun Oct  9 20:37:50 2022.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

===========================
neonutilities Documentation
===========================

**neonutilities** is a Python package for accessing and downloading data from the National Ecological Observatory Network (NEON) API.

.. toctree::
   :maxdepth: 1
   :caption: Contents:

   API Reference<ref_api.rst>

..
	User Guide</user_guide/index>   

Install
-------

The easiest way to install ``neonutilities`` and its dependencies is with pip.

.. code:: bash

   conda activate myenv
   pip install git+https://github.com/arojas314/neonutilities.git


Capabilities
------------
Download and Read Data
^^^^^^^^^^^^^^^^^^^^^^

First, download some PAR data and save to a directory.

.. code-block:: python

   # Download PAR data
   import neonutilities as nu
   nu.api.download_data('DP1.00024.001', "HARV", start="2019-01", end="2019-02", download_folder="./data")

.. note::
   A complete listing of the products available are available at `here <https://data.neonscience.org/data-products/explore>`_.

There are methods to do the following:

* Download aerial observation platform (AOP) remote sensing data for a given area
* Download and read eddy covariance (EC) instrument data directly into a Pandas DataFrame

.. code-block:: python

   # Download AOP data
   nu.api.download_aop_files('DP1.30003.001','HARV','2019','./data/HARV_2019/lidar','./HARV_poly.shp') # Spatial data should be in local UTM zone!

.. code-block:: python

   # Download EC instrument data and read directly into dataframe
   par_data = nu.api.get_instrument_data("DP1.00024.001", "HARV", start="2020-01", end="2020-12", tmi = 30, outdir = "./NEON_PAR_HARV")



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
