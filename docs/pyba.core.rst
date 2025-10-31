pyba.core package
=================

The **``pyba.core``** package forms the foundation of the PyBA framework.  
It contains the core logic for browser automation, dependency handling,  
and integration with external providers and scripts.

Package Overview
----------------

The package consists of the following main components:

- **``agent``** — Agents built on Playwright and other automation backends.  
- **``lib``** — Core libraries for dependency management, actions, and tracing.  
- **``scripts``** — Ready-to-use automation scripts such as login and data extraction.  
- **``main``** — Entry point for initializing and running the core engine.  
- **``provider``** — Interfaces for integrating with external APIs or service providers.

Subpackages
------------

.. toctree::
   :maxdepth: 2
   :caption: Core Subpackages

   pyba.core.agent
   pyba.core.lib
   pyba.core.scripts

Submodules
-----------

pyba.core.main
~~~~~~~~~~~~~~

The ``main`` module defines the central entry point for engine initialization  
and orchestration of automation workflows.

.. automodule:: pyba.core.main
   :members:
   :undoc-members:
   :show-inheritance:

pyba.core.provider
~~~~~~~~~~~~~~~~~~

The ``provider`` module contains abstractions and concrete implementations  
for managing API integrations, service credentials, and communication between  
the PyBA engine and third-party providers.

.. automodule:: pyba.core.provider
   :members:
   :undoc-members:
   :show-inheritance:

Module Contents
---------------

.. automodule:: pyba.core
   :members:
   :undoc-members:
   :show-inheritance:
