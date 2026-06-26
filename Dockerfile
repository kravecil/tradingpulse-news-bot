FROM python:3.14-slim

WORKDIR /app

COPY pyproject.toml uv.lock ./

RUN pip install --no-cache-dir --upgrade uv && \
    uv sync --frozen

COPY . .

CMD ["uv", "run", "main.py"]

