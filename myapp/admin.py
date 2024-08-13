from django.contrib import admin
from .models import FileUploadSession, FileChunk

# Enregistrer le modèle FileUploadSession avec la configuration personnalisée de l'administrateur
@admin.register(FileUploadSession)
class FileUploadSessionAdmin(admin.ModelAdmin):
    """
    Options de l'interface d'administration pour le modèle FileUploadSession.
    
    Attributs :
        list_display (tuple) : Champs à afficher dans la vue en liste de l'administrateur.
        search_fields (tuple) : Champs pouvant faire l'objet d'une recherche dans l'interface d'administration.
        list_filter (tuple) : Champs permettant de filtrer la vue de la liste.
    """
    list_display = ('session_id', 'file_name', 'user_id', 'total_chunks', 'is_complete', 'date_uploaded', 'file_size')
    search_fields = ('session_id', 'file_name', 'user_id')
    list_filter = ('is_complete',)

# Enregistrer le modèle FileChunk avec une configuration d'administration personnalisée
@admin.register(FileChunk)
class FileChunkAdmin(admin.ModelAdmin):
    """
    Options de l'interface d'administration pour le modèle FileChunk.
    
    Attributs :
        list_display (tuple) : Champs à afficher dans la vue en liste de l'administrateur.
        search_fields (tuple) : Champs pouvant faire l'objet d'une recherche dans l'interface d'administration.
        list_filter (tuple) : Champs permettant de filtrer la vue de la liste.
    """
    list_display = ('session', 'chunk_number', 'upload_time')
    search_fields = ('session__session_id', 'session__file_name')
    list_filter = ('upload_time',)
