FROM python:3.12-slim
WORKDIR /app
ENV PYTHONPATH=/app/backend
RUN useradd --create-home appuser
COPY pyproject.toml .
RUN pip install --no-cache-dir .
COPY backend ./backend
COPY migrations ./migrations
COPY alembic.ini .
USER appuser
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
