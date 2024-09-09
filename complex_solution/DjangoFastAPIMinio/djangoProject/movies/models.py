import uuid

from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models import FileField
from django.utils.translation import gettext_lazy as _
from storages.backends.s3boto3 import S3Boto3Storage

from movies.storages import CustomStorage


class UUIDMixin(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)

    class Meta:
        abstract = True


class TimeStampedMixin(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class FilmWork(UUIDMixin, TimeStampedMixin):
    class Type(models.TextChoices):
        MOVIE = 'movie'
        TV_SHOW = 'tv_show'

    title = models.CharField(_('title'), max_length=255)
    description = models.TextField(_('description'), blank=True)
    creation_date = models.DateField(_('creation_date'), blank=True)
    rating = models.FloatField(blank=True, validators=[MinValueValidator(0), MaxValueValidator(100)])
    type = models.CharField(_('type'), choices=Type.choices, max_length=10)
    file = FileField(storage=CustomStorage(), null=True)
    # file = FileField(storage=S3Boto3Storage(), null=True)

    class Meta:
        db_table = 'film_work'
        verbose_name = _('Movie')
        verbose_name_plural = _('Movies')

    def __str__(self):
        return self.title
