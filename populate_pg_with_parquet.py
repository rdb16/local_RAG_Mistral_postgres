
import os
import time
from datetime import datetime

import pandas as pd

from utils import load_env, parquet_to_sql, init_db, insert_into_db
import psycopg as pg
from utils import parquet_date_and_sha1
from utils.file_list import get_files_from_data, get_filtered_list, get_file_list_from_db


def main():
    start_time = time.time()
    ###############################################################################
    # Setup your database to insert embeddings
    ###############################################################################

    # Get openAI api key by reading local .env file
    conf = load_env.load('config/config.json')
    data_path = conf['DATA_PATH']
    connection_string = conf['CONNECTION_STRING']

    dbname = init_db.check(conf)
    connection_string = conf['CONNECTION_STRING'] + dbname
    # lecture du fichier parquet
    # df = pd.read_parquet("hf://datasets/Cohere/movies/movies.parquet")

    # liste des fichiers à traiter:
    file_data_list = get_files_from_data(data_path, ".parquet")
    parquet_pg_list = get_file_list_from_db(conf, dbname)
    file_to_import = get_filtered_list(parquet_pg_list, file_data_list)
    print("Nombre de fichiers à importer :", len(file_to_import))

    if len(file_to_import) == 0:
        print("Rien à importer on sort")
        end_time = time.time()
        duration = (end_time - start_time) * 1000
        print("duration en ms: ", int(duration))
        exit(0)

    for filename in os.listdir(data_path):
        path = os.path.join(data_path, filename)
        print("le fichier parquet à traiter: ", path)

        # on calcule les champs d'insertion
        path_file = os.path.join(data_path, filename)
        file_date, sha1 = parquet_date_and_sha1.get_metadata(path_file)
        if not file_date:
            file_date = datetime.now()
        data_dico = {"file_name": path,
                     "file_date": file_date,
                     "document_type": "test",
                     "sha1": sha1
                     }

        # on insert dans la table inserted_file
        pk_parquet = insert_into_db.insert(conf, dbname, data_dico)

        # on crée la table movies avec son schéma
        sql = parquet_to_sql.create_sql(path)
        print(sql)

        # création de la table (sans vector)

        conn = pg.connect(connection_string)
        cur = conn.cursor()
        try:
            cur.execute(sql)
            conn.commit()
            cur.close()
        except pg.Error as e:
            print("ERROR : ", e)

        # nom de la table crée :
        table_created = path.split('/')[-1].replace('.parquet', '')

        # Maintenant on va insérer les data
        df = pd.read_parquet(path)
        with conn.cursor() as cur:
            placeholders = ','.join(['%s'] * len(df.columns))
            columns = ','.join(df.columns)
            sql = f"INSERT INTO {table_created} ({columns}) VALUES ({placeholders})"
            # cast est un mot réservé que l'on échappe sous postgres avec "doubles quotes
            sql = sql.replace('cast', '"cast"')

            try:
                for row in df.itertuples(index=False, name=None):
                    cur.execute(sql, row)
                    conn.commit()
            except pg.Error as e:
                print("ERROR : ", e)
            finally:
                conn.close()

    ###############################################################################
    end_time = time.time()
    duration = (end_time - start_time) * 1000
    print("durée écoulée en ms: ", int(duration))


if __name__ == '__main__':
    main()
