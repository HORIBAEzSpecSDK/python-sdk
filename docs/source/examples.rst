========
Examples
========

Before you start
================

0. (Optional but recommended) Work in a virtual environment:

   Navigate to the (empty) project folder you want to work and run:

   .. code:: bash

     python -m venv .

   Activate the virtual environment:

   .. tip::
     *Windows*

     .. code:: powershell

       .\Scripts\activate


     *Unix*

     .. code:: bash

        source ./bin/activate

   *Note: do deactivate it, simply run* :code:`deactivate`.


1. Install the sdk:

   .. code:: bash

     pip install horiba-sdk

   or install with `Poetry`

   .. code:: bash

     poetry add horiba-sdk


Center Scan
===========

.. image:: ./images/python_first_steps.gif
  :align: center


The center scan scans at/around a given wavelength and displays the scanned intensity.

1. Create a file named :code:`center_scan.py` and copy-paste the content of
   `examples/asynchronous_examples/center_scan.py <https://github.com/HORIBAEzSpecSDK/python-sdk/blob/main/examples/asynchronous_examples/center_scan.py>`_

2. Install the required library for plotting the graph:

   .. code:: bash

     pip install matplotlib numpy

   or install with `Poetry`

   .. code:: bash

     poetry add matplotlib numpy

3. Run the example with:

   .. code:: bash

     python center_scan.py
