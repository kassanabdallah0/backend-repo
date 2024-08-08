from django.db import models

class FileUploadSession(models.Model):
    session_id = models.CharField(max_length=100, unique=True)
    file_name = models.CharField(max_length=255)
    user_id = models.CharField(max_length=100, blank=True, null=True)  # Optional user_id
    total_chunks = models.IntegerField(default=0)  # Total number of chunks expected
    is_complete = models.BooleanField(default=False)
    assembly_status = models.CharField(max_length=20, default='pending')  # pending, in_progress, completed, failed
    date_uploaded = models.DateTimeField(auto_now_add=True)  # Date of uploading

    def __str__(self):
        return f'{self.file_name} ({self.session_id})'

class FileChunk(models.Model):
    session = models.ForeignKey(FileUploadSession, on_delete=models.CASCADE)
    chunk_number = models.IntegerField()
    chunk_data = models.BinaryField()
    upload_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Chunk {self.chunk_number} of {self.session.file_name}'
