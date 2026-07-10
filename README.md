# Flyrank Tiny Backend

A minimal FastAPI backend with two JSON endpoints.

## Endpoints

- `GET /` returns a welcome message.
- `GET /health` returns the server health status.

## Run locally

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate

```
## Install dependencies 
``` bash 
pip install -r requirements.txt
```
## Start the server 
``` bash
uvicorn main:app --reload --port 8000 
```
## Test with curl
``` bash
curl http://127.0.0.1:8000/
curl http://127.0.0.1:8000/health
```