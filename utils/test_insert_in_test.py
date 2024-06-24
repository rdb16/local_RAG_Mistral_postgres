import psycopg
from utils import load_env

conf = load_env.load('../config/config.json')
data_path = conf['DATA_PATH']
dbname = data_path.replace("./data-", "base_")

# connection
conn_string = conf['IMAC_CONNECTION_STRING'] + dbname
conn = psycopg.connect(conn_string)
ids = "filexxx.pdf:1:1"
fk = 23

statement = """
            INSERT INTO embeddings (fk_pdf_file, ids, content, tokens )
            VALUES (%s, %s, %s, %s)   
        """
values = (fk, ids, "Encore du texte bidon bidond (bidon) abaracadabrant", 640 )
print(statement)
conn.execute(statement, values)
conn.commit()

conn.close()
