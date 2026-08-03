# KaamSetu AI Infrastructure Service

This is the AI service microservice for KaamSetu, built with FastAPI. It handles all AI models, training, dataset loading, and integrations with the main backend.

## Setup

1. Install Python 3.12+
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Copy `.env.example` to `.env` and fill in the values:
   ```bash
   cp .env.example .env
   ```

## Running the Service

Start the development server:

```bash
uvicorn app.main:app --reload
```

## Running Tests

Execute the unit tests using pytest:

```bash
pytest
```
