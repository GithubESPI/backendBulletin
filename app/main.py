import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import apprenants, groupes, absences, uploads, importBulletin

# Configurer le logger
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = FastAPI()

# Ajouter le middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Autorise toutes les origines
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(apprenants.router, prefix="/apprenants", tags=["apprenants"])
app.include_router(groupes.router, prefix="/groupes", tags=["groupes"])
app.include_router(absences.router, prefix="/absences", tags=["absences"])
app.include_router(uploads.router, prefix="", tags=["uploads"])
app.include_router(importBulletin.router, prefix="", tags=["import"])

#uvicorn app.main:app --reload