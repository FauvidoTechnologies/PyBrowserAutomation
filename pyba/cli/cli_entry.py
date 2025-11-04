from pyba.cli.cli_core.cli_main import CLIMain


def main():
    cli = CLIMain()
    # By default running only the sync endpoint
    cli.cli_sync_run()
