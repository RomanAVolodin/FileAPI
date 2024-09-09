from datetime import timedelta
from functools import lru_cache

from aiohttp import ClientResponse, ClientSession
from fastapi import UploadFile, status, Depends, HTTPException
from miniopy_async import Minio

from services.interfaces import FileStorage
from storages.minio import get_storage


class MinioStorage(FileStorage):
    def __init__(self, client: Minio):
        self.client = client

    async def save(self, file: UploadFile, bucket: str, path: str) -> str:
        found = await self.client.bucket_exists(bucket)
        if not found:
            await self.client.make_bucket(bucket)

        _ = await self.client.put_object(
            bucket_name=bucket, object_name=path, data=file, length=-1, part_size=10 * 1024 * 1024,
        )
        return path

    async def get_presigned_url(self, bucket: str, path: str) -> str:
        url = await self.client.get_presigned_url('GET', bucket, path, expires=timedelta(days=1),)
        return url

    async def get_object_by_path(self, session: ClientSession, bucket: str, path: str) -> bytes:
        result = await self.client.get_object(bucket, path, session)
        result_bytes = await result.content.read()
        return result_bytes

    async def get_object_response_by_path(self, session: ClientSession, bucket: str, path: str) -> ClientResponse:
        result = await self.client.get_object(bucket, path, session)
        return result


@lru_cache()
def get_storage_service(client: Minio = Depends(get_storage)) -> FileStorage:
    return MinioStorage(client)
