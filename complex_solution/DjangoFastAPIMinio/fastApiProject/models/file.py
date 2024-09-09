import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, Index, Integer, String
from sqlalchemy.dialects.postgresql import UUID

from db.db import Base


class FileDbModel(Base):
    __tablename__ = 'files'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    path_in_storage = Column(String(255), nullable=False, unique=True)
    filename = Column(String(255), nullable=False)
    size = Column(Integer, nullable=False)
    file_type = Column(String(100), nullable=True)
    short_name = Column(String(24), nullable=False, unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    Index('idx_file_path', 'path_in_storage')
    Index('idx_file_short_name', 'short_name')

    def __init__(self, path_in_storage: str, filename: str, short_name: str, size: int, file_type: str) -> None:
        self.path_in_storage = path_in_storage
        self.filename = filename
        self.short_name = short_name
        self.size = size
        self.file_type = file_type

    def __repr__(self) -> str:
        return f'<id {self.id}>'
