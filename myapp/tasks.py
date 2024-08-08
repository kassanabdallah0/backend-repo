from .models import FileChunk, FileUploadSession
import os
from celery import shared_task
import logging

logger = logging.getLogger(__name__)

@shared_task(bind=True)
def add(self, x=2, y=3):
    logger.info(f'Received task: {self.request.id}')
    result = x + y
    logger.info(f'Add task result: {result}')
    print(result)
    return result

@shared_task(bind=True)
def assemble_chunks(self, session_id, file_name):
    try:
        session = FileUploadSession.objects.get(session_id=session_id)
        # Split the file name and extension correctly
        base_name, ext = os.path.splitext(file_name)
        session_id_suffix = f'_{session_id}' if session_id else ''
        
        # Ensure the extension starts with a dot if not empty
        if ext and not ext.startswith('.'):
            ext = f'.{ext}'
        print(f'Base name : {base_name} \n Sessionidsuffix : {session_id_suffix} \n Type : {ext}')
        file_path = os.path.join('media', 'largefiles', f'{base_name}{session_id_suffix}{ext}')
        
        
        with open(file_path, 'wb') as f:
            chunks = FileChunk.objects.filter(session=session).order_by('chunk_number')
            for chunk in chunks:
                f.write(chunk.chunk_data)
        
        session.is_complete = True
        session.save()
        FileChunk.objects.filter(session=session).delete()
        logger.info(f'File assembly completed for session {session_id}')
        print("Done")
        return {'status': 'file assembled successfully'}
    
    except Exception as e:
        print("Error")
        logger.error(f'Error assembling file for session {session_id}: {e}')
        return {'status': 'error', 'error': str(e)}

