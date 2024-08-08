from celery import shared_task
from .models import FileChunk, FileUploadSession
import os
import logging
from django.db import transaction

logger = logging.getLogger(__name__)

@shared_task(bind=True)
def assemble_chunks(self, session_id, file_name):
    try:
        with transaction.atomic():
            session = FileUploadSession.objects.select_for_update().get(session_id=session_id)
            session.assembly_status = 'in_progress'
            session.save()

            base_name, ext = os.path.splitext(file_name)
            session_id_suffix = f'_{session_id}' if session_id else ''

            if ext and not ext.startswith('.'):
                ext = f'.{ext}'
            file_path = os.path.join('media', 'largefiles', f'{base_name}{session_id_suffix}{ext}')

            with open(file_path, 'wb') as f:
                chunks = FileChunk.objects.filter(session=session).order_by('chunk_number')
                for chunk in chunks:
                    f.write(chunk.chunk_data)

            session.is_complete = True
            session.assembly_status = 'completed'
            session.file_name = f'{base_name}{session_id_suffix}{ext}'
            session.save()
            FileChunk.objects.filter(session=session).delete()
            logger.info(f'File assembly completed for session {session_id}')
            return {'status': 'file assembled successfully'}

    except Exception as e:
        session.assembly_status = 'failed'
        session.save()
        logger.error(f'Error assembling file for session {session_id}: {e}')
        return {'status': 'error', 'error': str(e)}
