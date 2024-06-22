import argparse
import os
import shutil
import sys
from pathlib import Path

from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.schema.document import Document

import psycopg
from psycopg import OperationalError
import ast
import pgvector
import math
from pgvector.psycopg import register_vector
from utils import load_env, chunk_ids
from get_embedding_function import get_embedding_function
from langchain_community.vectorstores.chroma import Chroma
from utils import load_env
from utils import check_pg
from utils.pdf_list import get_pdf_from_data, get_pdf_list_from_db, get_filtered_list
from utils import spliter


def main():
    ###############################################################################
    # Setup your database to insert embeddings
    ###############################################################################

    # Get openAI api key by reading local .env file
    conf = load_env.load('config/config.json')
    data_path = conf['DATA_PATH']

    # DEBUG
    # TODO : à terme un dico de la conf donnera le dossier des pdf, les url à taper, et
    #  le dossier des csv pour que que tous ces sources nourrissent les vecteurs datasource

    # check db
    # la base pg sera nommée comme le data_path en remplaçant data par base

    dbname = data_path.replace("./data-", "base_")

    # vérif que la base pg est installée
    result = check_pg.check_pg(conf)
    if result:
        print('Connexion ok')
    else:
        print('Connexion KO!!!')
        exit(1)

    # vérif que la base existe
    result = check_pg.check_db(conf, dbname)
    if result:
        print(f'la base {dbname} existe')
    else:
        print(f'la base {dbname} n\'existe pas')
        print('Nous allons la créer')
        result1 = check_pg.create_db(conf, dbname)
        if result1:
            print(f'la base {dbname} a été crée')
        else:
            print(f'la création de la base {dbname} est en erreur')
            print('On sort')
            exit(1)

    # on vérifie l'extension vector
    result = check_pg.check_db_extension(conf, dbname)
    if result:
        print(f'la base {dbname} a l\'extension vector')
    else:
        print(f'la base {dbname} refuse l\'extension vector')

    # on crée la table embeddings si elle n'existe pas
    result = check_pg.create_chunks_table(conf, dbname)
    if result:
        print(f'la table embeddings a été crée dans la base {dbname}')
    else:
        print(f'impossible de créer la table embeddings, on sort')
        exit(1)

    result = check_pg.create_pdf_table(conf, dbname)
    if result:
        print(f'la table embeddings a été crée dans la base {dbname}')
    else:
        print(f'impossible de créer la table pdf_file, on sort')
        exit(1)

    pdf_data_list = get_pdf_from_data(data_path)
    pdf_pg_list = get_pdf_list_from_db(conf, dbname)
    file_to_import = get_filtered_list(pdf_pg_list, pdf_data_list)

    # on va copier tous les pdf à traiter dans ce répertoire
    tmp_dir = Path("./tmp")

    # Vérifier si le répertoire existe
    if tmp_dir.exists() and tmp_dir.is_dir():
        shutil.rmtree(tmp_dir)
        print("Répertoire existant supprimé.")

    # Créer le répertoire
    tmp_dir.mkdir(parents=True, exist_ok=True)
    print("Répertoire créé.")

    for file in Path(data_path).iterdir():
        if file.name in file_to_import:
            destination = tmp_dir / file.name
            shutil.copy(file, destination)
    print("Les pdfs sont dans tmp, on lance le calcul de leur embedding")

    documents = PyPDFDirectoryLoader(data_path).load()
    chunks = spliter.split_documents(documents)
    print(" chunk0: ", chunks[0])
    print(" chunk type: ", chunks[0].type)
    # Calculate Page IDs.
    chunks_with_ids = chunk_ids.calculate(chunks)
    for chunk in chunks_with_ids:
        print("ids: ", chunk.metadata["id"])

    conn_string = conf['IMAC_CONNECTION_STRING'] + dbname
    conn = psycopg.connect(conn_string)
    # Register the vector type with psycopg2
    register_vector(conn)

    conn.close()

    ###############################################################################


if __name__ == '__main__':
    main()
