# 💬 RAG Chatbot – FastAPI + Postgres + pgvector + Alembic + Docker

A Retrieval-Augmented Generation (RAG) chatbot built with **FastAPI**, **PostgreSQL**, and **pgvector**.
This project enables efficient document storage, vector embeddings, and semantic search to power an AI chatbot with context-aware responses.

---

## 🚀 Features

* **FastAPI backend** for chat, embeddings, and retrieval
* **PostgreSQL + pgvector** for vector similarity search
* **Dockerized microservices** for easy deployment
* **Alembic migrations** fully configured
* **Chunking + embedding pipeline** for document ingestion
* **LLM provider support** (OpenAI or local models)
* **Clean, modular architecture**

---

## 🧱 Architecture

```
FastAPI (App)
   ├── Ingestion: PDFs / text → chunk → embed → store vectors
   ├── Retrieval: pgvector similarity search
   └── Chat: LLM using retrieved context

PostgreSQL + pgvector
Docker Compose for orchestration
Alembic for DB migrations
```

---

## 🐳 Docker Setup

Start the whole environment:

```bash
docker-compose up --build
```

This will launch:

* FastAPI API on `http://localhost:8000`
* Postgres + pgvector
* Optional admin UI (if included)

---

## 🛠️ Run Locally (Without Docker)

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Make sure your Postgres instance has **pgvector** installed.

---

# ⚙️ Alembic — How to Use It

## 1️⃣ Initialize Alembic (already done)

If needed:

```bash
alembic init app/db/migrations
```

---

## 2️⃣ Create a Migration

Run after editing SQLAlchemy models:

```bash
alembic revision --autogenerate -m "your message"
```

---

## 3️⃣ Apply Migrations

```bash
alembic upgrade head
```

To revert:

```bash
alembic downgrade -1
```
---

## 🔍 Example Vector Search (pgvector)

```python
query = (
    db.query(DocumentEmbedding)
    .order_by(DocumentEmbedding.embedding.cosine_distance(query_vector))
    .limit(5)
)
```

---

# 🚀 API

Start API:

```bash
uvicorn app.main:app --reload
```

Swagger docs:

👉 [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 🌱 Environment Variables

Create `.env`:

```
OPENAI_API_KEY=
DOCS_PATH=./data/docs

PROJECT_NAME=
ENVIRONMENT=development

POSTGRES_USER=
POSTGRES_PASSWORD=
POSTGRES_DB=
POSTGRES_HOST=
POSTGRES_PORT=
```

---

## 🔮 Roadmap

* Hybrid search (text + vector)
* More chunking strategies
* Multi-provider embeddings
* Add authentication
* Add admin dashboard

---

## 📄 License

MIT License.
