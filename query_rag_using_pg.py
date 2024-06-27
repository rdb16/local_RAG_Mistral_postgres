import argparse
import time
import psycopg
from langchain_core.prompts import PromptTemplate
from langchain_community.llms.ollama import Ollama
from embedding_function import get_embedding_function
from utils import load_env, db_name

PROMPT_TEMPLATE = """
    Répond à la question en n'utilisant que les données du contexte  à l'exclusion de toutes autres:
    
    {context}
    
    ---
    
    Répond à la question en français, en te basant sur le contexte ci-dessus: {question}
    """


def query_rag(query_txt: str, conf: dict) -> tuple:
    conn_string = conf["IMAC_CONNECTION_STRING"]
    dbname = db_name.get_name(conf)
    conn_string = conn_string + dbname
    print("conn_string", conn_string)
    print("engine", conf["EMBEDDINGS_ENGINE"])

    embedding_fn = get_embedding_function(conf["EMBEDDINGS_ENGINE"])

    query_embedding = embedding_fn.embed_query(query_txt)
    # print("query_embedding", query_embedding)
    end_vecto = time.time()

    with psycopg.connect(conn_string) as conn:
        # on lance une requête par similarité sur la table
        with conn.cursor() as cursor:
            cursor.execute("""
                            SELECT ids, content, embedding FROM embeddings
                            ORDER BY embedding <=> %s::vector
                            LIMIT 5;
                        """, (query_embedding,))

            results = cursor.fetchall()

            context_text = "\n\n---\n\n".join([doc[1] for doc in results])
            prompt_template = PromptTemplate(innput_variables=["context", "question"], template=PROMPT_TEMPLATE)
            prompt = prompt_template.format(context=context_text, question=query_txt)
            # print("prompt", prompt)

            model = Ollama(model="mistral")
            response_text = model.invoke(prompt)

            sources = [doc[0] for doc in results]
            format_response = f"Réponse: {response_text}\nSources: {sources}"

        return format_response, end_vecto


def main():
    start_time = time.time()
    conf = load_env.load('config/config.json')
    # create CLi
    parser = argparse.ArgumentParser()
    parser.add_argument('query_text', type=str, help="Entrer votre question.")
    args = parser.parse_args()
    query_text = args.query_text
    response, vecto = query_rag(query_text, conf)
    print(response)
    vecto_duration = (vecto - start_time) * 1000
    print("durée de la vectorisation de la question: ",int(vecto_duration))
    end_time = time.time()
    duration = (end_time - start_time) * 1000
    print("durée totale en ms: ", int(duration))


if __name__ == "__main__":
    main()
