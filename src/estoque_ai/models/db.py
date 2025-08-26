from src.estoque_ai.models.models_database import get_conn

def create_table():
    conn = get_conn()
    cur = conn.cursor()

    sql = """
    create table if not exists public.configs (
        id text primary key,
        api_key text not null,
        doc text not null,
        created_at timestamptz not null default now(),
        updated_at timestamptz not null default now()
    );
    """

    try:
        cur.execute(sql)
        conn.commit()
        print("✅ Tabela 'configs' criada (ou já existia).")
    except Exception as e:
        conn.rollback()
        print("❌ Erro ao criar tabela:", e)
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    create_table()
