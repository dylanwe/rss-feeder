FROM ghcr.io/astral-sh/uv:python3.11-bookworm-slim

RUN apt-get update && apt-get install -y \
	build-essential \
	curl \
	&& apt-get clean \
	&& rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY . .

RUN uv sync --frozen

CMD ["uv", "run", "fastapi", "run", "src/rss-pocket-feeder/main.py"]
