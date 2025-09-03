import uvicorn
from fastapi import FastAPI

from estoque_ai.mongodb_database import mongo_client
from estoque_ai.routers import router_db_config
from estoque_ai.routers.routers_chat import chat

app = FastAPI(title='Estoque.AI')

app.include_router(chat.router)
app.include_router(router_db_config.router_config)

mongo_client.admin.command('ping')

if __name__ == '__main__':
    uvicorn.run('app:app', host='127.0.0.1', port=8000, reload=True)
