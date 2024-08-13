from celery import shared_task
from .models import FileChunk, FileUploadSession
import os
import logging
from django.db import transaction

# Initialize the logger
logger = logging.getLogger(__name__)

@shared_task(bind=True)
def assemble_chunks(self, session_id, file_name):
    """
    Celery task to assemble file chunks into a complete file.

    This task retrieves the file upload session and its associated chunks,
    assembles the chunks into a complete file, updates the session status,
    and deletes the chunk data from the database.
    
    Args:
        self: Reference to the current task instance.
        session_id (str): The ID of the file upload session.
        file_name (str): The name of the file being uploaded.
    
    Returns:
        dict: A status message indicating the result of the task.
    """
    try:
        # Use a database transaction to ensure atomicity
        with transaction.atomic():
            # Lock the session row for update to prevent concurrent modifications
            session = FileUploadSession.objects.select_for_update().get(session_id=session_id)
            
            # Update the assembly status to 'in_progress'
            session.assembly_status = 'in_progress'
            session.save()

            # Split the file name and extension correctly
            base_name, ext = os.path.splitext(file_name)
            session_id_suffix = f'_{session_id}' if session_id else ''

            # Ensure the extension starts with a dot if not empty
            if ext and not ext.startswith('.'):
                ext = f'.{ext}'

            # Construct the file path
            file_path = os.path.join('media', 'largefiles', f'{base_name}{session_id_suffix}{ext}')

            # Open the file for writing in binary mode
            with open(file_path, 'wb') as f:
                # Retrieve and order the file chunks
                chunks = FileChunk.objects.filter(session=session).order_by('chunk_number')
                for chunk in chunks:
                    # Write each chunk to the file
                    f.write(chunk.chunk_data)

            # Update the session to mark it as complete and set the final file name
            session.is_complete = True
            session.assembly_status = 'completed'
            session.file_name = f'{base_name}{session_id_suffix}{ext}'
            session.save()

            # Delete the file chunks from the database
            FileChunk.objects.filter(session=session).delete()

            # Log the successful completion
            logger.info(f'File assembly completed for session {session_id}')
            return {'status': 'file assembled successfully'}

    except Exception as e:
        # Handle any exceptions, updating the session status to 'failed'
        session.assembly_status = 'failed'
        session.save()

        # Log the error
        logger.error(f'Error assembling file for session {session_id}: {e}')
        return {'status': 'error', 'error': str(e)}
