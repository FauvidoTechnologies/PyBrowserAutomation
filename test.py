from pyba import Engine, Database

database = Database(engine="sqlite", name="/home/purge/Desktop/pyba.db")

engine = engine = Engine(
    vertexai_project_id="atlas-467316",
    vertexai_server_location="us-central1",
    use_logger=True,
    enable_tracing=True,
    trace_save_directory="/home/purge/Desktop",
    handle_dependencies=False,
    headless=False,
    database=database,
)

output = engine.sync_run(
    "goto https://instagram.com, go to messages, search for shrestho, open his DMs and say that it is an AI messaging him and surprise him!",
    automated_login_sites=["instagram"],
)

print(output)
