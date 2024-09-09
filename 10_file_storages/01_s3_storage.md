# Хранилище S3

В качестве альтернативы файловым хранилищам появились **объектные хранилища** — они позволяют хранить петабайты данных и масштабируются на лету.

В марте 2006 года компания Amazon представила рынку хранилище Amazon Simple Storage Service (S3), впоследствии ставшее самой популярной реализацией объектного хранилища.

### Что такое объектное хранилище S3

Объектное хранилище S3 (англ. Object storage S3) — это облачный сервис, позволяющий хранить файлы любого типа и объёма. Чаще всего его используют для хранения неструктурированных данных: например, изображений, видео, программного кода, архивов документов.

В объектном хранилище S3 каждый файл представлен в качестве объекта с идентификатором и метаданными. Нахождение объекта в плоском адресном пространстве даёт возможность легко запрашивать доступ к нему по его идентификатору, в отличие от файловой системы, где нужно знать точный путь к файлу.

В объектном хранилище в метаданные можно добавить дополнительную, более подробную информацию о файлах, хранящихся в объекте. Например, метаданные к видеофайлу могут включать информацию о месте съёмки, типе камеры и даже людях, находящихся в каждом кадре.

К достоинствам такого типа хранилища можно отнести:
* Доступ к данным через HTTP API.
* Бесконечная масштабируемость.
* Быстрый поиск объектов за счёт расширенных метаданных и плоского адресного пространства.
* Георепликация — хранение копий объектов на географически распределённых серверах.
* Хранение данных любого типа и размера.

### Как использовать S3 на практике

Напишем приложение, которое будет загружать файл в объектное хранилище и скачивать его оттуда. 

Для работы с S3-хранилищем будем использовать популярную библиотеку [aioboto3](https://aioboto3.readthedocs.io/en/latest/usage.html){target="_blank"}.

Зарегистрируйте учётную запись в сервисе [https://aws.amazon.com/ru/s3/](https://aws.amazon.com/ru/s3/){target="_blank"}.

Перейдите в раздел Storage / S3 (Scalable Storage in the Cloud).

![image](images/s3_at_amazon_fin.png)

S3 — это не иерархическая файловая система, а всего лишь хранилище ключей и значений, хотя ключ часто используется как путь к файлу для организации данных. Чтобы разместить файл в объектном хранилище S3, его необходимо поместить в бакет. **Бакет** (англ. bucket — «ведро») — это сущность для организации хранения в хранилище.

Перед началом работы необходимо создать бакет, кликнув на соответствующую кнопку в интерфейсе.

![image](images/create_bucket_button_fin.png)

Чтобы познакомиться с работой хранилища, не нужно изменять настройки по умолчанию, достаточно придумать имя бакета и выбрать регион расположения.

![image](images/bucket_created_fin.png)

Для доступа к вашему хранилищу из приложения создайте пару ключей `access key` и `secret access key`.
Для этого перейдите в раздел `Security Credentials` и подраздел `Access keys`.

![image](images/security_creds_fin.png)

Загрузите файл в хранилище:

```python
import asyncio
from pathlib import Path

from loguru import logger
import aioboto3

async def upload(suite: str, release: str, filename: str, staging_path: Path, bucket: str,) -> str:
    blob_s3_key = f'{suite}/{release}/{filename}'

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

```

Результатом работы программы будет следующее:

```bash
2023-07-05 15:11:29.066 | INFO     | __main__:upload:19 - Uploading suite/12/newfilename.txt to s3
2023-07-05 15:11:30.025 | INFO     | __main__:upload:21 - Finished Uploading suite/12/newfilename.txt to s3
```

В хранилище появился файл:

![image](images/file_in_storage_fin.png)

Готово!

Хранилище S3 обладает плоской, а не иерархической файловой системой, как в Unix или Windows. Кроме того, в хранилище S3 нет такого понятия как файл или каталог, здесь есть «объекты».

Однако в бакете S3 можно создать некоторое подобие файловой системы, используя префиксы и разделители для организации хранящихся данных.

Каждому объекту можно назначить имя ключа с префиксом. **Префикс** — это строка символов в начале имени ключа объекта. Префикс может быть любой длины в зависимости от максимальной длины имени ключа объекта. Помните, что префиксы — это не каталоги.

Для получения объекта из хранилища используем следующий код:

```python
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
```

```bash
2023-07-05 15:22:57.450 | INFO     | __main__:serve_blob:16 - Downloading suite/12/newfilename.txt from s3
2023-07-05 15:22:58.002 | INFO     | __main__:serve_blob:18 - Finished Downloading suite/12/newfilename.txt from s3
```

Готово! 

С хранилищем S3 разобрались, и оно отлично подходит для хранения фильмов. Но обеспечивать безопасность на внешнем ресурсе будет сложновато. Значит, нужен более оптимальный вариант. О нём и пойдет речь в следующем уроке!

