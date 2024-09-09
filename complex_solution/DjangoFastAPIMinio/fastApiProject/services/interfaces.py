from abc import ABC, abstractmethod

from aiohttp import ClientResponse, ClientSession
from fastapi import UploadFile


class FileStorage(ABC):
    @abstractmethod
    async def save(self, file: UploadFile, bucket: str, path: str) -> str:
        ...

    @abstractmethod
    async def get_object_by_path(self, session: ClientSession, bucket: str, path: str) -> bytes:
        ...

    @abstractmethod
    async def get_object_response_by_path(self, session: ClientSession, bucket: str, path: str) -> ClientResponse:
        ...

    @abstractmethod
    async def get_presigned_url(self, bucket: str, path: str) -> str:
        ...
