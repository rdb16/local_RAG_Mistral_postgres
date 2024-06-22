import psycopg as pg
import pgvector
from pgvector.psycopg import register_vector


def check_pg(conf: dict) -> bool:
    connection_string = conf['IMAC_CONNECTION_STRING'] + "postgres"
    try:
        pg.connect(connection_string)
        return True
    except pg.Error as e:
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
    try:
        table_create_command = """
                CREATE TABLE IF NOT EXISTS embeddings (
                    id bigserial primary key,
                    fk_pdf_file bigserial not null,                    
                    document_type text default 'NONE',
                    ids text,
                    content text,
                    tokens integer,
                    embedding vector(1536)
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
                    file_date text,
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


def insert_into_pdf(conf: dict, dbname: str, values: dict):
    connection_string = conf['IMAC_CONNECTION_STRING'] + dbname
    conn = pg.connect(connection_string)
    cur = conn.cursor()
    try:
        table_insert_command = """
        INSERT INTO pdf_file (file_name, document_type, file_date, sha1) 
        VALUES (values["file_name"], values["document_type"], values["file_date"], values["sha1"])
        
        """

    except pg.Error as e:
        print("ERROR : ", e)
        return False
    finally:
        cur.close()
        conn.close()


def general(conf: dict, dbname: str) -> bool:
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
    result = create_table(conf, dbname)
    if result:
        print("La table embeddings existe.")
    else:
        print("La table embeddings n'a pa pu être crée, on sort")
        exit(1)
