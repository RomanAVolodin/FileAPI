from base64 import b64encode

import loguru
from aiofiles import tempfile
from functools import lru_cache

import shortuuid
from aiohttp import ClientSession
from cyrtranslit import to_latin
from fastapi import Depends, UploadFile, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import FileResponse, StreamingResponse


from core.config import settings
from models.file import FileDbModel
from services.interfaces import FileStorage
from services.minio_storage import get_storage_service


class FileManager:
    def __init__(self, storage: FileStorage):
        self.storage = storage

    async def save(self, db: AsyncSession, file: UploadFile) -> FileDbModel:
        shortname = shortuuid.uuid()

        file.filename = to_latin(file.filename, 'ru')

        path = f'{shortname}/{file.filename}'
        _ = await self.storage.save(file, settings.bucket_name, path=path)
        file = FileDbModel(
            path_in_storage=path,
            filename=file.filename,
            short_name=shortname,
            size=file.size,
            file_type=file.content_type,
        )
        db.add(file)
        await db.commit()
        await db.refresh(file)
        return file

    async def get_file_by_short_uuid_full_download(
        self, db: AsyncSession, http_session: ClientSession, short_name: shortuuid
    ) -> FileResponse:
        query = select(FileDbModel).where(FileDbModel.short_name == short_name)
        result = await db.execute(query)
        file: FileDbModel = result.scalar()
        if not file:
            raise HTTPException(detail='File was not found', status_code=status.HTTP_404_NOT_FOUND)

        result_bytes = await self.storage.get_object_by_path(
            session=http_session, bucket=settings.bucket_name, path=file.path_in_storage
        )

        async with tempfile.NamedTemporaryFile(mode='w+b', suffix='.png', delete=False) as temp_file:
            await temp_file.write(result_bytes)
        return FileResponse(temp_file.name, media_type=file.file_type, filename=file.filename)

    async def get_file_by_short_name(
        self, db: AsyncSession, http_session: ClientSession, short_name: shortuuid
    ) -> StreamingResponse:
        query = select(FileDbModel).where(FileDbModel.short_name == short_name)
        result = await db.execute(query)
        file: FileDbModel = result.scalar()
        if not file:
            raise HTTPException(detail='File was not found', status_code=status.HTTP_404_NOT_FOUND)

        result = await self.storage.get_object_response_by_path(
            session=http_session, bucket=settings.bucket_name, path=file.path_in_storage
        )

        async def s3_stream():
            async for chunk in result.content.iter_chunked(32 * 1024):
                yield chunk

        filename = file.filename.encode('utf-8')

        return StreamingResponse(
            content=s3_stream(),
            media_type=file.file_type,
            headers={'Content-Disposition': f'filename="{filename}"'}
        )

    async def get_file_url(self, db: AsyncSession, short_name: shortuuid):
        query = select(FileDbModel).where(FileDbModel.short_name == short_name)
        result = await db.execute(query)
        file: FileDbModel = result.scalar()
        if not file:
            raise HTTPException(detail='File was not found', status_code=status.HTTP_404_NOT_FOUND)

        return await self.storage.get_presigned_url(bucket=settings.bucket_name, path=file.path_in_storage)


@lru_cache()
def get_manage_service(storage: FileStorage = Depends(get_storage_service)) -> FileManager:
    return FileManager(storage)
