from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import ORJSONResponse
from miniopy_async import Minio

from api.v1.files import router as file_router
from core.config import settings
from db.db import create_database
from storages import minio


@asynccontextmanager
async def lifespan(app: FastAPI):
    minio.storage = Minio(
        settings.storage_url, access_key=settings.minio_access_key, secret_key=settings.minio_secret_key, secure=False,
    )
    if settings.debug_mode:
        from models.file import FileDbModel
        await create_database()
    yield


app = FastAPI(
    lifespan=lifespan,
    title=settings.project_name,
    description=settings.project_description,
    version='1.0.0',
    docs_url='/api/openapi',
    openapi_url='/api/openapi.json',
    default_response_class=ORJSONResponse,
)


@app.get('/')
async def root(request: Request):
    return {'message': 'Hello World'}


app.include_router(
    file_router, prefix='/api/v1', tags=['File storage management'],
)


if __name__ == '__main__':
    uvicorn.run(
        'main:app', host='0.0.0.0', port=8001, reload=True,
    )
