import time
import psycopg as pg
from langchain_community.llms.ollama import Ollama
from langchain_core.prompts import PromptTemplate
import re

from utils import load_env, init_db, db_name


def print_readable(text, max_chars=90, max_words=25):
    # Diviser le texte en phrases
    sentences = re.split(r'(?<=[.!?]) +(?=[A-Z])', text)

    for sentence in sentences:
        words = sentence.split()
        line = ''
        word_count = 0

        for word in words:
            if len(line + word + ' ') > max_chars or word_count == max_words:
                print(line.strip())
                line = ''
                word_count = 0
            line += word + ' '
            word_count += 1

        # Imprimer la dernière ligne si elle contient des mots
        if line:
            print(line.strip())


def main():
    start_time = time.time()

    # charger la conf
    conf = load_env.load('config/config.json')
    dbname = db_name.get_name(conf)
    # print("dbname: ", dbname)
    connection_string = conf['CONNECTION_STRING'] + dbname
    acteur = input("Veuillez entrer le nom de l'acteur dont vous voulez la carrière ?")
    print("je lance la recherche de l'acteur : ", acteur)
    research = "%" + acteur + "%"

    sql = """
        SELECT string_agg(
        E'title: ' || title || E'\noverview: ' || overview || E'\ngenres: ' || genres,
         E'\n\n'
        ) As aggregated_info
        FROM movies
        WHERE "cast" ILIKE %s
        """
    # print(sql)

    conn = pg.connect(connection_string)
    cur = conn.cursor()
    context = ""
    try:
        cur.execute(sql, (research,))
        results = cur.fetchall()
        if results:
            for row in results:
                if row[0]:
                    context += row[0]
        else:
            print("L'acteur n'est pas été trouvé dans la base")
    except pg.Error as e:
        print("ERROR : ", e)
    finally:
        cur.close()
        conn.close()

    # print(context)

    # maintenant on appelle Mistral sur le serveur local Ollama
    PROMPT_TEMPLATE = """
        Répond à la question en n'utilisant que les données du contexte  à l'exclusion de toutes autres:

        {context}

        ---

        Répond à la question en français, en te basant sur le contexte ci-dessus: {question}
        """
    query_text = f'{acteur} a joué dans les films qui sont listés ci-après. Merci de résumer sa carrière cinématographique en donnant un aperçu, du genre de films dans les quels il a joué.\n'
    # print(query_text)
    print()
    prompt_template = PromptTemplate(innput_variables=["context", "question"], template=PROMPT_TEMPLATE)
    prompt = prompt_template.format(context=context, question=query_text)
    # print("prompt", prompt)
    model = Ollama(model="mistral")
    response_text = model.invoke(prompt)
    print_readable(response_text)

    end_time = time.time()
    print("Temps écoulé en secondes: %.2f" % (end_time - start_time))


if __name__ == '__main__':
    main()
