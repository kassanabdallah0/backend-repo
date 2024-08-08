from django.urls import path
from .views import UploadChunk, CompleteUpload, test_celery

urlpatterns = [
    path('upload_chunk/', UploadChunk.as_view(), name='upload_chunk'),
    path('complete_upload/', CompleteUpload.as_view(), name='complete_upload'),
    path('test_celery/', test_celery, name='test_celery'),
]