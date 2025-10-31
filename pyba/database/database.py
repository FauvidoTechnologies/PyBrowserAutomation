from typing import Literal

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from pyba.utils.load_yaml import load_config

config = load_config("general")["database"]


class Database:
    """
    Client-side database function -> Minimizes the config use
    """

    def __init__(
        self,
        engine: Literal[
            "sqlite", "postgres", "mysql"
        ],  # Optional: Can be specified inside the config as well
        name: str = None,
        host: str = None,
        port: int = None,
        username: str = None,
        password: str = None,
        ssl_mode: Literal["disable", "require"] = None,
    ):
        """
        Args:
                sqlite:
                        `engine`: "sqlite"
                        `name`: path to the database file
                        other details can be left empty

                mysql:
                        `engine`: "mysql"
                        `name`: Name of the mysql database
                        `username` and `password`: For logging into the server
                        `host` and `port`: Location of the server

                        Note: Default port is 3306 for MySQL

                postgres:
                        `engine`: "postgres"
                        `name`: Name of the postgres database
                        `username` and `password`: For logging into the server
                        `host` and `port`: Location of the server

                        Note: Default port is 5432 for MySQL
                        Note: `ssl_mode`: "require" for encrypted databases

        Optionally supports entries defined inside the config as well in case they are not provided here.

        > This engine is the recommended way to define the database structure
        """
        engine: str = engine or config["engine"]

        self.name: str = name or config["name"]
        self.host: str = host or config["host"]
        self.port: int = port or config["port"]
        self.username: str = username or config["username"]
        self.password: str = password or config["password"]
        self.ssl_mode: str = ssl_mode or config["ssl_mode"]

        self.database_connection_string = self.create_database(engine_name=engine)
        self.session = self.create_connection(engine_name=engine)

    def create_database(self, engine_name: Literal["sqlite", "postgres", "mysql"]) -> str:
        """
        Defines connection URLs for the different databases for SQLAlchemy usage

        Args:
                `engine_name`: The database model name for initialisation

        Returns:
                A string for SQLAlchemy connection
        """

        return {
            "postgres": f"postgresql+psycopg2://{self.username}:{self.password}@{self.host}:{self.port}/{self.name}?sslmode={self.ssl_mode}",
            "mysql": f"mysql+pymysql://{self.username}:{self.password}@{self.host}:{self.port}/{self.name}",
            "sqlite": f"sqlite:///{self.name}",
        }[engine_name]

    def create_connection(self, engine_name: Literal["sqlite", "postgres", "mysql"]):
        """
        Function to create connections to the database

        Args:
                `engine_name`: The database engine name

        Returns:
                connection if successful otherwise False
        """
        connection_args = {}

        if engine_name == "sqlite":
            connection_args["check_same_thread"] = False

        try:
            db_engine = create_engine(
                self.database_connection_string,
                connect_args=connection_args,
                pool_size=50,
                pool_pre_ping=True,
            )

            Session = sessionmaker(bind=db_engine)

            return Session()
        except Exception as e:
            print(f"Couldn't create a connection to the database: {e}")
            return False


"""
Example:

from pyba import Engine, Database

database = Database(engine="sqlite", name="/tmp/pyba/pyba.db")
engine = Engine(openai_api_key=os.getenv("openai_api_key"), use_logger=True, handle_dependencies=False, enable_tracing=True, database=database)

output = engine.sync_run(prompt="go to workflow and download my gradecard", automated_login_sites=["workflow_iitm"])

print(f"This is my gradecard details: {output}")

val = engine.save_code(save_path="/tmp/pyba/automation_code.py")

if val:
	print("Automation code saved at /tmp/pyba/automation_code.py")
"""
