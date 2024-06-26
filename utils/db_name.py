from utils import load_env


def get_name(conf: dict) -> str:
    data_path = conf['DATA_PATH']
    dbname = data_path.replace("./data-", "base_")
    if conf['EMBEDDINGS_ENGINE'] == 'us-east-1':
        dbname = dbname + '_titan_v1'
    elif conf['EMBEDDINGS_ENGINE'] == 'eu-west-2':
        dbname = dbname + '_titan_v2'
    elif conf['EMBEDDINGS_ENGINE'] == 'eu-west-3':
        dbname = dbname + '_cohere_mlv3'
    else:
        dbname = dbname + '_llama3'

    return dbname


def main():
    conf = load_env.load('../config/config.json')
    db = get_name(conf)
    print(db)



if __name__ == '__main__':
    main()