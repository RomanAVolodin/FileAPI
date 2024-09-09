from miniopy_async import Minio

storage: Minio | None = None


async def get_storage() -> Minio:
    return storage
