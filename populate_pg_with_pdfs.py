import os
import shutil
from pathlib import Path
from langchain_community.document_loaders import PyPDFDirectoryLoader
from PyPDF2.errors import PdfReadError
import time
import psycopg
from utils import load_env, chunk_ids, check_pg, init_db
from embedding_function import get_embedding_function
from utils.file_list import get_files_from_data, get_file_list_from_db, get_filtered_list
from utils import spliter, insert_into_db
from utils import pdf_date_and_sha1 as pdf_metadata


def main():
    start_time = time.time()
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
    dbname = init_db.check(conf)

    # on crée la table embeddings si elle n'existe pas
    result = check_pg.create_pdf_chunks_table(conf, dbname)
    if result:
        print(f'la table embeddings est dans la base {dbname}')
    else:
        print(f'impossible de créer la table embeddings, on sort')
        exit(1)

    result = check_pg.create_file_table(conf, dbname)
    if result:
        print(f'la table pdf_file est dans la base {dbname}')
    else:
        print(f'impossible de créer la table pdf_file, on sort')
        exit(1)

    pdf_data_list = get_files_from_data(data_path, ".pdf")
    pdf_pg_list = get_file_list_from_db(conf, dbname)
    file_to_import = get_filtered_list(pdf_pg_list, pdf_data_list)
    print("Nombre de fichiers à importer :", len(file_to_import))

    if len(file_to_import) == 0:
        print("Rien à importer on sort")
        end_time = time.time()
        duration = (end_time - start_time) * 1000
        print("duration en ms: ", int(duration))
        exit(0)

    # import dans la table pdf_file
    import_dico: dict = {}
    for file in file_to_import:
        path_file = os.path.join(data_path, file)
        file_date, sha1 = pdf_metadata.get_pdf_details(path_file)
        if file_date:
            data_dico = {"file_name": file,
                         "file_date": file_date,
                         "document_type": "test",
                         "sha1": sha1
                         }
        else:
            data_dico = {"file_name": file,
                         "document_type": "test",
                         "sha1": sha1
                         }
        # print(data_dico)
        fk_pdf = insert_into_db.insert(conf, dbname, data_dico)
        import_dico[file] = fk_pdf

    print("fk_dico: ", import_dico)

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

    # engine
    embed_engine = get_embedding_function(conf["EMBEDDINGS_ENGINE"])

    chunks = None
    try:
        documents = PyPDFDirectoryLoader(tmp_dir).load()
        chunks = spliter.split_documents(documents)
    except PdfReadError as e:
        print(e)

    # connection
    conn_string = conf['CONNECTION_STRING'] + dbname
    conn = psycopg.connect(conn_string)

    # Calculate Page IDs.
    chunks_with_ids = chunk_ids.calculate(chunks)
    for chunk in chunks_with_ids:
        ids = chunk.metadata["id"]
        content = chunk.page_content
        pdf_name = chunk.metadata["source"].split("/")[-1]
        fk_pdf = import_dico[pdf_name]
        print("file_name", pdf_name, "fk: ", fk_pdf)
        txt = chunk.page_content
        vector = embed_engine.embed_query(txt)
        tokens = len(vector)
        print("tokens", tokens)

        statement = """
            INSERT INTO embeddings (fk_pdf_file, ids, content, tokens, embedding)
            VALUES (%s, %s, %s, %s, %s)    
        """

        values = (fk_pdf, ids, content, tokens, vector)
        print(statement)
        conn.execute(statement, values)
        conn.commit()
    conn.close()

    ###############################################################################
    end_time = time.time()
    duration = (end_time - start_time) * 1000
    print("durée écoulée en ms: ", int(duration))


if __name__ == '__main__':
    main()
