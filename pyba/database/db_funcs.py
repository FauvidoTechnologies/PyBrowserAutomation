import time


def send_submit_query(session):
    """
    Function to send submit based queries to db
    (such as insert and update or delete), it retries 100 times if
    connection returned an error.

    Args:
        session: session to commit

    Returns:
        True if submitted success otherwise False
    """
    try:
        for _ in range(1, 100):
            try:
                session.commit()
                return True
            except Exception:
                time.sleep(0.1)
    except Exception as e:
        print(f"An error occurred while adding to the database: {e}")
        return False
    return False
