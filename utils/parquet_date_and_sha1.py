import hashlib

import pyarrow.parquet as pq


# Charger le fichier Parquet`
def get_metadata(path):
    parquet_file = pq.ParquetFile(path)

    # Obtenir le schéma du fichier
    schema = parquet_file.schema.to_arrow_schema()

    # Afficher des informations sur chaque colonne
    for field in schema:
        print(f"Nom de la colonne: {field.name}")
        print(f"Type de la colonne: {field.type}")
        # S'il y a des métadonnées associées à la colonne, les afficher
        if field.metadata:
            print(f"Métadonnées de la colonne: {field.metadata}")
            # TODO Trouver la date avec la clé creation_date, en attendant on renvoie None
            creation_date = None
        print()  # Ajoute un espace pour la clarté entre les colonnes
    else : creation_date = None

    # Calculate SHA-1 hash of the file
    sha1_hash = hashlib.sha1()
    try:
        with open(path, 'rb') as f:
            while chunk := f.read(4096):
                sha1_hash.update(chunk)
        sha1_hexdigest: str = sha1_hash.hexdigest()
    except Exception as e:
        return creation_date, f"Error calculating SHA1: {str(e)}"

    return creation_date, sha1_hash


if __name__ == "__main__":
    get_metadata('../data-parquet/movies.parquet')
