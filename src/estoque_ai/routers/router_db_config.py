from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from src.estoque_ai.models.models_database import get_conn

router_config = APIRouter(prefix='/config', tags=['Configurações'])


class ConfigIn(BaseModel):
    apikey: str
    doc: str


class ConfigOut(BaseModel):
    apikey: str
    doc: str


@router_config.post('/', response_model=dict)
def save_config(cfg: ConfigIn):
    conn = get_conn()
    cur = conn.cursor()

    try:
        cur.execute(
            """
            insert into configs (id, api_key, doc)
            values ('singleton', %s, %s)
            on conflict (id) do update set
                api_key = excluded.api_key,
                doc = excluded.doc,
                updated_at = now()
        """,
            (cfg.apikey, cfg.doc),
        )
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise HTTPException(500, detail=f'Erro ao salvar config: {e}')
    finally:
        cur.close()
        conn.close()

    return {'status': 'ok', 'message': 'Configuração salva com sucesso'}


@router_config.get('/', response_model=ConfigOut)
def get_config():
    conn = get_conn()
    cur = conn.cursor()

    try:
        cur.execute("select api_key, doc from configs where id = 'singleton'")
        row = cur.fetchone()
        if not row:
            raise HTTPException(404, detail='Configuração não encontrada')
    finally:
        cur.close()
        conn.close()

    return ConfigOut(apikey=row[0], doc=row[1])
