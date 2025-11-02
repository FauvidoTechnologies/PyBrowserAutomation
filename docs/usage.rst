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
   agent.sync_run("Go to twitter and search for 'cybersecurity news'")


or you can save the output from the automation to use later in your code:

.. code-block:: python

   from pyba import Engine

   # If OpenAI
   agent = Engine(openai_api_key="")
   output = agent.async_run(prompt="Login to my instagram and give me all the IDs present in my feed", automated_login_sites=["instagram"]) # More details on `automated_login_sites` later

   print(output)

You can run ``pyba`` in both **sync** and **async** modes depending on your use case. To run the **async** endpoint simply use ``.run()``

.. code-block:: python

   from pyba import Engine

   # If OpenAI
   agent = Engine(openai_api_key="")
   agent.run("Go to twitter and search for 'cybersecurity news'")

Enable local **logging** if you need

.. code-block:: python

   from pyba import Engine
   # If OpenAI
   agent = Engine(openai_api_key="", use_logger=True)
   agent.run("Go to twitter and search for 'cybersecurity news'")


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
^^^^^^^^^^

.. code-block:: bash

   git clone https://github.com/fauvidoTechnologies/PyBrowserAutomation.git
   cd pyba
   pip install .

.. _guide:

Guide
--------------

.. _dependency-management:

Dependency management
^^^^^^^^^^^^^^^^^^^^^

``pyba`` will automatically install playwright and other system dependencies. If they're already installed then it will skip the installation.

.. code-block:: python

   from pyba import Engine
   # If OpenAI
   agent = Engine(openai_api_key="", handle_dependencies=True)
   agent.run("Go to twitter and search for 'cybersecurity news'")

You can also install the dependencies manually

.. code-block:: bash

   playwright install-deps # Install dependencies
   playwright install # Install browsers 

.. _tracing:

Tracing
^^^^^^^

``pyba`` has support for playwright traceviewer by allowing you to enable tracing and generate a ``.zip`` file

.. code-block:: python

   from pyba import Engine
   # If OpenAI
   agent = Engine(openai_api_key="", use_logger=True, enable_tracing=True)
   agent.run("Go to twitter and search for 'cybersecurity news'")

You can optionally choose a directory to save the ``.zip`` file to.

.. code-block:: python

   from pyba import Engine
   # If OpenAI
   agent = Engine(
      openai_api_key="",
      use_logger=True,
      enable_tracing=True,
      trace_save_directory="your-directory",
   )
   agent.run("Go to twitter and search for 'cybersecurity news'")

.. note::
   By default pyba will create a directory **/tmp/pyba** and save the traces with a unique trace_id

.. _headless:

Headless
^^^^^^^^

The headless mode is supported

.. code-block:: python

   from pyba import Engine

   # If OpenAI
   agent = Engine(
      openai_api_key="",
      use_logger=True,
      enable_tracing=True,
      trace_save_directory="your-directory",
      headless=True,
   )
   agent.run("Go to twitter and search for 'cybersecurity news'")

Using the ``headless`` will render some construction useless. This is because we rely on javascript execution in specific functions (see ``extractions.js``).

.. _auto-login:

Automated-logins
^^^^^^^^^^^^^^^^

The library was specifically built for exploratory purposes, and should you need to enter a social media site which requires a login (like Instagram, Twitter, Facebook, LinkedIn etc.) then ``pyba`` will handle that automatically.

Specify which sites you want to login to in the ``.run()`` argument

.. code-block:: python

   from pyba import Engine

   # If OpenAI
   agent = Engine(
      openai_api_key="",
      use_logger=True,
      enable_tracing=True,
      trace_save_directory="your-directory",
      headless=False,
   )
   agent.run("Go to instagram and like all posts by mrbeast", automated_login_sites=["instagram"])

.. _database:

Database-logging
^^^^^^^^^^^^^^^^

The library supports three types of databases:

* MySQL (server-client)
* PostgreSQL (server-client)
* SQLite (file based system)

Set the data configurations using the ``Database`` class from ``pyba`` and set the engines

.. code-block:: python

   from pyba import Engine, Database

   database = Database(engine="sqlite", name="/tmp/pyba/pyba.db")
   engine = Engine(openai_api_key="", enable_tracing=True, database=database)

   output = engine.sync_run(prompt="Visit Flipkart and find the price of the costliest iphone")

   print(output)


You can check for a database called ``EpisodicMemory`` at ``/tmp/pyba/pyba.db``

.. code-block:: bash
   sqlite3 /tmp/pyba/pyba.db
   > .tables
   > select * from EpisodicMemory;

.. note::
   Coming soon: Features for creating an automation script based on what was achieved to save you tokens in case you need to run the same thing multiple times or use it in a report for reproducibility

.. _code-generation:

Automation script generation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

You can create the automation scripts that are used by ``pyba`` to run it multiple times

.. note::
   To create the script you'll need to use the database feature

.. note::
   We're supporting only playwright ``sync endpoints`` right now

.. code-block:: python

   from pyba import Engine, Database

   database = Database(name="sqlite", name="/tmp/pyba/pyba.db")
   engine = Engine(openai_api_key="", enable_logging=True, database=database, use_logger=True)

   output = engine.sync_run(prompt="Order the costliest iphone from amazon India")

   print(output)

   val = engine.generate_code(output_path="/tmp/pyba/automation_code.py")
   if val:
      print("Code generated!")
