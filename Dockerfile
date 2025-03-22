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
apt-get install -qyy --no-install-recommends --no-install-suggests curl ca-certificates
apt-get clean
rm -rf /var/lib/apt/lists/*
curl -sL https://github.com/tailwindlabs/tailwindcss/releases/latest/download/tailwindcss-linux-x64 \
    -o /usr/bin/tailwindcss
chmod +x /usr/bin/tailwindcss
EOT

# Copy Tailwind config and styles
WORKDIR /styles
COPY tailwind.config.js ./
COPY static/css/ static/

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
