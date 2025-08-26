import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

SB_URL = os.getenv('SB_URL')
SB_API_KEY = os.getenv('SB_API_KEY')
SB_PASSWORD = os.getenv('SB_PASSWORD')
SB_USER = os.getenv('SB_USER')
SB_DATABASE = os.getenv('SB_DATABASE')


conn_str = f"postgresql://postgres:{SB_PASSWORD}@db.fgmgldxhbtgghgkiuesi.supabase.co:5432/postgres"

conn = psycopg2.connect(conn_str, sslmode="require")  # SSL obrigatório
cur = conn.cursor()

cur.execute("SELECT version();")
print(cur.fetchone())

cur.close()
conn.close()



