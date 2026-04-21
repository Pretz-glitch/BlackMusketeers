from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel, create_engine, Session

class DressItem(SQLModel, table=True):
    __table_args__ = {'extend_existing': True}
    id: Optional[int] = Field(default=None, primary_key=True)
    filename: str
    image_path: str
    season: str
    style: str
    color: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

sqlite_url = "sqlite:///app.db"
engine = create_engine(sqlite_url)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session
