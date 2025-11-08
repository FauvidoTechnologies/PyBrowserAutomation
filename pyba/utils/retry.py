import random


class Retry:
    """
    Class to implement the exponential backoff and retry logic. Note that this backoff and retry will be
    blocking for that specific context.

    Defines the following variables:

    `exponential_base`: 2 (we're using base 2)
    `base_timeout`: 1 second
    `max_backoff_time`: 60 seconds
    """

    def __init__(self):
        self.base = 2
        self.base_timeout = 1
        self.max_backoff_time = 60

    def calculate_next_time(self, attempt_number):
        """
        Function to calculate the next wait time in seconds

        Args:
                `attempt_number`: The number of failed attempts
        """

        delay = self.base_timeout * (self.base ** (attempt_number - 1))
        delay = min(delay, self.max_backoff_time)
        jitter = random.uniform(0, delay / 2)
        return delay + jitter
