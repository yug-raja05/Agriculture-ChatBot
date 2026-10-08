<<<<<<< HEAD
# NLP_Project
=======
# AgriGenius AI - Enterprise AI Agriculture SaaS Platform

AgriGenius AI is a modern, production-grade conversational artificial intelligence application designed to empower farmers with real-time crop recommendations, disease diagnostics, weather advisories, mandi market price predictions, and government schemes matching guides.

---

## 1. Technical Architecture Overview

AgriGenius AI is designed with a decoupled, modular microservices architecture:

```
  Farmer / Admin UI (React & Tailwind CSS)
                   │
                   ▼
  FastAPI REST API Gateway & Controllers Router
   ├── [NLP Ingestion Engine] (Unicode clean, spaCy multilingual tokens, HF Zero-Shot Classifier)
   ├── [AI Agent Orchestrator] (LangChain agent-loops with dynamic tools)
   ├── [RAG Retrieval Chain] (E5 Multilingual Embeddings & Chroma DB CloudClient)
   ├── [ML Model Registry] (Lazy loader, performance metrics comparisons, CUDA GPU configs)
   ├── [Plant Health Platform] (EfficientNet disease detection, OCR bill parsing, Whisper STT, Coqui TTS)
   └── [Agri Services Platform] (Weather forecast analyzers, mandi price trends, notifications queue)
```

---

## 2. Directory Layout Structure

The workspace follows this directory hierarchy:
```
agrigenius/
├── docker-compose.yml              # Production composition file
├── .github/workflows/ci-cd.yml      # CI/CD GitHub Actions pipelines
├── backend/
│   ├── Dockerfile                  # Backend build recipe
│   ├── requirements.txt            # Python dependencies libraries
│   ├── verify_rag.py               # RAG verification test
│   ├── verify_nlp.py               # NLP pipeline verification test
│   ├── verify_ml.py                # Model registry verification test
│   ├── verify_plant_health.py      # Plant health diagnostics verification test
│   ├── verify_agri_services.py     # Weather and Mandi verification test
│   ├── verify_enterprise.py        # Monitoring and backup verification test
│   ├── app/
│   │   ├── main.py                 # FastAPI application main entry
│   │   ├── core/
│   │   │   ├── database.py         # Mongo connections
│   │   │   ├── security.py         # JWT and password hashes
│   │   │   └── backup.py           # Disaster recovery dumps
│   │   ├── api/v1/
│   │   │   ├── router.py           # Global routing mounts
│   │   │   └── endpoints/
│   │   │       ├── nlp.py          # REST endpoints for text analyses
│   │   │       ├── models.py       # REST endpoints for model benchmarking
│   │   │       ├── plant_health.py # REST endpoints for images, OCR, audio
│   │   │       ├── agri_services.py# REST endpoints for weather/mandi prices
│   │   │       └── enterprise.py   # REST endpoints for analytics dashboards
│   │   └── ai/
│   │       ├── agent.py            # Main Agent coordinator
│   │       ├── nlp/                # NLP engine cleaners and tokenizers
│   │       ├── rag/                # E5 embeddings and RAG vector searchers
│   │       ├── ml_framework/       # ML models registry loaders
│   │       ├── plant_health/       # CV classifiers and document parsers
│   │       ├── agri_services/      # Weather/Mandi prices recommendation engines
│   │       └── tools/              # registered LLM tools wrappers
```

---

## 3. Core Platforms & Platform Engines

1. **Enterprise NLP Ingestion Engine**:
   - Unicode cleans, removes emojis, and normalizes whitespaces. Preserves Hindi/Gujarati scripts.
   - Tokenizes prompts using spaCy.
   - Classifies 20+ specialized farming intents using zero-shot classification.
   - Extracts crop, fertilizer, chemical, size, and location entities.

2. **Semantic RAG Knowledge Base**:
   - Leverages `intfloat/multilingual-e5-base` query embeddings model.
   - Segregates overlapping text chunks across PDF, DOCX, TXT, CSV, JSON document uploads.
   - Performs vector searches in Chroma DB returning High/Medium/Low confidence citations card metrics.

3. **AI Model Management Registry**:
   - Dynamic activation controls switching active crop, fertilizer, yield, or soil models via `.env` keys.
   - Validates baseline criteria (>75% accuracy) and benchmarks inference latencies (50 simulated cycles).
   - Generates accuracy and memory metrics comparison maps.

4. **Intelligent Plant Health Platform**:
   - Classifies plant leaves and fruit disease severity (EfficientNet-B0/ResNet50).
   - Extracts dosage schedules from labels and soil reports using modular OCR parsing.
   - Implements speech-to-text transcribers (Whisper) and text-to-speech voice responses (Coqui TTS).
   - Writes treatment advisories to downloadable PDF reports.

5. **Smart Agriculture Services Platform**:
   - Computes farming advisories (irrigation, sowing, pesticide spraying) based on forecast wind speeds and humidity.
   - Decouples Agmarknet mandi price comparisons.
   - Runs in-app notifications and recurring reminders asynchronously using FastAPI BackgroundTasks.

---

## 4. Execution & Setup Instructions

### Python Pip Manual Setup
1. Change directory to backend:
   ```bash
   cd backend
   ```
2. Install python packages:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the application locally:
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```

### Docker Compose Containerization
To launch the complete MongoDB, ChromaDB, FastAPI Backend, and React Frontend stack:
```bash
docker-compose up --build -d
```

---

## 5. Verification Commands
To test the individual components of the system:
- **RAG System**: `python backend/verify_rag.py`
- **NLP Engine**: `python backend/verify_nlp.py`
- **Model Registry**: `python backend/verify_ml.py`
- **Plant Health**: `python backend/verify_plant_health.py`
- **Agri Services**: `python backend/verify_agri_services.py`
- **DevOps & Backups**: `python backend/verify_enterprise.py`
- **Global App Load**: `python backend/verify_app.py`

>>>>>>> f4e5c46 (Initial commit without secrets)
