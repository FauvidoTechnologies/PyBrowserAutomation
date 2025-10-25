.. pyba documentation master file, created by
   sphinx-quickstart on Sat Oct 25 10:40:19 2025.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

pyba documentation
==================

PyBA is short for "Python-Browser-Automation". Simply put, it allows you to enter tasks in natural language and have them be executed. It is built on top of ``playwright`` and it supports traceviewing optionally.

.. note::
   pyba was specifically built for OSINT purposes.

The main differentiating factors between pyba and others are as follows:

- Performs a depth-first-search and supports retracing of steps
- Generates multiple ``plans`` optionally to achieve a particular task and performs them in parallel
- Perfect for use cases when the task is **not** extremely clear and more exploratory in nature

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   modules
   pyba