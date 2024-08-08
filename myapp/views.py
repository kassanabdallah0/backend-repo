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

@method_decorator(csrf_exempt, name='dispatch')
class UploadChunk(APIView):
    parser_classes = [MultiPartParser]

    def post(self, request):
        session_id = request.data['sessionId']
        chunk_number = request.data['chunkNumber']
        chunk = request.data['chunk']

        session, created = FileUploadSession.objects.get_or_create(
            session_id=session_id,
            defaults={'file_name': request.data.get('fileName', ''), 'total_chunks': request.data.get('totalChunks')}
        )

        FileChunk.objects.create(session=session, chunk_number=chunk_number, chunk_data=chunk.read())

        return Response({'status': 'chunk uploaded'})

@method_decorator(csrf_exempt, name='dispatch')
class CompleteUpload(APIView):

    def post(self, request):
        session_id = request.data['sessionId']
        session = FileUploadSession.objects.get(session_id=session_id)
        if not session.is_complete:
            session.assembly_status = 'in_progress'
            session.save()
            assemble_chunks.delay(session_id, session.file_name)
        return Response({'status': 'file assembly task started'})

class AssemblyStatus(APIView):
    def get(self, request, session_id):
        try:
            session = FileUploadSession.objects.get(session_id=session_id)
            return Response({'status': session.assembly_status})
        except FileUploadSession.DoesNotExist:
            return Response({'status': 'error', 'message': 'Session not found'}, status=404)

@method_decorator(csrf_exempt, name='dispatch')
class ListCompletedUploads(APIView):

    def get(self, request):
        completed_uploads = FileUploadSession.objects.filter(is_complete=True).values(
            'session_id', 'file_name', 'user_id', 'total_chunks', 'date_uploaded'
        )
        return Response(list(completed_uploads))
    
@method_decorator(csrf_exempt, name='dispatch')
class DeleteUpload(APIView):

    def delete(self, request, session_id):
        try:
            session = FileUploadSession.objects.get(session_id=session_id)
            # Delete file from storage
            base_name, ext = os.path.splitext(session.file_name)
            file_path = os.path.join(settings.MEDIA_ROOT, 'largefiles' ,f'{base_name}{ext}')
            if os.path.exists(file_path):
                os.remove(file_path)
            # Delete related chunks
            FileChunk.objects.filter(session=session).delete()
            FileUploadSession.objects.filter(session_id =session_id ).delete()
            # Delete session record
            session.delete()
            return Response({'status': f'file deleted successfully path : {file_path}'}, status=status.HTTP_200_OK)
        except FileUploadSession.DoesNotExist:
            return Response({'status': 'error', 'message': 'FileUploadSession not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'status': 'error', 'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
