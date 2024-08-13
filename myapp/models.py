from django.db import models

class FileUploadSession(models.Model):
    """
    Model to represent a file upload session.
    
    Attributes:
        session_id (str): Unique identifier for the upload session.
        file_name (str): Name of the uploaded file.
        user_id (str, optional): Identifier for the user who uploaded the file.
        total_chunks (int): Total number of chunks expected for the file.
        is_complete (bool): Flag indicating whether the file upload is complete.
        assembly_status (str): Status of the file assembly process.
        date_uploaded (datetime): Date and time when the file was uploaded.
        file_size (int): Size of the uploaded file.
    """
    session_id = models.CharField(max_length=100, unique=True)
    file_name = models.CharField(max_length=255)
    user_id = models.CharField(max_length=100, blank=True, null=True)  # Optional user_id
    total_chunks = models.IntegerField(default=0)  # Total number of chunks expected
    is_complete = models.BooleanField(default=False)
    assembly_status = models.CharField(max_length=20, default='pending')  # pending, in_progress, completed, failed
    date_uploaded = models.DateTimeField(auto_now_add=True)  # Date of uploading
    file_size = models.BigIntegerField()  # Size of the uploaded file

    def __str__(self):
        return f'{self.file_name} ({self.session_id})'

class FileChunk(models.Model):
    """
    Model to represent a chunk of a file in an upload session.
    
    Attributes:
        session (ForeignKey): Reference to the FileUploadSession model.
        chunk_number (int): The sequential number of the chunk.
        chunk_data (binary): The binary data of the chunk.
        upload_time (datetime): The time when the chunk was uploaded.
    """
    session = models.ForeignKey(FileUploadSession, on_delete=models.CASCADE)
    chunk_number = models.IntegerField()
    chunk_data = models.BinaryField()
    upload_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Chunk {self.chunk_number} of {self.session.file_name}'
