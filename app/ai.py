import os

from openai import OpenAI


def generate_embedding(text: str, client: OpenAI) -> list[float]:
    """Generate an embedding vector for the given text."""
    model = os.environ.get("EMBEDDING_MODEL", "bge-m3-GGUF")
    if len(text) > 10000:
        text = text[:10000]

    response = client.embeddings.create(model=model, input=text)
    return response.data[0].embedding


def ask_chat(conn, client: OpenAI, question: str) -> tuple[str | None, str]:
    """Search the DB for similar messages and answer via the LLM.

    Returns (answer, retrieved_context).
    """
    question_vector = generate_embedding(question, client)

    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT message FROM rag_test
        ORDER BY embedding <=> %s::vector
        LIMIT 4;
        """,
        (question_vector,),
    )
    rows = cursor.fetchall()
    cursor.close()

    context = ""
    for i, row in enumerate(rows):
        context += f"--- EXTRACT {i + 1} ---\n{row[0]}\n\n"

    system_prompt = f"""You are the extension of the user's memory. Answer the question using STRICTLY the chat extracts below.

RULES:
1. Answer in Italian, natural and warm, but using only the facts found in the chats.
2. If you can't find anything useful, say: "Non ho trovato info utili nella tua chat". DO NOT create anything by yourself.

CHAT CONTEXT:
{context}"""

    model = os.environ.get("CHAT_MODEL_NAME", "gemma-4-26B-A4B-it-mtp")
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": question},
        ],
        temperature=0.1,
    )

    return response.choices[0].message.content, context
