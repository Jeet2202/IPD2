# Service Marketplace Backend

Production-ready backend for a blue-collar service marketplace.

## Tech Stack

| Technology | Role |
|---|---|
| Python 3.11 | Runtime |
| FastAPI | Async web framework |
| MongoDB Atlas | Cloud database |
| Beanie | Async MongoDB ODM |
| Pydantic v2 | Data validation |
| Uvicorn | ASGI server |

## Project Structure

```
backend/
├── app/
│   ├── __init__.py        # Package marker
│   ├── main.py            # FastAPI app with async lifespan
│   ├── config.py          # Environment settings (pydantic-settings)
│   └── database.py        # MongoDB connection manager
├── requirements.txt       # Pinned dependencies
├── pyproject.toml         # Project metadata + linter config
├── .env.example           # Environment variable template
├── .gitignore             # Git ignore rules
└── README.md              # This file
```

Feature modules will be added as `app/<feature>/` directories (e.g., `app/users/`, `app/services/`).

## Setup

```bash
# 1. Create virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Linux/Mac

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
copy .env.example .env       # Windows
# cp .env.example .env       # Linux/Mac
# Edit .env with your MongoDB Atlas URI

# 4. Run development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## API Documentation

Once running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health
