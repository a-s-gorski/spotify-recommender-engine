FROM python:3.12-slim

WORKDIR /app

RUN pip install uv

COPY uv.lock pyproject.toml ./

RUN uv venv && \
    uv pip install --system -r pyproject.toml

COPY src/ ./src
COPY main.py .
COPY artifacts/ ./artifacts

ENV PYTHONUNBUFFERED=1

EXPOSE 8000

CMD ["python", "main.py"]