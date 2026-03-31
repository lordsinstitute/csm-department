# MindCanvas — AI Knowledge Graph

> Transform your browsing history into an intelligent, visual knowledge network powered by semantic AI clustering and a RAG-based conversational assistant.

[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker&logoColor=white)](https://www.docker.com/)
[![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![React](https://img.shields.io/badge/React-18-61DAFB?logo=react&logoColor=black)](https://react.dev/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-pgvector-4169E1?logo=postgresql&logoColor=white)](https://github.com/pgvector/pgvector)
[![License](https://img.shields.io/badge/License-MIT-F59E0B)](LICENSE)

---

**Lords Institute of Engineering and Technology**
Department of Computer Science and Engineering (AI & ML)

| #   | Name                     | Roll No.     | Role             |
| --- | ------------------------ | ------------ | ---------------- |
| 1   | Mohammed Huzaifah        | 160922748020 | Full Stack & AI  |
| 2   | Syed Abdul Muqeet Mujeeb | 160922748006 | Backend & RAG    |
| 3   | Niyazuddin Mohammed      | 160922748039 | Frontend & Graph |
| 4   | Mir Danish Ali           | 160922748023 | ML & Embeddings  |

**Project Guide:** Mr. Shaik Khaja Pasha _(Assistant Professor, Dept. of CSE — AI & ML)_

---

## Table of Contents

1. [About](#about)
2. [Screenshots](#screenshots)
3. [Features](#features)
4. [Tech Stack](#tech-stack)
5. [Architecture](#architecture)
6. [Quick Start](#quick-start-docker)
7. [Environment Variables](#environment-variables)
8. [API Reference](#api-reference)
9. [Manual Installation](#manual-installation)
10. [Troubleshooting](#troubleshooting)

---

## About

We consume vast amounts of content daily — articles, tutorials, research papers, documentation — but this knowledge remains scattered and disconnected. **MindCanvas** solves this by transforming browsing data into a visual, searchable knowledge graph with AI-powered semantic clustering and a context-aware conversational assistant.

**Core capabilities:**

- Automatically groups related content into meaningful clusters using GPT-4.1-mini
- Visualises relationships between topics as an interactive neural-style graph
- Lets you query your own knowledge base in natural language via RAG

---

## Screenshots

![Knowledge Graph](docs/images/image.png)
_Interactive knowledge graph with AI semantic clustering_

![AI Chat Interface](docs/images/image-4.png)
_RAG-powered chatbot with source citations and confidence scores_

![Graph Clusters](docs/images/image-5.png)
_Semantic cluster view with neural-style node layout_

---

## Features

### AI-Powered Semantic Clustering

- **GPT-4.1-mini JSON Mode** — structured LLM output assigns nodes to semantic clusters (Python pages group with Python, finance with finance, etc.)
- **Smart Fallback** — topic-specificity algorithm activates when the API is unavailable, ensuring clustering always works

### Interactive Knowledge Graph

- **Neural Layout** — phyllotaxis golden-angle cluster placement with polygon/neuron/spiral node shapes per cluster size
- **Cytoscape.js** — hardware-accelerated graph rendering with glow nodes, shadow-blur effects, and cluster coloring
- **Interactive** — hover to highlight connections, click any node to inspect details and related content

### RAG Chatbot

- **Knowledge-Aware** — answers questions grounded in your actual browsing history and saved content
- **Source Citations** — every response references the content it draws from with similarity scores
- **Keyword Fallback** — gracefully handles queries even when vector search returns no results

### Chrome Extension

- **One-Click Export** — sends browsing history directly to MindCanvas
- **Privacy First** — all data stays on your machine; nothing is sent to third-party servers

---

## Tech Stack

### Backend

| Technology                                 | Purpose                                    |
| ------------------------------------------ | ------------------------------------------ |
| **FastAPI**                                | Async Python web framework                 |
| **SentenceTransformer** `all-MiniLM-L6-v2` | 384-dim local embeddings                   |
| **OpenAI GPT-4.1-mini**                    | Semantic clustering & content analysis     |
| **asyncpg** + **pgvector**                 | High-performance PostgreSQL vector queries |
| **scikit-learn** (DBSCAN)                  | Embedding-based clustering fallback        |
| **BeautifulSoup**                          | Web content extraction                     |

### Frontend

| Technology                   | Purpose                               |
| ---------------------------- | ------------------------------------- |
| **React 18** + **Vite**      | UI framework & fast dev/build tooling |
| **Cytoscape.js** + **fcose** | Graph layout and visualisation        |
| **Styled Components**        | Dark indigo theme with CSS-in-JS      |
| **Zustand**                  | Lightweight global state management   |
| **Framer Motion**            | Animations and transitions            |

### Infrastructure

| Technology                       | Purpose                                    |
| -------------------------------- | ------------------------------------------ |
| **Docker** + **Docker Compose**  | Container orchestration                    |
| **PostgreSQL 16** + **pgvector** | Vector similarity search & content storage |

---

## Architecture

```
┌─────────────────────┐
│   Chrome Extension  │  Exports browsing history via one-click
└────────┬────────────┘
         │ POST /api/ingest
         ▼
┌─────────────────────────────────────────┐
│         FastAPI Backend  :8090          │
│                                         │
│  • BeautifulSoup  — content extraction  │
│  • SentenceTransformer — embeddings     │
│  • GPT-4.1-mini   — AI clustering       │
│  • RAG pipeline   — chatbot context     │
└────────┬────────────────────────────────┘
         │ asyncpg + pgvector
         ▼
┌─────────────────────────────────────────┐
│     PostgreSQL 16 + pgvector  :5432     │
│                                         │
│  • vector(384) similarity search        │
│  • JSONB content & topic storage        │
└────────┬────────────────────────────────┘
         │ REST API
         ▼
┌─────────────────────────────────────────┐
│       React Frontend  :3030             │
│                                         │
│  • Cytoscape.js  — graph visualisation  │
│  • Zustand       — state management     │
│  • RAG chatbot   — knowledge queries    │
└─────────────────────────────────────────┘
```

---

## Quick Start (Docker)

### Prerequisites

- Docker 20.10+ and Docker Compose 2.0+
- OpenAI API Key

### 1. Clone

```bash
git clone https://github.com/Sa1f27/MindCanvas.git
cd MindCanvas
```

### 2. Configure Environment

```bash
cp backend/.env.example backend/.env
```

Edit `backend/.env` with your OpenAI key (see [Environment Variables](#environment-variables)).

### 3. Start

```bash
docker compose up -d --build
```

This starts three containers: `postgres` (pgvector), `backend` (FastAPI), and `frontend` (React/Vite). The backend waits for the database health check before starting.

### 4. Access

| Service              | URL                        |
| -------------------- | -------------------------- |
| Frontend             | http://localhost:3030      |
| Backend API          | http://localhost:8090      |
| Interactive API Docs | http://localhost:8090/docs |

### 5. Load Sample Data (Optional)

Ingest 72 curated URLs across 18 topics for a quick demo:

```bash
# Linux / macOS
curl -X POST http://localhost:8090/api/ingest \
  -H "Content-Type: application/json" \
  -d @sample/sample_data.json

# Windows PowerShell
.\sample\load_sample_data.ps1
```

---

## Environment Variables

| Variable         | Required | Description                                                    |
| ---------------- | -------- | -------------------------------------------------------------- |
| `OPENAI_API_KEY` | **Yes**  | OpenAI API key for clustering and chat                         |
| `DATABASE_URL`   | No       | PostgreSQL connection string (default: local Docker container) |
| `OPENAI_MODEL`   | No       | Override default model (default: `gpt-4o-mini`)                |

Default `backend/.env`:

```env
OPENAI_API_KEY=sk-your-key-here
DATABASE_URL=postgresql://postgres:postgres@postgres:5432/mindcanvas
```

> **Note:** The PostgreSQL database runs locally in Docker — no external database account is required.

---

## API Reference

| Method | Endpoint                      | Description                                  |
| ------ | ----------------------------- | -------------------------------------------- |
| `POST` | `/api/ingest`                 | Import browsing history (batch URL list)     |
| `POST` | `/api/chat`                   | Chat with the RAG knowledge assistant        |
| `POST` | `/api/search/semantic`        | Vector similarity search                     |
| `GET`  | `/api/knowledge-graph/export` | Full graph export (nodes + edges + clusters) |
| `GET`  | `/api/cluster`                | Cluster metadata                             |
| `GET`  | `/api/content`                | List all stored content                      |
| `GET`  | `/api/trending`               | Trending topics by frequency                 |
| `GET`  | `/api/recommendations`        | Personalised content recommendations         |
| `GET`  | `/api/health`                 | System health check                          |

Full interactive documentation: http://localhost:8090/docs

---

## Manual Installation

<details>
<summary>Expand for local development setup</summary>

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8090 --reload
```

Requires a running PostgreSQL instance with the `vector` extension. Run `backend/init.sql` against your database to initialise the schema.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Chrome Extension

1. Open `chrome://extensions/`
2. Enable **Developer mode**
3. Click **Load unpacked**
4. Select the `extension/` folder

</details>

---

## Troubleshooting

| Symptom                         | Likely Cause                       | Fix                                                                   |
| ------------------------------- | ---------------------------------- | --------------------------------------------------------------------- |
| Backend exits immediately       | Missing `OPENAI_API_KEY` in `.env` | Add a valid key to `backend/.env`                                     |
| Graph shows no nodes            | No data ingested yet               | Load sample data or use the Chrome extension                          |
| Clustering falls back to topics | Invalid or missing OpenAI key      | AI clustering requires a working API key                              |
| Port already in use             | Another process on 8090/3030       | Change ports in `docker-compose.yml`                                  |
| `docker compose` not found      | Old Docker version                 | Upgrade to Docker Compose v2 (`docker compose`, not `docker-compose`) |

---

## License

MIT License — see [LICENSE](LICENSE) for details.

---

<p align="center">Built for the AI age &nbsp;|&nbsp; <a href="https://github.com/Sa1f27/MindCanvas">GitHub</a></p>
