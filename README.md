# RAG TEST

A **Retrieval-Augmented Generation** system that turns text exports into a queryable memory. Import your chat files, then ask questions in natural language and get answers grounded in the imported conversation history.

Built with Python 3.13, PostgreSQL + [pgvector](https://github.com/pgvector/pgvector), and any OpenAI-compatible local LLM server (e.g. [llama.cpp](https://github.com/ggml-org/llama.cpp)).

## Features

- **Chat ingestion** — parse chat text exports into semantic chunks
- **Vector embeddings** — store embeddings in PostgreSQL via pgvector
- **Interactive REPL** — ask questions about your chat history in natural language
- **Local-first** — runs entirely on your machine with a local LLM server (no cloud API keys needed)
- **Docker-ready** — spin up the full stack with `docker compose`

## Architecture

```
┌──────────────┐     ┌──────────────┐     ┌──────────────────┐
│ Chat File    │────▶│ Parser       │────▶│ Embedding Model  │
│ (.txt)       │     │ (chunking)   │     │ (bge-m3-GGUF)    │
└──────────────┘     └──────────────┘     └────────┬─────────┘
                                                    │
┌──────────────┐     ┌──────────────┐               ▼
│ User Query   │────▶│ Embedding    │──────▶  ┌──────────────┐
│ (REPL)       │     │ + Vector     │         │ PostgreSQL   │
└──────────────┘     │ Search       │         │ + pgvector   │
                     └──────┬───────┘         └──────────────┘
                            │
                     ┌──────▼───────┐
                     │ Chat Model   │
                     │ (gemma-4-26B)│
                     └──────┬───────┘
                            │
                     ┌──────▼───────┐
                     │   Answer     │
                     └──────────────┘
```

## Prerequisites

- [Docker & Docker Compose](https://docs.docker.com/compose/)
- A local LLM server with OpenAI-compatible API (e.g. [llama.cpp](https://github.com/ggml-org/llama.cpp) served on port 8081)
- [uv](https://github.com/astral-sh/uv) (Python package manager)

## Quick Start

### 1. Clone and configure

```bash
git clone <repo-url>
cd RAG
cp .env.example .env
```

Edit `.env` and set your database credentials and LLM server URL.

### 2. Start the database

```bash
docker compose up -d postgres
```

### 3. Install dependencies

```bash
uv sync
```

### 4. Ingest your chat

Export your chat as text, then run:

```bash
uv run python app/main.py --ingest /path/to/your_chat.txt
```

This parses the file into chunks, generates embeddings, and stores them in PostgreSQL.

### 5. Query your memory

```bash
uv run python app/main.py
```

You'll enter an interactive REPL. Ask anything about the chat in natural language:

```
--- RAG TEST ---
Ask me anything about the chat (type 'quit' to exit)

TU: What did we talk about last week?

MODEL-NAME: [answer based on the retrieved chat context...]
```

## Environment Variables

| Variable | Description | Example |
|---|---|---|
| `POSTGRES_USER` | PostgreSQL username | `admin` |
| `POSTGRES_PASSWORD` | PostgreSQL password | `your-secure-password` |
| `POSTGRES_DB` | Database name | `test_db` |
| `POSTGRES_PORT` | Database port | `5432` |
| `LLAMA_SERVER_URL` | URL of your local LLM server (OpenAI-compatible) | `http://host.docker.internal:8081/v1` |
| `EMBEDDING_MODEL_NAME` | Embedding model name | `embedding-GGUF` |
| `CHAT_MODEL_NAME` | Chat/completion model name | `chat-GGUF` |

## Project Structure

```
RAG/
├── app/
│   ├── main.py        # Entry point (ingestion + REPL)
│   ├── parser.py      # chat parser & chunker
│   ├── ai.py          # Embedding generation & chat query logic
│   └── database.py    # PostgreSQL connection & ingestion
├── docker-compose.yml # Docker services (PostgreSQL + app)
├── Dockerfile         # Python app image (uv + Python 3.13)
├── init.sql           # Database schema (pgvector table)
├── pyproject.toml     # Python dependencies
├── .env.example       # Environment variables template
└── .gitignore
```

## Running with Docker

Build and start the full stack:

```bash
docker compose up --build
```

Then exec into the container to run commands:

```bash
docker compose exec app uv run python app/main.py --ingest /path/to/your_chat.txt
docker compose exec app uv run python app/main.py
```

## Notes

- The LLM server must expose an **OpenAI-compatible API** (llama.cpp, Ollama with `--api`, etc.)
- Embedding truncation is capped at 10,000 characters per chunk to stay within model limits
- The system answers in **Italian** by default — edit the system prompt in `app/ai.py` to change the language

## License

MIT
