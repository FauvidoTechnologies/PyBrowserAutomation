# PyBA — Python Browser Automation

[![PyPI Downloads](https://static.pepy.tech/personalized-badge/py-browser-automation?period=total&units=INTERNATIONAL_SYSTEM&left_color=BLACK&right_color=GREEN&left_text=downloads)](https://pepy.tech/projects/py-browser-automation)

PyBA (Py Browser Automation) is a no-code, LLM-powered, reproducible browser automation framework written in Python.
It can visit any website, navigate interfaces autonomously, fill forms, perform OSINT tasks, automate testing, extract data, and execute complex multi-step workflows - all from a single natural-language prompt.

Built on top of Playwright, PyBA focuses on highly exploratory automations rather than precise inputs (though it supports both styles). It is designed for developers, researchers, analysts, and security engineers who want human-level browser reasoning without manually writing automation scripts.

---

## Core Modes

PyBA provides three execution modes, each optimized for a different style of reasoning:

- `Normal Mode`
  Deterministic navigation using exact instructions.  
  Example:  
  `"Open Instagram, go to my DMs, and tell XYZ I'll be late for the party."`

- `BFS Mode`
  Breadth-first reasoning for tasks with multiple possible success paths.  
  Example:  
  `"Map all possible online identities associated with the username 'vect0rshade'."`

- `DFS Mode`
  Deep, recursive exploration for investigative or research-type tasks.  
  Example:  
  `"Analyze this user’s GitHub activity and infer their technical background."`

---

## Key Features

##### Trace zip generation

Automatic creation of Playwright trace files for full reproducibility in traceviewer.

##### Built-in logging & dependency management

Every step is logged and optionally stored in a local/server database.

##### Automatic script generation

Successful runs can be exported as standalone Python Playwright scripts.

##### Local or remote databases

Persist every action, observation, and browser state for auditing or replaying runs.

##### Stealth mode & anti-fingerprinting presets

Configurable behavior for bypassing common bot-detection heuristics.

##### Quick login to platforms

Fast social-media authentication using environment-variable credentials, without ever exposing them to the LLM.

##### Thread-safe

Suitable for parallel multi-task workflows.

###### Specialized extractors for certain platforms

(e.g., YouTube metadata, structured outputs, etc.)

**For detailed examples of each feature, refer to the `automation_eval/` directory.**

---

## Philosophy

PyBA originated from building a fully automated intelligence/OSINT platform designed to replicate everything a human analyst can do in a browser - but with reproducibility and speed.

Goals include:

- Integrating LLM cognition directly into browser operations  
- Navigating complex websites like a human  
- Avoiding bot-detection halts  
- Providing standardized logs and replayability  
- Scaling from simple automations to deep investigative workflows

---

## Installation

Install via PyPI:

```sh
pip install py-browser-automation
```

Or install from source:

```sh

git clone https://github.com/FauvidoTechnologies/PyBrowserAutomation
cd PyBrowserAutomation
pip install .
```

## Quickstart

(See full documentation at: https://pyba.readthedocs.io/)

### 1. Initialize Engine

You can use OpenAI, VertexAI, or Gemini as the reasoning backend.

Example (OpenAI):

```python
from pyba import Engine

engine = Engine(openai_api_key="")
output = engine.sync_run(
    prompt="open my instagram and tell me who posted what",
    automated_login_sites=["instagram"]
)
print(output)
```

Or generate automation code:

```py
output = engine.sync_run(
    prompt="visit the Wikipedia page for quantum mechanics, click the first hyperlink repeatedly until you reach Philosophy, and count the steps"
)

engine.generate_code(output_path="/tmp/script.py")
print(output)
```

Explore more examples in `automation_eval/`.

---

If the project has helped you, consider giving it a star 🌟!