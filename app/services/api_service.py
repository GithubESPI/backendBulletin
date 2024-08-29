import httpx
from fastapi import HTTPException
import logging
import requests

# Configure the logger
logger = logging.getLogger(__name__)

# Fonction pour enregistrer l'URL du fichier Excel dans la base de données
def save_generated_excel_url_to_db(user_id, excel_url):
    response = requests.post(
        'http://localhost:3000/api/documents',  # Remplacez par l'URL de base correcte
        json={
            'userId': user_id,
            'generatedExcelUrl': excel_url
        }
    )
    if response.status_code != 200:
        raise Exception(f"Failed to save Excel URL: {response.content}")

    
# Fonction asynchrone pour récupérer des données depuis une API
async def fetch_api_data(url: str, headers: dict):
    # Log le début de la récupération des données
    logger.debug(f"Fetching data from {url} with headers {headers}")
    
    # Utilisation d'un client HTTP asynchrone pour effectuer la requête
    async with httpx.AsyncClient(follow_redirects=True) as client:
        # Effectuer une requête GET avec un timeout de 60 secondes
        response = await client.get(url, headers=headers, timeout=60.0)
        
        # Vérifier le statut de la réponse
        if response.status_code != 200:
            # Log en cas d'échec de la requête
            logger.error(f"Failed to fetch data: {response.status_code} - {response.text}")
            # Lever une exception HTTP en cas de statut de réponse non-200
            raise HTTPException(status_code=response.status_code, detail=f"API call failed with status {response.status_code}")
        
        try:
            # Tenter de parser la réponse JSON
            data = response.json()
            # Log des données récupérées
            logger.debug(f"Fetched data: {data}")
            # Vérifier si les données sont de type liste ou dictionnaire
            if isinstance(data, (list, dict)):
                return data
            else:
                # Log en cas de données non conformes
                logger.error("Data is not a list or dict")
                return None
        except ValueError as e:
            # Log en cas d'erreur de parsing JSON
            logger.error(f"Error parsing JSON: {str(e)}")
            return None
