EOL > README.md
# Backend pour le Téléchargement de Fichiers Volumineux

Ce projet est un backend développé avec Django, Celery, Redis, et PostgreSQL, conçu pour gérer le téléchargement de fichiers volumineux en plusieurs morceaux. Il supporte également l'assemblage des fichiers en arrière-plan.

## Table des Matières

| Section                     | Description                                                       |
|-----------------------------|-------------------------------------------------------------------|
| [Fonctionnalités](#fonctionnalités)  | Fonctionnalités principales du projet                                 |
| [Prérequis](#prérequis)                | Logiciels et outils nécessaires pour installer et exécuter le projet |
| [Installation](#installation)            | Instructions pour installer et configurer le projet                   |
| [API Endpoints](#api-endpoints)          | Liste des endpoints disponibles pour interagir avec l'API            |
| [Technologies Utilisées](#technologies-utilisées) | Technologies employées dans le projet                                 |

## Fonctionnalités

| Fonctionnalité                             | Description                                                                 |
|--------------------------------------------|-----------------------------------------------------------------------------|
| Téléchargement de fichiers en morceaux     | Supporte les téléchargements de fichiers volumineux en les divisant en morceaux |
| Traitement asynchrone                      | Utilise Celery pour assembler les morceaux de fichiers en arrière-plan      |
| Interface d'administration Django          | Permet de gérer les fichiers et leurs métadonnées via l'interface d'administration |

## Prérequis

- **Python 3.9+**
- **PostgreSQL**
- **Redis**
- **Virtualenv** (optionnel mais recommandé)

## Installation

### 1. Cloner le Dépôt

\`\`\`bash
git clone https://github.com/kassanabdallah0/backend-repo.git
cd backend-repo
\`\`\`

### 2. Créer un Environnement Virtuel et Installer les Dépendances

\`\`\`bash
python -m venv venv
source venv/bin/activate  # Sur Windows : \`venv\Scripts\activate\`
pip install -r requirements.txt
\`\`\`

### 3. Configurer PostgreSQL

- Créez une base de données PostgreSQL et un utilisateur :

\`\`\`sql
CREATE DATABASE largefileupload;
CREATE USER abdallah WITH PASSWORD '1230';
ALTER ROLE abdallah SET client_encoding TO 'utf8';
ALTER ROLE abdallah SET default_transaction_isolation TO 'read committed';
ALTER ROLE abdallah SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE largefileupload TO abdallah;
\`\`\`

### 4. Appliquer les Migrations

\`\`\`bash
python manage.py migrate
\`\`\`

### 5. Créer un Superutilisateur

\`\`\`bash
python manage.py createsuperuser
\`\`\`

### 6. Lancer le Serveur Django

\`\`\`bash
python manage.py runserver
\`\`\`

### 7. Lancer Celery

Pour traiter les tâches d'assemblage en arrière-plan, lancez Celery avec la commande suivante (sur Windows) :

\`\`\`bash
celery -A mybackend.celery worker --pool=solo -l info
\`\`\`

## API Endpoints

Le backend expose plusieurs endpoints API pour interagir avec le système de téléchargement de fichiers :

| Endpoint                                        | Description                                                                 |
|-------------------------------------------------|-----------------------------------------------------------------------------|
| \`/fileupload/upload_chunk/\`                     | Endpoint pour télécharger un morceau de fichier                             |
| \`/fileupload/complete_upload/\`                  | Endpoint pour marquer la fin du téléchargement et démarrer l'assemblage du fichier |
| \`/fileupload/assembly_status/<session_id>/\`     | Endpoint pour vérifier le statut de l'assemblage du fichier                 |
| \`/fileupload/list_completed_uploads/\`           | Endpoint pour lister tous les téléchargements de fichiers terminés          |
| \`/fileupload/delete_upload/<session_id>/\`       | Endpoint pour supprimer un fichier téléchargé et ses métadonnées associées  |

## Technologies Utilisées

| Technologie   | Description                                             |
|---------------|---------------------------------------------------------|
| Django        | Framework web utilisé pour le backend                    |
| Celery        | Utilisé pour le traitement des tâches en arrière-plan    |
| Redis         | Courtier de messages pour Celery                         |
| PostgreSQL    | Base de données utilisée pour stocker les métadonnées des fichiers |
