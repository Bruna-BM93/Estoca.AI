from langchain.prompts import PromptTemplate
from langchain.schema import HumanMessage

import requests
import json
import os
from dotenv import load_dotenv

from models import llm_groq
from filter_checker import filter_validator

load_dotenv()
API_KEY = os.getenv("API_EGESTOR")
auth_url = os.getenv("AUTH_URL")

template = """

"""


def route_executor(rota):

    # Obter o access_token usando o personal_token
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




def final_responder():
    ...