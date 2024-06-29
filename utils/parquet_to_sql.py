import sys

import pyarrow as pa
import pyarrow.parquet as pq


def create_sql(parquet_file_path: str) -> str:
    # Lire le fichier Parquet
    table = pq.read_table(parquet_file_path)

    # Obtenir le schéma du fichier Parquet
    schema = table.schema

    # on nomme la table comme le fichier sans l'extension
    table_name = parquet_file_path.split('/')[-1].replace('.parquet', '')

    # Début de la commande SQL
    sql = f"CREATE TABLE IF NOT EXISTS {table_name}(\n"

    # Générer la définition des colonnes pour SQL
    columns_sql = []
    for field in schema:
        field_name = field.name
        field_type = field.type
        if field.name == 'cast':
            field_name = '"' + field_name + '"'

        # Convertir les types de données Parquet en types de données PostgreSQL
        if pa.types.is_int32(field_type):
            sql_type = "INTEGER"
        elif pa.types.is_int64(field_type):
            sql_type = "BIGINT"
        elif pa.types.is_float32(field_type):
            sql_type = "REAL"
        elif pa.types.is_float64(field_type):
            sql_type = "DOUBLE PRECISION"
        elif pa.types.is_boolean(field_type):
            sql_type = "BOOLEAN"
        elif pa.types.is_string(field_type) or pa.types.is_binary(field_type):
            sql_type = "TEXT"
        elif pa.types.is_timestamp(field_type):
            sql_type = "TIMESTAMP"
        else:
            sql_type = "TEXT"  # Par défaut, si non géré

        # Ajouter la définition de colonne à la liste

        columns_sql.append(f"    {field_name} {sql_type}")

    # Joindre toutes les définitions de colonnes
    sql += ",\n".join(columns_sql)

    # Terminer la commande SQL
    sql += "\n);"

    return sql


if __name__ == "__main__":
    file_path = '../data-parquet/movies.parquet'
    sql_command = create_sql(file_path)
    print(sql_command)
