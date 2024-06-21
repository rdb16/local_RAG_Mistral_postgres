from langchain_community.embeddings.ollama import OllamaEmbeddings
from langchain_community.embeddings.bedrock import BedrockEmbeddings
from sklearn.metrics.pairwise import cosine_similarity


def get_embedding_function(region):
    if region == "us-east-1":
        embeddings = BedrockEmbeddings(
            credentials_profile_name="bedrock_user",
            region_name="us-east-1",
            model_id="amazon.titan-embed-text-v1"  # vecteur 1536
        )
    elif region == "eu-west-2":
        embeddings = BedrockEmbeddings(
            credentials_profile_name="bedrock_user",
            region_name="eu-west-2",
            model_id="amazon.titan-embed-text-v2:0")  # vecteur 1024

    # elif region == "eu-west-3":
    #     embeddings = BedrockEmbeddings(
    #         credentials_profile_name="bedrock_user",
    #         region_name="eu-west-2",
    #         model="amazon.titan-embed-text-v2:0"
    # )

    else:
        embeddings = OllamaEmbeddings(
            model="llama3",
            base_url="http://localhost:11434"
        )

    return embeddings


def test_embedding_function(region):
    embedding = get_embedding_function(region)
    # renvoie le vecteur du document
    base_texts = [
            "Alpha est la première lettre de l'alphabet grec",
            "Beta est la seconde lettre de l'alphabet grec",
            "Gamma est la troisième lettre de l'alphabet grec",
            "La pie voleuse est un oiseau noir et blanc",
            "Le minium est une couleur proche du rouge"
    ]
    base_embeddings = {txt: embedding.embed_query(txt) for txt in base_texts}
    # renvoie le vecteur de la question
    question = "Quelle est la couleur du plumage de la pie?"
    question_embedded = embedding.embed_query(question)
    print("longueur du vecteur: ",len(question_embedded), "Type du vecteur: ", type(question_embedded))
    # Test de la fonction de recherche
    retrieved_text = find_closest_text(question_embedded, base_embeddings)
    print("Rappel de la question: ", question)
    print(f"Réponse correspondante: {retrieved_text}")


# Trouver le texte correspondant à un embedding donné
def find_closest_text(target_embedding, text_embeddings):
    best_match = None
    highest_similarity = -1

    for text, emb in text_embeddings.items():
        similarity = cosine_similarity([target_embedding], [emb])[0][0]
        print("similarity: ", similarity, "text: ", text)
        if similarity > highest_similarity:
            highest_similarity = similarity
            best_match = text

    return best_match


if __name__ == "__main__":
    test_embedding_function("local")
