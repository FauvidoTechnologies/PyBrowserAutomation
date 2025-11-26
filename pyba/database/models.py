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


class ExtractedData(Base):
    """
    Database for extracted data

    Arguments:
            - `session_id`: A unique session ID for the run
            - `extraction_model`: The pydantic BaseModel strcture for reference
            - `logs`: The actual logs implemented as a growing buffer
    """

    __tablename__ = "ExtractionData"

    session_id = Column(Text, primary_key=True)
    extraction_model = Column(Text, nullable=False)
    logs = Column(Text, nullable=False)

    def __repr__(self):
        return ("ExtractedData(session_id: {0}, extraction_model: {1}, logs: {2})").format(
            self.session_id, self.extraction_model, self.logs
        )
