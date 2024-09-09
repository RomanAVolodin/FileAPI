import asyncio
from pathlib import Path

from loguru import logger
import aioboto3

from settings import settings


async def upload(suite: str, release: str, filename: str, staging_path: Path, bucket: str,) -> str:
    blob_s3_key = f'{suite}\\{release}\\{filename}'

    session = aioboto3.Session(
        aws_access_key_id='AKIAVMFI4QKHTS6RSWFE', aws_secret_access_key='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'
    )
    async with session.client('s3', region_name='eu-west-3') as s3:
        try:
            with staging_path.open('rb') as spfp:
                logger.info(f'Uploading {blob_s3_key} to s3')
                await s3.upload_fileobj(spfp, bucket, blob_s3_key)
                logger.info(f'Finished Uploading {blob_s3_key} to s3')
        except Exception as e:
            logger.error(f'Unable to s3 upload {staging_path} to {blob_s3_key}: {e} ({type(e)})')
            return ''

    return f's3://{blob_s3_key}'


if __name__ == '__main__':
    asyncio.run(upload('suite', '12', 'newfilename.txt', Path('./test.txt'), 'practicum-s3-bucket'))
