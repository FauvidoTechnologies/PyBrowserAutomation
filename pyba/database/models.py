from sqlalchemy import Column, Text
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class EpisodicMemory(Base):
    """
    Memory for history logs

    Arguments:
            - `session_id`: A unique session ID for the run
            - `actions`: A JSON string of actions given as output by the model
            - `page_url`: The URL where this action was performed
    """

    __tablename__ = "EpisodicMemory"

    session_id = Column(Text, primary_key=True)
    actions = Column(Text, nullable=False)
    page_url = Column(Text, nullable=False)

    def __repr__(self):
        return ("EpisodicMemory(session_id: {0}, actions: {1}, page_url: {2})").format(
            self.session_id, self.actions, self.page_url
        )


class SemanticMemory(Base):
    """
    Memory for holding intermediate data, relevant goals, extracted outputs

    Arguments:
            - `session_id`: A unique session ID for the run
            - `logs`: The actual logs implemented as a growing buffer

    This is a growing memory type for each session, it holds everything of relevance to the task. This memory
    will be used to summarise the final output type.
    """

    __tablename__ = "SemanticMemory"

    session_id = Column(Text, primary_key=True)
    logs = Column(Text, nullable=False)

    def __repr__(self):
        return ("ExtractedData(session_id: {0}, logs: {1})").format(self.session_id, self.logs)
