import logging
from app.api.endpoints import apprenants, groupes, absences, uploads, importBulletin, codeRepertoire
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Configurer le logger pour la production
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Ajouter la middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://bulletin.groupe-espi.fr"],  # Remplacer par l'URL de ton frontend
    allow_credentials=True,
    allow_methods=["*"],  # Autorise toutes les méthodes HTTP (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Autorise tous les en-têtes
)

# Inclusion des routes des différents modules
app.include_router(apprenants.router, prefix="/apprenants", tags=["apprenants"])
app.include_router(groupes.router, prefix="/groupes", tags=["groupes"])
app.include_router(absences.router, prefix="/absences", tags=["absences"])
app.include_router(uploads.router, prefix="", tags=["uploads"])  # Uploads sans préfixe
app.include_router(importBulletin.router, prefix="/importBulletins", tags=["importBulletins"])
app.include_router(codeRepertoire.router, prefix="/codeRepertoire", tags=["codeRepertoire"])

# Pour lancer l'application en production, utilisez la commande suivante :
# gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app