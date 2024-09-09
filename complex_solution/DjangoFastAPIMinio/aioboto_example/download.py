import asyncio
from pathlib import Path

import aioboto3
from loguru import logger


async def serve_blob(suite: str, release: str, filename: str, staging_path: Path, bucket: str):
    blob_s3_key = f'{suite}/{release}/{filename}'

    session = aioboto3.Session(
        aws_access_key_id='AKIAVMFI4QKHTS6RSWFE', aws_secret_access_key='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'
    )
    async with session.client('s3', region_name='eu-west-3') as s3:
        with staging_path.open('wb') as spfp:
            logger.info(f'Downloading {blob_s3_key} from s3')
            await s3.download_fileobj(bucket, blob_s3_key, spfp)
            logger.info(f'Finished Downloading {blob_s3_key} from s3')


if __name__ == '__main__':
    asyncio.run(serve_blob('suite', '12', 'newfilename.txt', Path('./downloaded.txt'), 'practicum-s3-bucket'))