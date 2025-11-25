Extractions
===========

``pyba`` can extract information from the relevant webpages without you having to specify anything more than your preferred extraction
format!

There are two ways to use this feature.

.. contents::
   :local: 
   :depth: 2

.. _using-pydantic:

Using Pydantic
^^^^^^^^^^^^^^

To use the ``pydantic`` BaseModel, you can specify that in the ``run()`` method

.. code-block:: python

   from typing import List
   from pydantic import BaseModel

   from pyba import Engine, Database

   database = Database(engine="sqlite", name="/tmp/pyba.db")

   class Output(BaseModel):
       title: List[str]
       num_upvotes: List[str]
       num_comments: List[str]

   # If OpenAI
   agent = Engine(openai_api_key="", use_logger=True, enable_tracing=True, database=database)
   output = agent.run(
   """
   Go to news.ycombinator.com, the show section. Extract all the posts and fit them according to the format provided.
   """, extraction_format= Output)


.. _Normal:

Normal
^^^^^^^

You can just specify the extraction type in the prompt itself, note that it won't be as extact as using a class

.. code-block:: python

   from typing import List
   from pyba import Engine, Database

   database = Database(engine="sqlite", name="/tmp/pyba.db")

   # If OpenAI
   agent = Engine(openai_api_key="", use_logger=True, enable_tracing=True, database=database)
   output = agent.run(
   """
   Go to news.ycombinator.com, the show section. Extract all the posts. Extract the title, upvotes and comments for each post.
   """)
