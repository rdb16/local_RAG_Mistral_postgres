import os
import psycopg as pg

from utils import load_env


def get_file_list_from_db(conf: dict, db: str) -> list:
    connection_string = conf.get('CONNECTION_STRING') + db
    conn = pg.connect(connection_string)
    cur = conn.cursor()
    pdf_list = []
    try:
        cur.execute("SELECT file_name FROM inserted_file WHERE file_name IS NOT NULL")
        _list = cur.fetchall()
        for item in _list:
            pdf_list.append(item[0])
    except pg.Error as e:
        print("ERROR : ", e)
    finally:
        cur.close()
        conn.close()
    return pdf_list


def get_files_from_data(data_dir, ext) -> list:
    file_data_list = []
    try:
        for filename in os.listdir(data_dir):
            if filename.endswith(ext):
                file_data_list.append(filename)
    except OSError as e:
        print("ERROR : ", e)
    return file_data_list


def get_filtered_list(pg_list: list, data_list: list) -> list:
    filtered_list = [file for file in data_list if file not in pg_list]
    return filtered_list


def main():
    conf = load_env.load('../config/config.json')
    pdf_pg_list = get_pdf_list_from_db(conf, 'pg_monopoly2')
    print("nb de pdf trouvés dans pg : ", len(pdf_pg_list))
    print(pdf_pg_list)
    for pdf in pdf_pg_list:
        print(pdf)
    print("-------------")
    pdf_data_list = get_files_from_data('../data-player')
    print("nb de pdf trouvés dans data ", len(pdf_data_list))
    for pdf in pdf_data_list:
        print(pdf)

    print("-------------")
    pdf_to_import = get_filtered_list(pdf_pg_list, pdf_data_list)
    print("nb de pdf à importer après tri", len(pdf_to_import))
    for pdf in pdf_to_import:
        print(pdf)

    #


if __name__ == "__main__":
    main()
