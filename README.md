# CodeArena

CodeArena is a Django-based LeetCode-style practice platform with:

- Django templates + HTMX frontend
- Supabase-compatible Postgres configuration
- Celery + Redis async submission flow
- A separate FastAPI judge-runner service
- Canonical JSON problem imports for future scraping pipelines

## Local setup

1. Create and activate a virtualenv.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Copy environment defaults:

```bash
cp .env.example .env
```

4. Run migrations and load seed problems:

```bash
python manage.py migrate
python manage.py import_problems docs/sample-data/problems.json
```

5. Start services:

```bash
python manage.py runserver
celery -A config worker -l info -Q submissions,imports,default
uvicorn judge_runner.app:app --reload --port 8001
```

## Docker Compose

Use:

```bash
docker compose up --build
```

Then open `http://localhost:8000`.
