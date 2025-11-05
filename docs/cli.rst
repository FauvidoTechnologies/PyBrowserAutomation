PyBA — CLI Usage Guide
######################

This document is a complete, step-by-step usage file for the ``pyba`` command line interface. It explains all flags, modes, environment variables and gives worked examples that split the large monolithic command into sane, composable steps.

---

.. contents:: Table of contents
   :depth: 2
   :local:

---

1. Quickstart
=============

A minimal example to run a single automation task **without** logging to a database (use ``normal`` mode):

.. code-block:: bash

    # (optional) install the package first
    pip install .

    # Run in normal mode with a simple task
    pyba normal -t "go to example.com and find the contact page" --openai-api-key "your-key"

If you want to **store logs and interactions** in a database (to later generate scripts, analyze runs, or reuse recordings) use ``database`` mode instead — see examples below.

---

2. Installation
===============

You can install the project locally (editable) for development, or install the package to use the CLI directly.

.. code-block:: bash

    # editable install (dev)
    git clone https://github.com/fauvidoTechnologies/PyBrowserAutomation.git && cd PyBrowserAutomation
    pip install -e .

    # or normal install
    pip install pyba  # if published

    # or install with pipx for an isolated CLI install
    pipx install .

After installation, the ``pyba`` entrypoint will be available on your PATH on Unix-like systems and macOS.

.. admonition:: Note
   :class: note

   Tests were performed on Linux and macOS; Windows behavior may differ slightly.

---

3. Modes
========

``pyba`` has two main modes of operation. They choose how the CLI behaves regarding logging and clarifications.

normal
------

* ``pyba normal`` — Runs automations but **does not store logs** in a database.
* Use this mode for quick ad-hoc runs or scraping where you don't need persistence.

Example:

.. code-block:: bash

    pyba normal -t "search for cheap headphones on amazon.in" --openai-api-key ""

database
--------

* ``pyba database`` — Stores logs and runtime traces to the configured database engine; useful for building scripts from run-history and for auditability.
* When using ``database`` mode you **must** specify the database engine and name/path using ``-e`` and ``-n`` respectively.

Example (SQLite):

.. code-block:: bash

    pyba database -e sqlite -n /tmp/pyba.db -t "search gifts on amazon" --openai-api-key ""

---

4. Global / base flags (explanations)
=====================================

Below are flags defined on the ``base_parser`` (available to both ``normal`` and ``database`` modes unless otherwise noted):

* ``-V``, ``--version``

  * Prints the software version and exits.

* ``--openai-api-key <KEY>``

  * Use this to run automations with OpenAI models.
  * If provided, the tool will attempt to use OpenAI for LLM-driven decisions.

* ``--vertexai-project-id <PROJECT_ID>``

  * Use Vertex AI's Gemini models. Must be a valid GCP project id.
  * Requires properly configured VertexAI credentials on the machine.

* ``--vertexai-server-location <LOCATION>``

  * The region for VertexAI model serving (for example: ``us-central1``).

* ``--headless``

  * Run playwright in headless mode (no GUI). Common for servers/containers.

* ``--handle-deps``

  * Automatically install or manage Playwright/browser dependencies as required.
  * Useful to ensure required browser binaries are present before starting automation.

* ``-v``

  * **Verbose logger**; prints live updates of what the automation is doing.
  * Very useful while debugging or when you want a play-by-play in the terminal.

* ``--enable-tracing``

  * Enables Playwright tracing (records actions/network) and produces a ``.zip`` trace file compatible with Playwright's Trace Viewer.

* ``--trace-save-dir <DIR>``

  * Directory to save generated trace ``.zip`` files when ``--enable-tracing`` is used.

* ``-t``, ``--task "<TASK STRING>"``

  * The natural-language automation task to execute, e.g. ``-t "search amazon for gifts"``.

* ``-L``, ``--login-sites <SITE>``

  * Add this flag *repeatedly* to enable automated login to pre-configured sites (the tool prints which sites are enabled).
  * Example: ``-L instagram -L amazon``.
  * **NOTE:** automated login requires the corresponding credentials to be set in environment variables — see section 6.

---

5. Database-mode-only flags
===========================

When you run ``pyba database``, additional flags are required/available for database configuration:

* ``-e``, ``--engine <engine>`` (required)

  * The database engine to use. Allowed values: ``sqlite``, ``mysql``, ``postgres``.

* ``-n``, ``--name <name_or_path>`` (required)

  * For SQLite: the **path** to the ``.db`` file (e.g. ``/tmp/pyba.db``).
  * For MySQL/Postgres: the database **name** on the server.

* ``-u``, ``--username <username>``

  * Username for MySQL/Postgres servers.

* ``-p``, ``--password <password>``

  * Password for MySQL/Postgres servers (consider using env vars or a secrets manager instead of passing on the CLI).

* ``-H``, ``--host-name <hostname_or_ip>``

  * Hostname or IP of the DB server for MySQL/Postgres.

* ``-P``, ``--port <port>``

  * Port number of the DB server for MySQL/Postgres.

* ``--ssl-mode <mode>``

  * ``postgres`` SSL mode: ``disabled`` (default) or ``required``.

* ``--generate-code``

  * The ``script generation`` flag: If enabled, it generates a playwright script that correctly performs the same task as the model without using any more of your tokens (if you need to perform tasks repeatedly)

