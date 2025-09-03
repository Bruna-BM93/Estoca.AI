import psycopg

conn = psycopg.connect(
    host='127.0.0.1',
    port=5456,
    dbname='teste',
    user='teste',
    password='teste',
)
print('Connected!')
conn.close()
