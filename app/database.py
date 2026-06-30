import os

import psycopg2

from ai import generate_embedding


def connect_to_db() -> psycopg2.extensions.connection:
    """Create and return a PostgreSQL connection from environment variables."""
    return psycopg2.connect(
        host=os.environ.get("DB_HOST", "localhost"),
        database=os.environ.get("POSTGRES_DB"),
        user=os.environ.get("POSTGRES_USER"),
        password=os.environ.get("POSTGRES_PASSWORD"),
        port=os.environ.get("POSTGRES_PORT"),
    )


def populate_db(conn, chunks: list[str], client) -> None:
    """Insert chunks into the rag_test table, generating embeddings on the fly."""
    print(f"Starting ingestion of {len(chunks)} chunks")

    cursor = conn.cursor()
    query = "INSERT INTO rag_test (message, embedding) VALUES (%s, %s::vector);"
    batch_commit = 200

    for i, chunk in enumerate(chunks):
        vector = generate_embedding(chunk, client)
        cursor.execute(query, (chunk, vector))

        if i % 10 == 0:
            print(f"  Evaluated {i}/{len(chunks)} chunks...")

        if i > 0 and i % batch_commit == 0:
            conn.commit()
            print(f"  Saved {i} chunks")

    conn.commit()
    cursor.close()
    print(f"Finished ingestion of {len(chunks)} chunks")
