import uvicorn
from fastapi import FastAPI
from mongodb_database import mongo_client
from routers.routers_chat import chat
from routers import router_db_config

app = FastAPI(title="Estoque.AI")

app.include_router(chat.router)
app.include_router(router_db_config.router_config)

mongo_client.admin.command('ping')

if __name__ == '__main__':
    uvicorn.run('app:app', host='127.0.0.1', port=8000, reload=True)
