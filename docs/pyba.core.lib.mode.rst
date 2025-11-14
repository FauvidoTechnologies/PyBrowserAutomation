PyBA Modes
==========================

The **PyBA modes** define the high-level exploration strategies used by the
PyBA autonomous OSINT agent. These modes determine *how* PyBA generates plans,
navigates the search space, performs web interactions, and reasons over
collected data.

At a high level, both **Breadth-First Search (BFS)** and **Depth-First Search
(DFS)** modes automatically:

- Generate structured exploratory plans
- Execute actions such as web searches, browser automation, and API calls
- Reason over intermediate outputs
- Produce reproducible results

The difference lies in *how* they explore the space of possible actions.

Submodules
----------

Breadth First Search
-----------------------------

.. automodule:: pyba.core.lib.mode.BFS
   :members:
   :undoc-members:
   :show-inheritance:

**Description**

The **BFS Mode** explores the search space *laterally*. It is ideal when you
want to test multiple hypotheses or approaches in parallel.

Key characteristics:

- **Multiple plans** are generated at the start  
  (bounded by ``max_breadth`` — default: 5).
- All plans are **executed in parallel**, allowing wide exploration.
- Each plan proceeds for up to ``max_depth`` steps  
  (default: 10), where each step is an LLM-generated action.

This mode is excellent for OSINT workflows where many different leads,
strategies, or data sources must be probed simultaneously.

**Example Usage**

.. code-block:: python

   from pyba import BFS, Database

   database = Database(engine="sqlite", name="/tmp/pyba.db")
   bfs = BFS(api_key="OPENAI_KEY", database=database,
             max_breadth=5, max_depth=10)

   output = bfs.sync_run(prompt="map out this person's digital footprint")
   print(output)


Depth First Search
-----------------------------

.. automodule:: pyba.core.lib.mode.DFS
   :members:
   :undoc-members:
   :show-inheritance:

**Description**

The **DFS Mode** explores a search path *deeply*, focusing on one detailed plan
at a time.

Key characteristics:

- Generates **one extremely detailed plan**.
- Executes the plan for up to ``max_depth`` steps  
  (same action-step definition as BFS).
- After completing the plan, PyBA generates a **new plan** based on:
  - the progress so far,
  - the intermediate results,
  - and updated reasoning.
- This cycle repeats **``max_breadth`` times** (default: 5).

DFS is ideal when an OSINT task requires following a chain of logic or
investigation deeply before considering alternatives.

**Example Usage**

.. code-block:: python

   from pyba import DFS, Database

   database = Database(engine="sqlite", name="/tmp/pyba.db")
   dfs = DFS(api_key="OPENAI_KEY", database=database,
             max_breadth=5, max_depth=10)

   output = dfs.sync_run(prompt="trace connections between these entities")
   print(output)


Base module
------------------------------

.. automodule:: pyba.core.lib.mode.base
   :members:
   :undoc-members:
   :show-inheritance:

This module defines the shared infrastructure underpinning BFS and DFS modes,
including:

- Core execution loops  
- Logging and reproducibility primitives  
- Database and state integration  
- Plan and step orchestration utilities  


Module contents
---------------

.. automodule:: pyba.core.lib.mode
   :members:
   :undoc-members:
   :show-inheritance:
