import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from estoque_ai.mongodb_database import mongo_client
from estoque_ai.routers import router_db_config
from estoque_ai.routers.routers_chat import chat

app = FastAPI(title='Estoque.AI')

# habilitar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # pode trocar "*" por ["http://localhost:3000"] se quiser limitar
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router)
app.include_router(router_db_config.router_config)

mongo_client.admin.command('ping')

if __name__ == '__main__':
    uvicorn.run('app:app', host='0.0.0.0', port=8000, reload=True)


@app.get("/ping")
async def ping():
    return {"message": "pong"}
