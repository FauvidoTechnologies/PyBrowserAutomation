from sqlalchemy import create_engine

from pyba.database.models import Base


class SQLiteHandler:
    """
    Class for handling SQLite table creation
    """

    def __init__(self, database_engine_configs):
        """
        Args:
                `database_engine_configs`: User supplied configurations imported from the Database class
        """

        self.database_engine_configs = database_engine_configs
        self.database_connection_string = self.database_engine_configs.database_connection_string

        self.engine = create_engine(
            self.database_connection_string, connect_args={"check_same_thread": False}
        )

    def sqlite_create_tables(self):
        """
        Method to create the SQLite tables
        """
        Base.metadata.create_all(self.engine)

    def setup(self):
        """
        Entrypoint for database and table creation
        """
        self.sqlite_create_tables()
