from django.urls import path
from .views import UploadChunk, CompleteUpload, AssemblyStatus, ListCompletedUploads, DeleteUpload

urlpatterns = [
    path('upload_chunk/', UploadChunk.as_view(), name='upload_chunk'),
    path('complete_upload/', CompleteUpload.as_view(), name='complete_upload'),
    path('assembly_status/<str:session_id>/', AssemblyStatus.as_view(), name='assembly_status'),
    path('list_completed_uploads/', ListCompletedUploads.as_view(), name='list_completed_uploads'),
    path('delete_upload/<str:session_id>/', DeleteUpload.as_view(), name='delete_upload'),
]
