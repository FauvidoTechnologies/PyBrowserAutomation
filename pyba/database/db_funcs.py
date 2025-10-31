import json
import time
from typing import Optional

from pyba.database.database import Database
from pyba.database.models import EpisodicMemory


class DatabaseFunctions:
    """
    Composition class for the database functions
    """

    def __init__(self, database: Database):
        """
        Args:
            `database`: The database instance for commiting

        If database is none, it doesn't initialise the database session
        """
        if database is None:
            return
        self.database = database
        self.session = self.database.session

    def submit_query_with_retry(self):
        """
        Function to send submit based queries to db
        (such as insert and update or delete), it retries 100 times if
        connection returned an error.

        Args:
            `session`: session to commit

        Returns:
            True if submitted success otherwise False
        """
        if not hasattr(self, "session"):
            return False

        try:
            for _ in range(1, 100):
                try:
                    self.session.commit()
                    return True
                except Exception:
                    time.sleep(0.1)
        except Exception:
            self.session.rollback()
            return False

        self.session.rollback()
        return False

    def push_to_episodic_memory(self, session_id: str, action: str, page_url: str) -> bool:
        """
        Pushes a new action and page_url onto the stack for a given session_id.
        It retrieves the existing record, appends the new values as JSON strings,
        and updates/inserts the record.

        Args:
            session_id: The unique session ID.
            action: The action string to be pushed.
            page_url: The page URL string to be pushed.

        Returns:
            True if the operation was successful, otherwise False.
        """
        if not hasattr(self, "session"):
            return False
        try:
            memory_record = (
                self.session.query(EpisodicMemory)
                .filter(EpisodicMemory.session_id == session_id)
                .one_or_none()
            )

            if memory_record:
                try:
                    actions_list = json.loads(memory_record.actions)
                    page_url_list = json.loads(memory_record.page_url)
                except json.JSONDecodeError:
                    # If stored data is not a valid json, refresh it with a new list
                    actions_list = []
                    page_url_list = []

                actions_list.append(action)
                page_url_list.append(page_url)

                memory_record.actions = json.dumps(actions_list)
                memory_record.page_url = json.dumps(page_url_list)

            else:
                new_memory = EpisodicMemory(
                    session_id=session_id,
                    actions=json.dumps([action]),
                    page_url=json.dumps([page_url]),
                )
                self.session.add(new_memory)

            return self.submit_query_with_retry()

        except Exception:
            self.session.rollback()
            return False
        finally:
            self.session.close()

    def get_episodic_memory_by_session_id(self, session_id: str) -> Optional[EpisodicMemory]:
        """
        Retrieves an episodic memory record by its `session_id`.

        Args:
            `session_id`: The unique session ID to query for.
        Returns:
            An EpisodicMemory object if found, else None.
        """
        # Check if session exists
        if not hasattr(self, "session"):
            return None
        try:
            memory = self.session.get(EpisodicMemory, session_id)
            return memory
        except Exception:
            return None