* ``--code-output-path``

  * The ``output path`` for the generated code. If not specified, this defaults to ``/tmp/pyba_script.py``

.. tip::

   The parser validates the engine value — if you pass an unsupported engine the CLI will exit with an error message.

---

6. Environment variables & automated login
==========================================

Automated login is powered by a login engine that expects credentials to be available in the environment. The CLI prints a small confirmation for each login site enabled.

Typical environment variables (example if you need to visit instagram and facebook):

.. code-block:: bash

    export instagram_username=your_username
    export instagram_password=supersecurepassword

    export facebook_username=youandyouonly
    export facebook_password=anotherpass

Use your shell's secure mechanism to store API keys & passwords. Avoid placing secrets in shell history or in plain text files.

If you run in CI, use the CI provider's secrets facility.

---

7. Step-by-step examples
===================================================

Below is the monolithic command you provided, split into clear steps and explained.

1) Install dependencies and ensure environment is ready
-----------------------------------------------------

.. code-block:: bash

    # ensure playwright dependencies if you need the browsers
    pyba normal --handle-deps

2) Run the database mode (broken down and explained)
---------------------------------------------------

.. code-block:: bash

    # Step A: create or point to the sqlite DB file path
    # (this will create the file if it doesn't exist and store run logs there)
    export PYBA_DB_PATH=/tmp/pyba.db

    # Step B: run the automation with clear flags
    pyba database \
      -e sqlite \
      -n "$PYBA_DB_PATH" \
      -t "go to Amazon India and look for gifts for my mom under 5k and text that to her on Instagram" \
      --vertexai-project-id "test-id" \
      --vertexai-server-location "test-location" \
      --handle-deps \
      --enable-tracing \
      --trace-save-dir "/tmp/pyba_traces" \
      -v \
      -L instagram \
      -L amazon \
      --generate-code \
      --code-output-path "/tmp/script.py"

**What each flag does in this command:**

* ``-e sqlite`` and ``-n /tmp/pyba.db`` — Use an SQLite file to log runs.
* ``-t "..."`` — The automation instruction in plain English.
* ``--vertexai-*`` — Use VertexAI (if you prefer OpenAI, set ``--openai-api-key`` instead).
* ``--handle-deps`` — Ensure Playwright browsers/deps are installed before running.
* ``--enable-tracing`` + ``--trace-save-dir`` — Record a trace zipped to ``/tmp/pyba_traces`` for replaying in Playwright Trace Viewer. It can be used to create a script using the SDK (support for CLI coming soon!)
* ``-v`` — Print verbose logs to the console.
* ``-L instagram -L amazon`` — Instruct the login engine to attempt automated login for these sites (credentials must be set in env).
* ``--generate-coode`` — Generate the automation script in sync playwright
* ``--code-output-path`` — Save the automation script in the specified location at ``/tmp/script.py``

---

8. Common tasks & troubleshooting
=================================

Check version
-------------

.. code-block:: bash

    pyba --version
    # or
    pyba -V

See help for top-level CLI
-------------------------

.. code-block:: bash

    pyba --help

See help for a specific mode
---------------------------

.. code-block:: bash

    pyba normal --help
    pyba database --help

Database engine validation error
--------------------------------

If you run ``pyba database`` with an engine not in ``[sqlite, mysql, postgres]``, the CLI will exit with:

.. code-block::

    Wrong database engine chosen. Please choose from sqlite, mysql or postgres

Make sure you pass one of the allowed values.

Trace files not appearing
-------------------------

* If you used ``--enable-tracing`` but did not set ``--trace-save-dir``, the tool will use a default location which is the current directory (check logs printed when running with ``-v``).
* Ensure Playwright tracing is supported by your installed playwright version.

Headless runs failing on servers
--------------------------------

* Use ``--handle-deps`` to ensure that required browser binaries are installed.
* On Linux servers, you might need additional OS packages (fonts, libnss, etc.) for headless chrome/chromium.

Credentials not being read
--------------------------

* Confirm your environment variables are exported in the same shell/process that calls ``pyba``.

---

9. Quick reference: common examples
===================================

**Normal mode — ad-hoc search (no DB):**

.. code-block:: bash

    pyba normal -t "find the CSE contact page for IIT Madras" --openai-api-key ""

**Database mode — SQLite, tracing and verbose:**

.. code-block:: bash

    pyba database -e sqlite -n /tmp/pyba.db \
      -t "search amazon.in for birthday gifts under 5000 INR" \
      -v --enable-tracing --trace-save-dir /tmp/pyba_traces --handle-deps \
      --openai-api-key ""

**Database mode — Postgres example (remote DB):**

.. code-block:: bash

    pyba database -e postgres -n pyba_db -u dbuser -p "dbpass" -H 192.168.1.10 -P 5432 -t "task here" --openai-api-key ""

**Use OpenAI instead of VertexAI:**

.. code-block:: bash

    pyba database -e sqlite -n /tmp/pyba.db -t "task here" --openai-api-key "$OPENAI_API_KEY"

---

Final notes and suggestions
===========================

* Prefer **environment variables** for secrets — it's safer than passing credentials on the command line, as shown in the last example.
* When debugging, always re-run with **-v (verbose)** and, if necessary, **--enable-tracing** so you can inspect the Playwright trace with Playwright Trace Viewer.
* Keep **--handle-deps** handy for fresh environments or containers where browsers are not installed.