import psycopg as pg


def insert(conf: dict, dbname: str, values: dict):
    connection_string = conf['CONNECTION_STRING'] + dbname
    conn = pg.connect(connection_string)
    cur = conn.cursor()
    try:
        table_insert_command = f"""
        INSERT INTO inserted_file (file_name, document_type, file_date, sha1) 
        VALUES ('{values["file_name"]}', '{values["document_type"]}', '{values["file_date"]}', '{values["sha1"]}')
        RETURNING id;
        """
        print("sql : ", table_insert_command)
        cur.execute(table_insert_command)
        fk_inserted_file = cur.fetchone()[0]
        conn.commit()
        return fk_inserted_file

    except pg.Error as e:
        print("ERROR : ", e)
        return False
    finally:
        cur.close()
        conn.close()
