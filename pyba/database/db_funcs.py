import time

from pyba.database.database import Database


class DatabaseFunctions:
    """
    Composition class for the database functions
    """

    def __init__(self, database: Database):
        """
        Args:
            `database`: The database instance for commiting

        If database is none, this class doesn't do anything
        """
        if database is None:
            return
        self.database = database
        self.session = self.database.session

    def send_submit_query(self):
        """
        Function to send submit based queries to db
        (such as insert and update or delete), it retries 100 times if
        connection returned an error.

        Args:
            `session`: session to commit

        Returns:
            True if submitted success otherwise False
        """
        try:
            for _ in range(1, 100):
                try:
                    self.session.commit()
                    return True
                except Exception:
                    time.sleep(0.1)
        except Exception as e:
            print(f"An error occurred while adding to the database: {e}")
            return False
        return False
