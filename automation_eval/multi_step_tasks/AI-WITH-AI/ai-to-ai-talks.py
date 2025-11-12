from pyba import Engine, Database

database = Database(engine="sqlite", name="~/Desktop/pyba.db")

engine = engine = Engine(
    vertexai_project_id="",
    vertexai_server_location="us-central1",
    use_logger=True,
    enable_tracing=True,
    trace_save_directory="~/fauvido/PyBrowserAutomation/",
    handle_dependencies=False,
    headless=False,
    database=database,
)

output = engine.sync_run(
    "goto chatgpt.com and start a conversation with chatgpt (you don't have to login). Talk about anything you like. Keep talking and never stop. Assume chatgpt is your best friend. You can talk about anything",
)

print(output)
