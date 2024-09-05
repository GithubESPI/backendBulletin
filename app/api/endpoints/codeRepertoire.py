from fastapi import APIRouter, HTTPException
from app.services.api_service import fetch_api_data
from app.core.config import settings

router = APIRouter()

@router.get("/")
async def get_repertoires():
    endpoint_repertoires = "/r/v1/document/repertoires-apprenant"
    url_repertoires = f"{settings.YPAERO_BASE_URL}{endpoint_repertoires}"
    headers = {
        "X-Auth-Token": settings.YPAERO_API_TOKEN,
        "Content-Type": "application/json"
    }
    try:
        # Utiliser un service pour appeler l'API et récupérer les données
        repertoires_data = await fetch_api_data(url_repertoires, headers)
        return repertoires_data
    except HTTPException as http_exc:
        # Vous pouvez gérer les erreurs spécifiques ici si nécessaire
        raise http_exc
    except Exception as exc:
        # Gestion des erreurs non spécifiques
        raise HTTPException(status_code=500, detail=str(exc))
