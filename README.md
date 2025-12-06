<h1 align="center">PyBA — Python Browser Automation</h1>

<p align="center">
  <strong>No-code, LLM-powered, reproducible browser automation in Python.</strong><br>
  Visit any website, navigate autonomously, fill forms, extract data, perform OSINT, automate testing, and run multi-step workflows — all from one natural-language prompt.
</p>

<p align="center">
  <a href="https://pepy.tech/projects/py-browser-automation">
    <img height="28px" src="https://static.pepy.tech/personalized-badge/py-browser-automation?period=total&units=INTERNATIONAL_SYSTEM&left_color=BLACK&right_color=GREEN&left_text=downloads" />
  </a>
  &nbsp;&nbsp;
  <a href="https://badge.socket.dev/pypi/package/py-browser-automation/0.2.8?artifact_id=tar-gz">
    <img height="28px" src="https://badge.socket.dev/pypi/package/py-browser-automation/0.2.8?artifact_id=tar-gz" />
  </a>
</p>

<p align="center">
  <a href="https://pypi.org/project/py-browser-automation/"><b>PyPI</b></a> •
  <a href="https://openhub.net/p/pyba"><b>CodeHub</b></a> •
  <a href="https://pyba.readthedocs.io/"><b>Documentation</b></a>
</p>

>[!NOTE]
>pyba is currently at version 0.2.9. This is not stable and I will be updating this a lot. The first major release is scheduled for 18th December 2025.

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

### Extraction

Extracts the relevant data **during** automation in a separate thread and logs it.
The format can be specified using pydantic models.

>The extracted data is stored in a separate table as memory

### Trace zip generation

Automatic creation of Playwright trace files for full reproducibility in traceviewer.

### Built-in logging & dependency management

Every step is logged and optionally stored in a local/server database.

### Automatic script generation

Successful runs can be exported as standalone Python Playwright scripts.

### Local or remote databases

Persist every action, observation, and browser state for auditing or replaying runs.

### Stealth mode & anti-fingerprinting presets

Configurable behavior for bypassing common bot-detection heuristics.

### Quick login to platforms

Fast social-media authentication using environment-variable credentials, without ever exposing them to the LLM.

### Thread-safe

Suitable for parallel multi-task workflows.

#### Specialized extractors for certain platforms

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