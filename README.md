### python 3.12

### configurer un virtual env dans le dossier du projet avec cette version de python
    ## et lancer pip install -r requirements.txt pour les dépendances

### installer sur votre ordinateur le serveur Ollama
    ## télécharger le LLM de mistral et llama3, de manière à ce que les traitements restent en interne

### Pour l'embedding le choix se fait avec le fichier get_embedding_function.py
    ## soit utiliser le modèle d'embeddings d"AWS titan ou autre moteur d'embedding,
    ## tel cohere-multilingual en eu-west-3
    ## soit un modèle local

### à la racine du projet créer un dossier config et un fichier config.json
    ## contenant les credentials de la base PG >= 14
    ## le chemin du dossier des pdfs à traiter
    ## le choix du moteur d'embedding
    ##  exemple
    {
      "IMAC_CONNECTION_STRING": "",
      "DATA_PATH": "./data-xxx",
      "DB_HOST": "",
      "DB_PORT": 5432,
      "DB_USER": "",
      "DB_PASS": "",
      "DB_NAME": "postgres",
      "EMBEDDINGS_ENGINE": "local"  # sur le serveur interne Ollama ou "us-east-1" pour Titan1
                                    # ou cohere-multilingual-v3 sur "eu-west-3"
      ......
    }

### la base vectorielle sera crée sur un serveur Postgresql version >= 14, ici 16
    ## le programme se charge de créer la base si elle n'existe pas
    ## et de rajouter l'extension vector
    ## enfin de générer une table embeddings, si elle n'existe pas, avec les champs définis ci-après
    ## est générée aussi un table pdf_file, si elle n'existe pas, dont la fk est reprise dans la table embeddings,
        ## avec une colonne sha1 et la date de création extraite du pdf
        TODO on vérifiera que pour un pdf donné la date de création est supérieure
         et que le sha1 est différent pour remplacer les chunks dans la base

### populate.py:
 ## liste les fichiers trouvés dans le dossier data spécifié dans le fichier de conf
 ## liste les pdf déjà importés dans la table inserted_file de la base correspondante 
 ## calcule la liste restreinte des nouveaux pdf à importer
 ## calcul l'embedding de ces fichiers et calcule l'index et génère les champs pour l'import
    # le nom du pdf
    # extrait des metadata la date de création du pdf, et la convertit en iso
    # le type de document :  compte-rendu, notice, ordonnances, ...( liste à fournir)
    # l'index ids = "numéro de page du pdf"."numéro du chunk de cette page" ( utile pour citer les sources dans le résultat)
    # le texte du chunk
    # le nb de tokens du chunk
    # enfin le vecteur ( la vectorisation est faite avec un titan embed Titan,
                        ou par llama3 en local, et  retourne un vecteur de dim 1536 ou 4096
                        selon le moteur d'embedding choisi)
 ## Importe les champs de chaque chunk dans la base

 Notons que pour une meilleure qualité de la recherche vectorielle,
 le moteur d'embeddings fournit par AWS est meilleur et qu'il est payant.
 Il faut donc avoir à la racine de son /home le dossier .aws avec profil et credentials.
 Ne pas oublier de demander l'accès dans bedrock à ce modèle de fondation dans la zone concernée.

 Pour la recherche vectorielle, il est nécessaire de générer le vecteur de la question avec le même moteur
 d'embeddings que celui qui a utilisé pour nourrir la base.

 Le modèle de fondation d'embeddings utilisé par défaut par langchain_community.embeddings.bedrock
 dans la région us-east-1 est le modèle "Amazon Titan Embeddings G1 - Text", dont l'identifiant de base
            est amazon.titan-embed-text-v1.
 Ce modèle est conçu pour des tâches telles que la récupération de texte, la similarité sémantique
 et le clustering, avec une longueur maximale de texte d'entrée de 8 000 tokens
 et une longueur maximale de vecteur de sortie de 1 536 dimensions.
Dans la région eu-west-3 c'est cohere, qui fonctionne bien.


 ### query_rag_using_pg
    ## lance en console python query_rag_using_pg.py avec la question comme argument
    ## bien vérifier le dossier de data choisi dan sle fichier de configuration
    TODO suite à des pdf mal formés certains chunks sont absents
     voir l'utilisation de PyMuPDF (également connu sous le nom de fitz).



