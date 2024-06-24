import psycopg as pg
import pgvector
from pgvector.psycopg import register_vector


def check_pg(conf: dict) -> bool:
    connection_string = conf['IMAC_CONNECTION_STRING'] + "postgres"
    try:
        pg.connect(connection_string)
        return True
    except pg.Error:
        return False


def check_db(conf: dict, dbname: str) -> bool:
    connection_string = conf['IMAC_CONNECTION_STRING'] + "postgres"
    conn = pg.connect(connection_string)
    cur = conn.cursor()
    try:
        cur.execute("SELECT FROM pg_database WHERE datname = %s", (dbname,))
        if cur.fetchone() is None:
            return False
        else:
            return True
    finally:
        cur.close()
        conn.close()


def check_db_extension(conf: dict, dbname: str) -> bool:
    connection_string = conf['IMAC_CONNECTION_STRING'] + dbname
    # DEBUG
    print("connecting to", connection_string)
    conn = pg.connect(connection_string)
    cur = conn.cursor()
    try:
        cur.execute("CREATE EXTENSION IF NOT EXISTS vector")
        conn.commit()
        return True
    except pg.Error as e:
        print("ERROR : ", e)
        return False
    finally:
        cur.close()
        conn.close()


def create_db(conf: dict, dbname: str) -> bool:
    connection_string = conf['IMAC_CONNECTION_STRING'] + "postgres"
    conn = pg.connect(connection_string)
    conn.autocommit = True
    cur = conn.cursor()
    try:
        cur.execute(f"CREATE DATABASE {dbname}")
        return True
    except pg.Error as e:
        print("ERROR : ", e)
        return False
    finally:
        cur.close()
        conn.close()


def create_chunks_table(conf: dict, dbname: str) -> bool:
    connection_string = conf['IMAC_CONNECTION_STRING'] + dbname
    conn = pg.connect(connection_string)
    cur = conn.cursor()
    if conf["EMBEDDINGS_ENGINE"] == "us-east-1":
        dim = 1536
    elif conf["EMBEDDINGS_ENGINE"] == "eu-west-2":
        dim = 1024
    else:
        dim = 4096
    try:
        table_create_command = f"""
                CREATE TABLE IF NOT EXISTS embeddings (
                    id bigserial primary key,
                    fk_pdf_file bigserial not null,                    
                    ids text,
                    content text,
                    tokens integer,
                    embedding vector({dim})
                    );
                            """
        cur.execute(table_create_command)
        conn.commit()
        return True
    except pg.Error as e:
        print("ERROR : ", e)
        return False
    finally:
        cur.close()
        conn.close()


def create_pdf_table(conf: dict, dbname: str) -> bool:
    connection_string = conf['IMAC_CONNECTION_STRING'] + dbname
    conn = pg.connect(connection_string)
    cur = conn.cursor()
    try:
        table_create_command = """
                CREATE TABLE IF NOT EXISTS pdf_file (
                    id bigserial primary key,
                    file_name text not null,                    
                    document_type text default 'None',
                    file_date timestamp not null,
                    sha1 text                    
                    );
                            """
        cur.execute(table_create_command)
        conn.commit()
        return True
    except pg.Error as e:
        print("ERROR : ", e)
        return False
    finally:
        cur.close()
        conn.close()



def general(conf: dict, dbname: str):
    # Vérif que la base existe sinon la créer
    result = check_db(conf, dbname)
    if result:
        print(f"La Base {dbname} existe")
    else:
        print(f"La Base {dbname} est à créer.")
        result1 = create_db(conf, dbname)
        if result1:
            print(f"La base {dbname} a été crée ")
        else:
            print(f"La base {dbname} n'a pas pu être crée, on sort")
            exit(1)

    # vérification de l'extension et de l'existence de la base
    result = check_db_extension(conf, dbname)
    if result:
        print("La base possède bien l'extension vector.")
    else:
        print("La base n'a pas pu recevoir l'extension vector, on sort")
        exit(1)

    # vérifie que la table a été crée sinon la crée
    result = create_chunks_table(conf, dbname)
    if result:
        print("La table embeddings existe.")
    else:
        print("La table embeddings n'a pa pu être crée, on sort")
        exit(1)
