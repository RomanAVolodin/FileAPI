# Файловое хранилище

В вашем кинотеатре уже создана административная панель для сотрудников компании: там они могут добавлять информацию о фильмах. Также есть ETL-сервис, перекладывающий и обновляющий информацию о фильмах в ElasticSearch. А ещё готов к эксплуатации сервис выдачи контента, дающий пользователю информацию о фильмах, жанрах и персонах.

Но не хватает самого главного – фильмов! И в этом разделе мы решим эту проблему.

## Локальное файловое хранилище

Одно из первых решений, которые приходят в голову, — использование в Django-админке [FileField](https://docs.djangoproject.com/en/4.2/ref/models/fields/#filefield){target="_blank"}.
Достаточно добавить одно поле в модель кинопроизведения, и дело сделано.

```python
class FilmWork(UUIDMixin, TimeStampedMixin):
    class Type(models.TextChoices):
        MOVIE = 'movie'
        TV_SHOW = 'tv_show'

    title = models.CharField(_('title'), max_length=255)
    description = models.TextField(_('description'), blank=True)
    creation_date = models.DateField(_('creation_date'), blank=True)
    rating = models.FloatField(blank=True, validators=[MinValueValidator(0), MaxValueValidator(100)])
    type = models.CharField(_('type'), choices=Type.choices, max_length=10)
    
    # файл будет загружен в папку MEDIA_ROOT/uploads
    # https://docs.djangoproject.com/en/4.2/ref/settings/#media-root
    file = FileField(upload_to='uploads/', null=True)

    class Meta:
        db_table = 'film_work'
        verbose_name = _('Movie')
        verbose_name_plural = _('Movies')

    def __str__(self):
        return self.title
```

При добавлении или редактировании кинопроизведения в административной панели появится необходимое поле для загрузки файла.

![image](06_sprint/10_file_storages/images/film-django-admin_fin.png)

После этого остается лишь в `docker-compose.yaml` примонтировать [именованный том](https://docs.docker.com/storage/volumes/){target="_blank"} в папку `uploads` проекта и этот же том подключить к контейнеру с Nginx.

```yaml
services:
  gateway:
    image: nginx:latest 
    volumes:
      - ./conf.d:/etc/nginx/conf.d 
      - media_volume:/opt/app/uploads:ro 
    ports:
      - "80:80"
    depends_on:
      - api

  api:
    image: nginx:latest 
    volumes:
      - ./conf.d:/etc/nginx/conf.d 
      - media_volume:/app/uploads

volumes:
  media_volume:
```

Теперь необходимо сконфигурировать Nginx таким образом, чтобы все запросы к адресу, начинающемуся с `/uploads`, он перенаправлял в папку `/opt/app/uploads`, где расположены медиафайлы. Для этого в конфигурационный файл Nginx добавим следующее:

```nginx configuration
location /uploads { 
    alias /opt/app/uploads; 
} 
```

Готово! Этих шагов достаточно для работы с файлами через файловое хранилище. Можно предоставлять пользователям доступ к фильмам через Nginx, который будет выступать в роли балансировщика нагрузки.

Такой способ хранения файлов вполне рабочий и применяется на практике, но, как правило, в небольших проектах, либо для быстрого создания [MVP](https://ru.wikipedia.org/wiki/%D0%9C%D0%B8%D0%BD%D0%B8%D0%BC%D0%B0%D0%BB%D1%8C%D0%BD%D0%BE_%D0%B6%D0%B8%D0%B7%D0%BD%D0%B5%D1%81%D0%BF%D0%BE%D1%81%D0%BE%D0%B1%D0%BD%D1%8B%D0%B9_%D0%BF%D1%80%D0%BE%D0%B4%D1%83%D0%BA%D1%82){target="_blank"}. 

Всё дело в том, что у использованного в примере хранилища файлов есть несколько серьёзных недостатков:

* Не подходит для хранения большого объёма данных.
* Есть ограничения на размер файла и длину имени.
* Невозможно управлять одновременными подключениями с тысячи компьютеров.
* Нужно следить за исчерпанием объёма ресурсов.

Для больших проектов используются другие способы хранения файлов. Рассмотрим их подробнее уже в следующем уроке!
