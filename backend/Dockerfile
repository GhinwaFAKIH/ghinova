# Optional alternative to the native Render Python service.
FROM python:3.14-slim
WORKDIR /app
COPY backend/requirements.txt backend/requirements-lock.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY backend/ ./backend/
RUN mkdir -p /var/data && chown 65534:65534 /var/data
USER 65534:65534
ENV PORT=8787 PYTHONDONTWRITEBYTECODE=1 BUDGET_DB=/var/data/usage.sqlite3
EXPOSE 8787
CMD ["sh", "-c", "exec uvicorn backend.app:app --host 0.0.0.0 --port $PORT --workers 1 --no-proxy-headers --no-access-log --limit-concurrency 32"]
