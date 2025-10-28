.. rst headers guide
   ============= (H1)
   ------------- (H2)
   ^^^^^^^^^^^^^ (H3)
   """"""""""""" (H4)
   ~~~~~~~~~~~~~ (H5)


Usage Guide
===========

.. contents::
   :local:
   :depth: 2

.. _quickstart:

Quickstart
----------

Below is a quickstart guide to start using PyBA.

.. code-block:: python

   from pyba import Engine

   # If VertexAI
   agent = Engine(vertexai_project_id="", vertexai_server_location="")
   
   # If OpenAI
   agent = Engine(openai_api_key="")
   agent.sync_run("Go to twitter.com and search for 'cybersecurity news'")

.. _installation:

Installation
------------

You can install PyBA either from PyPI or from source.


.. _installation-pypi:

PyPI
^^^^^^^^^

.. code-block:: bash

   pip install py-browser-automation

.. _installation-source:

Source
^^^^^^^^^^^

.. code-block:: bash

   git clone https://github.com/fauvidoTechnologies/PyBrowserAutomation.git
   cd pyba
   pip install .

.. _detailed-guide:

Detailed Guide
--------------
