import os
from pathlib import Path

from pyba import Engine

cwd = Path.cwd()

engine = Engine(
    vertexai_project_id=os.getenv("vertexai_project_id"),
    vertexai_server_location=os.getenv("vertexai_server_location"),
    handle_dependencies=False,
    enable_tracing=True,
    trace_save_directory=str(cwd),
)

# Since we're using the instagram login script, make sure to set the instagram_username and instagram_password in the enviornment
engine.sync_run(
    prompt="look for posts by mrbeast on instagram", automated_login_sites=["instagram"]
)
