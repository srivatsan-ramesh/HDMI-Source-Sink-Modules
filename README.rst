
HDMI-Source-Sink-Modules
========================

.. image:: https://travis-ci.org/srivatsan-ramesh/HDMI-Source-Sink-Modules.svg?branch=master
    :target: https://travis-ci.org/srivatsan-ramesh/HDMI-Source-Sink-Modules
    :alt: Build Status
.. image:: https://landscape.io/github/srivatsan-ramesh/HDMI-Source-Sink-Modules/master/landscape.svg?style=flat
   :target: https://landscape.io/github/srivatsan-ramesh/HDMI-Source-Sink-Modules/master
   :alt: Code Health
.. image:: https://coveralls.io/repos/github/srivatsan-ramesh/HDMI-Source-Sink-Modules/badge.svg?branch=master
    :target: https://coveralls.io/github/srivatsan-ramesh/HDMI-Source-Sink-Modules?branch=master
    :alt: Coverage Status
.. image:: https://readthedocs.org/projects/hdmi-source-sink-modules/badge/?version=latest
    :target: http://hdmi-source-sink-modules.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status

Implementation of HDMI Source/Sink Modules in MyHDL (http://www.myhdl.org/). 
Xilinx application notes `xapp460 <http://www.xilinx.com/support/documentation/application_notes/xapp460.pdf>`_ and `xapp495 <http://www.xilinx.com/support/documentation/application_notes/xapp495_S6TMDS_Video_Interface.pdf>`_ were used as reference.

Requirements
------------

* Python 3.5
* MyHDL 1.0.dev0

Getting Started
---------------

Clone this repository to get started.

.. code-block:: bash

    git clone https://github.com/srivatsan-ramesh/HDMI-Source-Sink-Modules.git

The project requires MyHDL version 1.0dev. The version has not been released (yet) and needs to be installed manually.

.. code-block:: bash

    cd HDMI-Source-Sink-Modules/
    pip install -r requirements.txt

After the dependencies have been installed, install the project.

.. code-block:: bash

    python setup.py install


Running Tests
-------------

The tests can be run using pytest.

.. code-block:: bash

    cd tests/
    py.test


Using Models
------------

HDMI Source/Sink Models are non-convertible modules which can be used to simulate the behaviour of HDMI Source/Sink Modules.
To initialize the interfaces -

.. code-block:: python

    # Interfaces for Tx Model

    video_interface_tx = VideoInterface(clock)
    aux_interface_tx = AuxInterface(clock)
    hdmi_interface_tx = HDMIInterface(clock10x)

    # Interfaces for Rx Model

    video_interface_rx = VideoInterface(clock)
    aux_interface_rx = AuxInterface(clock)
    hdmi_interface_rx = HDMIInterface(clock10x)

Here the two signals clock signals are driven by the clock_driver() block.

.. code-block:: python

    driver = clock_driver(clock)

The 'clock10x' signal should have a frequency 10 times that of clock signal.

The models can be initialized as -

.. code-block:: python

    hdmi_tx_model = HDMITxModel(clock, reset,
                                video_interface_tx, aux_interface_tx, hdmi_interface_tx)
    hdmi_rx_model = HDMIRxModel(video_interface_rx, aux_interface_rx, hdmi_interface_rx)

To simulate their process make use of the process() block of the models.

.. code-block:: python

    hdmi_tx_inst = hdmi_tx_model.process()
    hdmi_rx_inst = hdmi_rx_model.process()
