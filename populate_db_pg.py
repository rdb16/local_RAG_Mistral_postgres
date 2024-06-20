import argparse
import os
import shutil
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.schema.document import Document

import psycopg
from psycopg import OperationalError
import ast
import pgvector
import math
from pgvector.psycopg import register_vector
from utils import load_env
from get_embedding_function import get_embedding_function
from langchain_community.vectorstores.chroma import Chroma
from utils import load_env
from utils import check_pg


def main():
    ###############################################################################
    # Setup your database to insert embeddings
    ###############################################################################

    # Get openAI api key by reading local .env file
    conf = load_env.load('config/config.json')
    ## DEBUG
    # TODO : à terme un dico de la conf donnera le dossier des pdf, les url à taper, et
    #  le dossier des csv pour que que tous ces sources nourrissent les vecteurs datasource
    data_path = conf['DATA_PATH']

    # check db
    dbname= "pg_monopoly2"
    # vérif que la pg est installé
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
    result = check_pg.check_db_extension(conf,dbname)
    if result:
        print(f'la base {dbname} a l\'extension vector')
    else:
        print(f'la base {dbname}refuse l\'extension vector')

    # on crée la table embeddings si elle n'existe pas
    result = check_pg.create_table(conf, dbname)
    if result:
        print(f'la table embeddings a été crée dans la base {dbname}')
    else:
        print(f'impossible de créer la table embeddings, on sort')
        exit(1)

    conn_string = conf['IMAC_CONNECTION_STRING'] + dbname
    conn = psycopg.connect(conn_string)
    # Register the vector type with psycopg2
    register_vector(conn)


    ###############################################################################


if __name__ == '__main__':
    main()
