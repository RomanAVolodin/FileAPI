# Generated by Django 4.2.2 on 2023-06-21 13:11

from django.db import migrations, models
import movies.storages


class Migration(migrations.Migration):

    dependencies = [
        ('movies', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='filmwork',
            name='file',
            field=models.FileField(null=True, storage=movies.storages.CustomStorage(), upload_to=''),
        ),
    ]
