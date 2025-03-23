# Install Python dependencies
FROM python:3.12.4-alpine AS build-python
SHELL ["sh", "-exc"]

# Install uv
COPY --from=ghcr.io/astral-sh/uv:0.6.9 /uv /bin/

# Install dependencies
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --locked --no-cache --no-group dev

# Build Tailwind CSS
FROM debian:bookworm-slim AS build-tailwind
SHELL ["sh", "-exc"]

# Install Tailwind CSS CLI
RUN <<EOT
apt-get update -qy
apt-get install -qyy --no-install-recommends curl ca-certificates
apt-get clean
rm -rf /var/lib/apt/lists/*
EOT
RUN <<EOT
curl -sL https://github.com/tailwindlabs/tailwindcss/releases/download/v3.4.13/tailwindcss-linux-x64 \
    -o /bin/tailwindcss
chmod +x /bin/tailwindcss
EOT

# Copy Tailwind config and styles
WORKDIR /styles
COPY tailwind.config.js ./
COPY templates templates
COPY static/css static/css

# Compile styles
RUN tailwindcss -o tailwind.css --minify

# Final image
FROM python:3.12.4-alpine
SHELL ["sh", "-exc"]

# Copy compiled CSS, dependencies and source code
WORKDIR /app
COPY --from=build-python /app/.venv .venv
COPY --from=build-tailwind /styles/tailwind.css static/css/
COPY . .

# Run the application
CMD ["/app/.venv/bin/uvicorn", "src.main:app", "--proxy-headers", \
    "--forwarded-allow-ips", "*", "--host", "0.0.0.0", "--port", "8889" ]
