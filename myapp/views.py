from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .tasks import assemble_chunks
from .models import FileUploadSession, FileChunk
import os 
from django.conf import settings

# This decorator exempts the view from CSRF verification.
@method_decorator(csrf_exempt, name='dispatch')
class UploadChunk(APIView):
    """
    API view to handle uploading file chunks.
    """
    # Use MultiPartParser to handle file uploads
    parser_classes = [MultiPartParser]

    def post(self, request):
        """
        Handle POST requests to upload file chunks.

        This method processes individual chunks of a file upload, saving them
        to the database and updating the file upload session information.
        """
        # Extract data from the request
        session_id = request.data['sessionId']
        chunk_number = request.data['chunkNumber']
        chunk = request.data['chunk']
        file_name = request.data.get('fileName', '')
        total_chunks = request.data.get('totalChunks', 0)
        file_size = request.data.get('fileSize', 0)  # Get file size

        # Retrieve or create the file upload session
        session, created = FileUploadSession.objects.get_or_create(
            session_id=session_id,
            defaults={'file_name': file_name, 'total_chunks': total_chunks, 'file_size': file_size}
        )

        if not created:
            # Update the session information if it was not set initially
            session.total_chunks = total_chunks
            session.file_name = file_name
            session.file_size = file_size
            session.save()

        # Save the file chunk to the database
        FileChunk.objects.create(session=session, chunk_number=chunk_number, chunk_data=chunk.read())

        # Return a success response
        return Response({'status': 'chunk uploaded'})

# This decorator exempts the view from CSRF verification.
@method_decorator(csrf_exempt, name='dispatch')
class CompleteUpload(APIView):
    """
    API view to mark the completion of a file upload.
    """

    def post(self, request):
        """
        Handle POST requests to mark the completion of a file upload.

        This method updates the file upload session to indicate that the
        file assembly process has started.
        """
        # Extract the session ID from the request
        session_id = request.data['sessionId']

        # Retrieve the file upload session
        session = FileUploadSession.objects.get(session_id=session_id)

        if not session.is_complete:
            # Update the assembly status and save the session
            session.assembly_status = 'in_progress'
            session.save()

            # Start the asynchronous task to assemble the file chunks
            assemble_chunks.delay(session_id, session.file_name)

        # Return a response indicating that the file assembly task has started
        return Response({'status': 'file assembly task started'})

class AssemblyStatus(APIView):
    """
    API view to check the assembly status of a file upload.
    """

    def get(self, request, session_id):
        """
        Handle GET requests to check the assembly status of a file upload.

        This method retrieves the assembly status of a specific file upload session.
        """
        try:
            # Retrieve the file upload session
            session = FileUploadSession.objects.get(session_id=session_id)

            # Return the assembly status
            return Response({'status': session.assembly_status})
        
        except FileUploadSession.DoesNotExist:
            # Return an error response if the session is not found
            return Response({'status': 'error', 'message': 'Session not found'}, status=404)

# This decorator exempts the view from CSRF verification.
@method_decorator(csrf_exempt, name='dispatch')
class ListCompletedUploads(APIView):
    """
    API view to list all completed file uploads.
    """

    def get(self, request):
        """
        Handle GET requests to retrieve a list of completed file uploads.

        This method queries the FileUploadSession model for entries where
        the upload is marked as complete. It returns a list of these entries
        with specific fields.
        """
        # Query the database for completed file uploads
        completed_uploads = FileUploadSession.objects.filter(is_complete=True).values(
            'session_id',     # Unique session identifier
            'file_name',      # Name of the uploaded file
            'user_id',        # Identifier for the user who uploaded the file (optional)
            'total_chunks',   # Total number of chunks the file was divided into
            'date_uploaded',  # Date when the file was uploaded
            'file_size'       # Size of the uploaded file
        )
        
        # Return the list of completed uploads in the response
        return Response(list(completed_uploads))
    
# This decorator exempts the view from CSRF verification.
@method_decorator(csrf_exempt, name='dispatch')
class DeleteUpload(APIView):
    """
    API view to delete a file upload session and its associated data.
    """

    def delete(self, request, session_id):
        """
        Handle DELETE requests to delete a file upload session.

        This method retrieves the file upload session by session_id, deletes
        the associated file from storage, removes related file chunks, and 
        deletes the session record from the database.
        """
        try:
            # Retrieve the file upload session by session_id
            session = FileUploadSession.objects.get(session_id=session_id)

            # Construct the file path
            base_name, ext = os.path.splitext(session.file_name)
            file_path = os.path.join(settings.MEDIA_ROOT, 'largefiles', f'{base_name}{ext}')
            
            # Delete the file from storage if it exists
            if os.path.exists(file_path):
                os.remove(file_path)
            
            # Delete related file chunks from the database
            FileChunk.objects.filter(session=session).delete()
            
            # Delete the file upload session record from the database
            session.delete()
            
            # Return a success response
            return Response({'status': f'file deleted successfully path: {file_path}'}, status=status.HTTP_200_OK)
        
        # Handle the case where the session does not exist
        except FileUploadSession.DoesNotExist:
            return Response({'status': 'error', 'message': 'FileUploadSession not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Handle any other exceptions
        except Exception as e:
            return Response({'status': 'error', 'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)