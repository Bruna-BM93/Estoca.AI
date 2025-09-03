import os

import psycopg2
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv('SUPABASE_HOST')  # ex: db.xxxxx.supabase.co
DB_PORT = os.getenv('SUPABASE_PORT', '5432')
DB_NAME = os.getenv('SUPABASE_DB')
DB_USER = os.getenv('SUPABASE_USER')
DB_PASS = os.getenv('SUPABASE_PASS')


def get_conn():
    return psycopg2.connect(host=DB_HOST, port=DB_PORT, dbname=DB_NAME, user=DB_USER, password=DB_PASS, sslmode='require')
