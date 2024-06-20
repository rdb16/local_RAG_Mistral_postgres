# from langchain_community.embeddings.ollama import OllamaEmbeddings
from langchain_community.embeddings.bedrock import BedrockEmbeddings


def get_embedding_function():
    embeddings = BedrockEmbeddings(
        credentials_profile_name="bedrock_user",
        region_name="us-east-1"
    )
    # embeddings = OllamaEmbeddings(model="llama:7b", )
    # embeddings = BedrockEmbeddings(
    #     credentials_profile_name="bedrock_user",
    #     region_name="eu-west-2",
    #     model_name="amazon.titan-embed-text-v2:0"
    # )
    return embeddings


def test_embedding_function():
    embedding = get_embedding_function()
    # renvoie le vecteur du document
    r1 = embedding.embed_documents(
        [
            "Alpha est la première lettre de l'alphabet grec",
            "Beta est la seconde lettres de l'alphabet grec"
        ]
    )
    # renvoie le vecteur de la question
    r2 = embedding.embed_query(
        "Quelle est la deuxième lettre de l'alphabet grec?"
    )
    # print("question: ", r2)


if __name__ == "__main__":
    test_embedding_function()
