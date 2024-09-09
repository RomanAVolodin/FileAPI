# FileAPI-сервис кинотеатра

Пришло время применить знания о файловых хранилищах в вашем проекте!

##  Ещё один API

![image](images/Облачные решения.png)

Создадим сервис FileAPI, который будет принимать файлы от остальных сервисов кинотеатра, сохранять их в объектном хранилище S3 и выдавать эти файлы пользователям по запросу. 

В качестве объектного хранилища рекомендуем использовать уже хорошо знакомый фреймворк FastAPI и MinIO. Также потребуется база данных для учёта и контроля загруженных файлов. Реализуем её на базе PostgreSQL с использованием библиотеки SQLAlchemy.

Модель базы данных может быть такой (конечная реализация остаётся на ваше усмотрение):

```python
class FileDbModel(Base):
    __tablename__ = 'files'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    path_in_storage = Column(String(255), nullable=False, unique=True)
    filename = Column(String(255), nullable=False)
    size = Column(Integer, nullable=False)
    file_type = Column(String(100), nullable=True)
    short_name = Column(String(24), nullable=False, unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    Index('idx_file_path', 'path_in_storage')
    Index('idx_file_short_name', 'short_name')

    def __init__(self, path_in_storage: str, filename: str, short_name: str, size: int, file_type: str) -> None:
        self.path_in_storage = path_in_storage
        self.filename = filename
        self.short_name = short_name
        self.size = size
        self.file_type = file_type

    def __repr__(self) -> str:
        return f'<id {self.id}>'
```

* `id` — первичный ключ с типом UUID. 
* `path_in_storage` — полное имя файла с префиксом для доступа в S3-хранилище.
* `filename` — оригинальное имя файла, необходимо сохранять для выдачи пользователю.
* `size` — размер файла (коллеги-фронтендеры будут благодарны за эту информацию).
* `file_type` — тип файла (необходимо для корректного отображения на фронтенде).
* `short_name` — короткое имя файла.
* `created_at` — временная метка добавления файла в хранилище.

Обратим внимание на поле `short_name` (имя поля может быть любым). Сервис хранения файлов (FileAPI) должен обеспечивать достойный уровень безопасности хранимым данным. Одна из мер по обеспечению безопасности — скрыть оригинальное имя файла от сторонних лиц: превратить имя файла в бессмысленный набор символов во время генерации ссылки на файл.

Например, сравните две ссылки: 
- https://our_cool_servce.ru/star_wars_episode_1.mp4
- https://our_cool_servce.ru/hhouypjjdssd
  
В первом случае сразу понятно, что именно находится по этой ссылке. А ведь это мог быть не фильм, а документы, которые не хотелось бы афишировать! А вот вторая ссылка ничего полезного посторонним не даёт.

