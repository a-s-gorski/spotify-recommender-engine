
from sqlalchemy import Integer, String, ARRAY
from sqlalchemy.orm import DeclarativeBase, mapped_column
from pgvector.sqlalchemy import Vector

VECTOR_DIM = 500

class Base(DeclarativeBase):
    pass

class Playlist(Base):
    __tablename__ = "playlists"

    id = mapped_column(Integer, primary_key=True)
    name = mapped_column(String, nullable=False)
    tracks = mapped_column(ARRAY(String), nullable=False)
    embedding = mapped_column(Vector(VECTOR_DIM), nullable=False)