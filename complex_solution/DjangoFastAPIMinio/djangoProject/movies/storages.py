from django.core.files.storage import Storage
from django.core.files.uploadedfile import InMemoryUploadedFile
import requests


class CustomStorage(Storage):
    def _save(self, name, content: InMemoryUploadedFile):
        r = requests.post(
            'http://localhost:8001/api/v1/', files={'file': (content.name, content, content.content_type)}
        )
        return r.json().get('short_name')

    def url(self, name):
        return f'http://localhost:8001/api/v1/download-stream/{name}'

    def exists(self, name):
        return False
