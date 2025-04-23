FROM python:3.12-slim-bookworm
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
WORKDIR /code
COPY . /code
RUN uv sync --frozen
ENTRYPOINT ["uv",  "run", "harvest-mcp-server.py"]
