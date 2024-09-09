from datetime import datetime
from uuid import UUID

from models.base_model import BaseOrjsonModel


class FileResponse(BaseOrjsonModel):
    id: UUID
    path_in_storage: str
    filename: str
    size: int
    file_type: str | None
    short_name: str
    created_at: datetime

    class Config:
        orm_mode = True
