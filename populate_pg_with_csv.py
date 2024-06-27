import time

from utils import load_env, db_name


def main():
    start_time = time.time()
    ###############################################################################
    # Setup your database to insert embeddings
    ###############################################################################

    # Get openAI api key by reading local .env file
    conf = load_env.load('config/config.json')
    data_path = conf['DATA_PATH']

    # check db
    # la base pg sera nommée comme le data_path en remplaçant data par base
    dbname = db_name.get_name(conf)
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

