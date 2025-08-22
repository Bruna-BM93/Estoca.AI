from http import HTTPStatus
import uvicorn

from fastapi import FastAPI

from routers.routers_chat import chat
from mongodb_database import mongo_client

app = FastAPI()

@app.get('/', status_code=HTTPStatus.OK)
def read_root():
    return {'message': 'Hello World!'}


app.include_router(chat.router)

mongo_client.admin.command('ping')

if __name__ == "__main__":
    uvicorn.run("app:app", host="127.0.0.1", port=5002, reload=True)
