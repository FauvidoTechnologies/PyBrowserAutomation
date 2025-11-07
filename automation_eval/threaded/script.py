import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from pyba import Engine, Database
from pyba.core import DependencyManager

DependencyManager.playwright.handle_dependencies()

home = Path.home() / "Desktop"
db_path = home / "pyba.db"

# SQLAlchemy should be able to handle concurrent writes by itself through WAL mode
database = Database(engine="sqlite", name=str(db_path))


def make_engine():
    return Engine(
        vertexai_project_id=os.getenv("vertexai_project_id"),
        vertexai_server_location="us-central1",
        use_logger=True,
        headless=False,
        enable_tracing=True,
        trace_save_directory=str(home),
        handle_dependencies=False,
        database=database,
    )


def run_task(task_prompt, automated_login_sites=None):
    engine = make_engine()
    try:
        result = engine.sync_run(
            prompt=task_prompt, automated_login_sites=automated_login_sites or []
        )
        return {"task": task_prompt, "success": True, "result": result}
    except Exception as e:
        print("here")
        return {"task": task_prompt, "success": False, "error": str(e)}


if __name__ == "__main__":
    task_list = [
        "Search for ‘iPhone 16 Pro’ on Amazon, extract price and delivery info, then do the same on flipkart and output a comparison table",
        "Visit https://bbc.com/news, scrape the top 10 headlines and their URLs, and gimme that",
        "Open https://github.com/trending, extract repository names, descriptions, and star counts",
        "Log into Gmail and summarize all unread emails received today, grouping them by sender and subject",
        "Open Google Scholar and search ‘federated learning privacy’, then extract the first 10 paper titles and authors.",
    ]

    max_workers = min(5, len(task_list))
    results = []

    with ThreadPoolExecutor(max_workers=max_workers) as ex:
        futures = {ex.submit(run_task, t, ["instagram", "gmail"]): t for t in task_list}
        for fut in as_completed(futures):
            res = fut.result()
            results.append(res)

    print("All done. Summary:", results)
