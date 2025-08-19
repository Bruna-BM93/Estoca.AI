from http import HTTPStatus
import requests
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("API_ERP")

# 1️⃣ Obter o access_token usando o personal_token
auth_url = "https://api.egestor.com.br/api/oauth/access_token"
auth_body = {
    "grant_type": "personal",
    "personal_token": API_KEY
}

auth_response = requests.post(auth_url, json=auth_body)
auth_response.raise_for_status()

token_data = auth_response.json()
access_token = token_data.get("access_token")

if not access_token:
    raise ValueError("Não foi possível obter o access_token. Verifique sua chave API.")

# 2️⃣ Usar o access_token para acessar os produtos
produtos_url = "https://v4.egestor.com.br/api/v1/produtos?filtro=Armario%de%Cozinha"
headers = {
    "Authorization": f"Bearer {access_token}"
}

response = requests.get(produtos_url, headers=headers)
response.raise_for_status()

if response.status_code == HTTPStatus.OK:
    print(response.json())
else:
    print(f"Erro: {response.status_code} - {response.text}")