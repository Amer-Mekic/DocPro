# Smart Document Processing System

## Project overview
Build a full-stack document processing application. Users upload business documents (invoices and purchase orders) in PDF, image, CSV, or TXT format. The system extracts structured data using OpenAI-compatible LLM API, validates it with custom rules, and presents it through a review interface where users can correct and confirm documents.

## Tech stack
- **Backend:** Python, FastAPI, SQLAlchemy, Alembic, PostgreSQL
- **AI extraction:** OpenAI-compatible LLM API 
- **Parsing:** pdfplumber (PDF), pytesseract + OpenCV (images), pandas (CSV)
- **Frontend:** React, Vite, Tailwind CSS
- **Deployment:** Docker + docker-compose, Railway

## Project structure
project-root/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── database.py
│   │   ├── models/
│   │   ├── routers/
│   │   ├── services/
│   │   └── schemas/
│   ├── alembic/
│   ├── tests/
│   ├── uploads/
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env
├── frontend/
│   ├── src/
│   │   ├── api/
│   │   ├── pages/
│   │   └── components/
│   ├── package.json
│   └── vite.config.js
└── docker-compose.yaml


## Code style rules
- Use type hints everywhere in Python
- Use Pydantic schemas for all request and response bodies, never return raw SQLAlchemy objects
- Keep routers thin, business logic lives in `services/`
- Never call the LLM API from a router directly, always go through `services/extraction.py`
- Handle exceptions at the service level and surface them as structured error responses
- Use `async def` for all FastAPI route handlers

## Do not
- Do not add authentication or user sessions
- Do not use a third-party task queue. Process synchronously on upload
- Do not use real S3, local file storage only
- Do not use any UI component library other than Tailwind
- Do not hardcode the LLM API key anywhere in source files