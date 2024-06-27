import time


def main():
    start_time = time.time()
    ###############################################################################
    # Setup your database to insert embeddings
    ###############################################################################

    # Get openAI api key by reading local .env file
    conf = load_env.load('config/config.json')
    data_path = conf['DATA_PATH']
