from typing import Annotated

from aiohttp import ClientSession
from fastapi import APIRouter, UploadFile, File, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.responses import StreamingResponse, FileResponse

from api.v1.schemas.file import FileResponse as FileDtoResponse
from core.http_client import custom_http_client
from db.db import get_session
from services.manager import FileManager, get_manage_service

router = APIRouter()


@router.post(
    '/',
    response_model=FileDtoResponse,
    summary='Upload new file',
    description='Upload file to storage',
    response_description='Uploading creation procedure',
)
async def upload_file(
    file: UploadFile,
    db: AsyncSession = Depends(get_session),
    manager: FileManager = Depends(get_manage_service),
) -> FileDtoResponse:
    document = await manager.save(db, file=file)
    return document


@router.get(
    '/download-full/{short_name}',
    summary='Get file by short uuid',
    description='Get existing file by short uuid',
    response_description='File detailed response',
)
async def get_file(
    short_name: str,
    db: AsyncSession = Depends(get_session),
    manager: FileManager = Depends(get_manage_service),
    http_session: ClientSession = Depends(custom_http_client),
) -> FileResponse:
    return await manager.get_file_by_short_uuid_full_download(db, http_session=http_session, short_name=short_name)


@router.get(
    '/download-stream/{short_name}',
    summary='Get file by short uuid',
    description='Get existing file by short uuid',
    response_description='File detailed response',
)
async def get_file(
    short_name: str,
    db: AsyncSession = Depends(get_session),
    manager: FileManager = Depends(get_manage_service),
    http_session: ClientSession = Depends(custom_http_client),
) -> StreamingResponse:
    return await manager.get_file_by_short_name(db, http_session=http_session, short_name=short_name)


@router.get(
    '/get-url/{path}',
    summary='Get file by short uuid',
    description='Get existing file by short uuid',
    response_description='File detailed response',
)
async def get_file(
    short_name: str,
    db: AsyncSession = Depends(get_session),
    manager: FileManager = Depends(get_manage_service),
) -> StreamingResponse:
    return await manager.get_file_url(db, short_name=short_name)
