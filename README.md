# PyBA - Python Browser Automations

This is a no-code browser automation software written in python. It can visit any website, automate testing, repetitive tasks, form filling and more. This library is specifically built for more exploratory analysis than EXACT inputs (though it supports both through different modes).

## Features

- `Trace zip` file creation to recreate the automation for playwright traceviewer
- `Logger` and `dependency management` automatically
- Creation of the `automation script` in file once successful
- `Local and server based` database creation for holding all the actions performed
- Stealth mode and config heavy files for custom bypass laws
- `Quick login` to social media sites **without passing credentials** to the LLM

---

If the software has helped, consider giving us a star 🌟!

---

## Idea

This library will allow you to run an inhouse playwright instance and automate any task. These tasks can be related to web-scraping, OSINT (OpenSource INTelligence) etc.

This is built on top of playwright and it requires either VertexAI or OpenAI API keys to do the "thinking" part of the process. The library also contains support to automatically login to your social media sites (you'll have to provide a username and password! Check the the [usage](#usage) section for more on that) so you can use it for SOCmint or simple automated social media interactions as well.

We optionally allow you to enable tracing, the logs of which you can see on playwright's `traceviewer`. We also support logging and config files should you want to change any defaults

## Why?

The need for such a software came when I was building a fully automated intelligence framework. The goal is to replicate everything a human can do on the internet, and automate that process. This tool will employ all sorts of anti-bot detection and anti-fingerprinting techniques (I am still learning about them...) and will make sure that nothing halts the automation.

## Installation

The library can be installed via `pip`:

```sh
pip install py-browser-automation
```

or you can install it from the source:

```sh
git clone https://github.com/FauvidoTechnologies/PyBrowserAutomation/
cd PyBrowserAutomation
pip install .
```

## Usage (quickstart)

> [!NOTE]
> For more detailed instructions visit the [docs](https://pyba.readthedocs.io/)

- Import the main engine using:

```python3
from pyba import Engine
```

- Set the right configurations depending on which model you want to use:

> For VertexAI
```python3
engine = Engine(vertexai_project_id="", vertexai_server_location="", handle_dependencies=False)
```

> For OpenAI
```python3
engine = Engine(openai_api_key="", handle_dependencies=False)
```

> For Gemini (without VertexAI)
```python3
engine = Engine(gemini_api_key="")
```

- Set `handle_dependencies` to `True` if you're running this for the first time and install the playwright browsers and other dependencies by following the instructions.

- Run the `sync` endpoint using `engine.sync_run()`

```python3
engine.sync_run(prompt="open instagram")
```

For more use cases, check out the [evals](./automation_eval) direcrtory.