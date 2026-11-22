FROM python:3.13-slim

WORKDIR /app

RUN pip install --no-cache-dir uvicorn fastapi sqlalchemy pydantic httpx

COPY backend/voyagesim /app/backend/voyagesim

ENV PYTHONPATH=/app

EXPOSE 8001

CMD ["python", "-m", "uvicorn", "backend.voyagesim.app:app", "--host", "0.0.0.0", "--port", "8001"]
