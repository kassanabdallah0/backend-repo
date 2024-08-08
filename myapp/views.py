# fileupload/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .tasks import assemble_chunks
from .models import FileUploadSession, FileChunk

@method_decorator(csrf_exempt, name='dispatch')
class UploadChunk(APIView):
    parser_classes = [MultiPartParser]

    def post(self, request):
        session_id = request.data['sessionId']
        chunk_number = request.data['chunkNumber']
        chunk = request.data['chunk']

        session, created = FileUploadSession.objects.get_or_create(
            session_id=session_id,
            defaults={'file_name': request.data.get('fileName', '')}
        )

        FileChunk.objects.create(session=session, chunk_number=chunk_number, chunk_data=chunk.read())

        return Response({'status': 'chunk uploaded'})

@method_decorator(csrf_exempt, name='dispatch')
class CompleteUpload(APIView):

    def post(self, request):
        session_id = request.data['sessionId']
        session = FileUploadSession.objects.get(session_id=session_id)
        print(session.is_complete)
        if not session.is_complete:
            print(f'CompleteUpload : {session_id} and {session.file_name}')
            assemble_chunks.delay(session_id, session.file_name)
        print(2)
        return Response({'status': 'file assembly task started'})

from django.http import JsonResponse
from .tasks import add

@csrf_exempt
def test_celery(request):
    result = add.delay()
    return JsonResponse({'task_id': result.id})
