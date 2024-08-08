from django.contrib import admin
from .models import FileUploadSession, FileChunk

@admin.register(FileUploadSession)
class FileUploadSessionAdmin(admin.ModelAdmin):
    list_display = ('session_id', 'file_name', 'user_id', 'total_chunks', 'is_complete','date_uploaded','file_size')
    search_fields = ('session_id', 'file_name', 'user_id')
    list_filter = ('is_complete',)

@admin.register(FileChunk)
class FileChunkAdmin(admin.ModelAdmin):
    list_display = ('session', 'chunk_number', 'upload_time')
    search_fields = ('session__session_id', 'session__file_name')
    list_filter = ('upload_time',)