Для генерации подобного набора символов можно создать свой метод или использовать библиотеку [shortuuid](https://github.com/skorokithakis/shortuuid/){target="_blank"}. Можно даже использовать UUID, но необходимо учитывать, что пользователям иногда необходимо передавать ссылки не в виде электронного сообщения, а на бумаге, голосом или даже в SMS. И чем короче будет эта ссылка, тем благодарнее будут ваши клиенты!

#### Отправка файла в хранилище

Для работы с MinIO будем использовать пакет [miniopy-async](https://github.com/hlf20010508/miniopy-async){target="_blank"}. Это асинхронная версия [клиента для python](https://min.io/docs/minio/linux/developers/python/API.html){target="_blank"}, входящего в состав [minio SDK](https://min.io/docs/minio/linux/developers/minio-drivers.html){target="_blank"}.

```python
from fastapi import UploadFile
from miniopy_async import Minio
from miniopy_async.helpers import ObjectWriteResult

class MinioStorage:
    def __init__(self):
        # код упрощен для демонстрации, правильнее инициализировать соединение один раз 
        # и внедрять в сервис в качестве зависимости
        self.client = Minio(
            endpoint='minio_service:9000', 
            access_key='AKIAVMFI4QKHTS6RSWFE', 
            secret_key='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', 
            secure=False,
        )

    async def save(self, file: UploadFile, bucket: str, path: str) -> ObjectWriteResult:
        result = await self.client.put_object(
            bucket_name=bucket, object_name=path, data=file, length=-1, part_size=10 * 1024 * 1024,
        )
        return result
```

В метод `save` передаётся объект [UploadFile](https://fastapi.tiangolo.com/tutorial/request-files/#uploadfile){target="_blank"}, имя бакета и полный путь к файлу в хранилище (имя файла и префикс).
В результате возвращается объект `ObjectWriteResult` со всей информацией о сохранённом объекте.

#### Загрузка файла из хранилища

Получить файл из хранилища достаточно просто. В зависимости от бизнес-требований приложения можно использовать несколько вариантов получения файла из хранилища и выдачи его пользователю.

Например:

```python
from aiohttp import ClientSession
from aiofiles import tempfile
from starlette.responses import FileResponse

class MinioStorage:
    ...
    async def get_file(self, bucket: str, path: str) -> FileResponse:
        session = ClientSession()
        result = await self.client.get_object(bucket, path, session)
        result_bytes = await result.content.read()
        async with tempfile.NamedTemporaryFile(mode='w+b', suffix='.mp4', delete=False) as temp_file:
            await temp_file.write(result_bytes)
        return FileResponse(temp_file.name, media_type='video/mp4', filename='movie.mp4')
```

При таком подходе файл полностью скачивается из хранилища и отдается пользователю в виде [FileResponse](https://fastapi.tiangolo.com/advanced/custom-response/#fileresponse){target="_blank"}. Но это не самый удобный вариант: при большом размере файла пользователю придется ждать довольно долго.

Более оптимальный вариант — выдать пользователю объект [StreamingResponse](https://fastapi.tiangolo.com/advanced/custom-response/#using-streamingresponse-with-file-like-objects){target="_blank"}:

```python
from aiohttp import ClientSession
from starlette.responses import StreamingResponse

class MinioStorage:
    ...
    async def get_file(self, bucket: str, path: str) -> StreamingResponse:
        session = ClientSession()
        result = await self.client.get_object(bucket, path, session)
        
        async def s3_stream():
            async for chunk in result.content.iter_chunked(32 * 1024):
                yield chunk

        return StreamingResponse(
            content=s3_stream(),
            media_type='video/mp4',
            headers={'Content-Disposition': 'filename="movie.mp4"'}
        )
```

В таком случае FileAPI выступает в роли прокси-сервера между пользователем и S3-хранилищем.

Также можно выдавать пользователю подписанную ссылку — Presigned URL:

```python
from datetime import timedelta

class MinioStorage:
    ...
    async def get_presigned_url(self, bucket: str, path: str) -> str:
        return await self.client.get_presigned_url('GET', bucket, path, expires=timedelta(days=1),)
```

Presigned URL — это временная ссылка, по которой можно получить доступ к приватному файлу в хранилище. Сгенерировать такую ссылку может только тот, у кого есть ключи доступа (Access key и Secret key) от хранилища. Как правило, это владелец.

Работа с Presigned URL устроена так:

1. Владелец генерирует Presigned URL, задавая срок действия ссылки.
2. Владелец отправляет сгенерированную ссылку пользователям, которым хочет открыть доступ к файлу.
3. Пользователи получают ссылку вида:
`http://minio_storage:9000/files/GWSJL42dkwEznfzpcX2ZMD/movie.mp4?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=PQ0HIwZ7zJABTSFkjPNt%2F20230706%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Date=20230706T104636Z&X-Amz-Expires=86400&X-Amz-SignedHeaders=host&X-Amz-Signature=72cf5dd8e43dd7c966075395d5b9b58f05f84c348ac0dfaa73880dc226dc15e5`

   В ней содержится:
   * `http://minio_storage:9000/files/GWSJL42dkwEznfzpcX2ZMD/movie.mp4` — путь до файла в бакете.
   * `X-Amz-Algorithm=AWS4-HMAC-SHA256` — алгоритм шифрования, который использовался для создания подписи в ссылке.
   * `X-Amz-Credential=PQ0HIwZ7zJABTSFkjPNt%2F20230706%2Fus-east-1%2Fs3%2Faws4_request` — дополнительная информация о запросе (регион, время).
   * `X-Amz-Date=20230706T104636Z` — время создания ссылки.
   * `X-Amz-Expires=86400` — продолжительность действия ссылки в секундах.
   * `X-Amz-SignedHeaders=host` — HTTP-заголовки, которые будут добавлены в запрос по ссылке.
   * `X-Amz-Signature=72cf5dd8e43dd7c966075395d5b9b58f05f84c348ac0dfaa73880dc226dc15e5` — подпись, которая даёт пользователю доступ к объекту по ссылке.
     
5. Получив такую ссылку, пользователи смогут посмотреть и скачать файл в течение срока действия ссылки, который задал владелец.
6. Когда время действия ссылки истечёт, доступ будет аннулирован. При переходе по ссылке пользователи увидят ошибку `AccessDenied` — Отказано в доступе.

![image](images/access_denied_fin.png)

В Presigned URL не заложена проверка подлинности получателя. Это значит, что доступ к файлу будет у всех пользователей, к которым попала действующая временная ссылка. Например, если один из пользователей, которому вы прислали ссылку, перешлёт её другому человеку, тот тоже сможет просмотреть и скачать файл.
