from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from django.conf import settings

# Définit le module de configuration par défaut de Django pour le programme 'celery'.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mybackend.settings')

app = Celery('mybackend')
app.config_from_object(settings, namespace='CELERY')

# Charge les modules de tâches à partir de toutes les configurations d'applications Django enregistrées.
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
