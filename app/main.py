import os
import sys

from openai import OpenAI

from parser import parse_chat_file
from database import connect_to_db, populate_db
from ai import ask_chat


def create_client() -> OpenAI:
    """Create the OpenAI-compatible client from environment variables."""
    return OpenAI(
        base_url=os.environ.get("LLAMA_SERVER_URL"),
        api_key="sk-no-key-required",
    )


def run_ingestion(client: OpenAI, path: str) -> None:
    """Parse a chat file and ingest chunks into the database."""
    chunks = parse_chat_file(path)
    print(f"Parsing completed, created {len(chunks)} chunks")

    conn = connect_to_db()
    try:
        populate_db(conn, chunks, client)
    finally:
        conn.close()


def run_repl(client: OpenAI) -> None:
    """Interactive query loop."""
    conn = connect_to_db()
    model_name = os.environ.get("CHAT_MODEL_NAME", "gemma-4-26B-A4B-it-mtp")

    print("--- RAG TEST ---")
    print("Ask me anything about the chat (type 'quit' to exit)\n")

    try:
        while True:
            question = input("TU: ").strip()
            if question == "quit":
                break
            if not question:
                continue

            try:
                answer, _ = ask_chat(conn, client, question)
                print(f"\n{model_name.upper()}: {answer}\n")
            except Exception as e:
                print(f"Error during research: {e}")
    finally:
        conn.close()
        print("Chat closed")


def main():
    client = create_client()

    if len(sys.argv) >= 3 and sys.argv[1] == "--ingest":
        run_ingestion(client, sys.argv[2])
    else:
        run_repl(client)


if __name__ == "__main__":
    main()
