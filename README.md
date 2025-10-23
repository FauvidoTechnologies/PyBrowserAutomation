# PyBA - Python Browser Automations

This is a browser automation software written in python. It can visit any website, automate testing, repetitive tasks, form filling and more.

## Idea

This library will allow you to run an inhouse playwright instance and automate any task. These tasks can be related to web-scraping, OSINT (OpenSource INTelligence), online shopping, form filling etc.

This is built on top of playwright and it requires either VertexAI or OpenAI API keys to do the "thinking" part of the process. The library also contains support to automatically login to your social media sites (you'll have to provide a username and password! Check the the [usage](#usage) section for more on that) so you can use it for SOCmint or simple automated social media interactions as well.

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

## Usage

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

- Set `handle_dependencies` to `True` if you're running this for the first time and install the playwright browsers and other dependencies by following the instructions.

- Run the `sync` endpoint using `engine.sync_run()`

```python3
engine.sync_run(prompt="open instagram", automated_login_sites=["instagram"])
```

> You can set the `automated_login_sites` argument as whichever website you want to automatially login to.

This is useful in case of OSINT when you inevitably come across a profile that is hidden behind the login wall. Setting that field will trigger the login scripts to run after it verifies the site.

If you don't want to automatically login, don't set this value. The default behavior is to not do any such thing.

- We also have an async endpoint if you need. That can be called using just `.run()`