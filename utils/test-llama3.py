from langchain_community.embeddings import OllamaEmbeddings
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

# Initialisation du modèle Ollama
ollama_emb = OllamaEmbeddings(
    model="llama3",
    base_url="http://localhost:11434"
)

# Texte pour lequel nous voulons obtenir des embeddings
text = "2"
embedding = ollama_emb.embed_query(text)

# Simuler un stockage de textes et leurs embeddings
known_texts = [
    "Texte exemple 1",
    "Texte exemple 2",
    "Votre texte ici"
]
text_embeddings = {txt: ollama_emb.embed_query(txt) for txt in known_texts}


# Trouver le texte correspondant à un embedding donné
def find_closest_text(target_embedding, text_embeddings):
    best_match = None
    highest_similarity = -1

    for text, emb in text_embeddings.items():
        similarity = cosine_similarity([target_embedding], [emb])[0][0]
        if similarity > highest_similarity:
            highest_similarity = similarity
            best_match = text

    return best_match


# Test de la fonction de recherche
retrieved_text = find_closest_text(embedding, text_embeddings)
print(f"Texte correspondant: {retrieved_text}")
