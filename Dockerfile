FROM python:3.12.4-alpine
WORKDIR /app
COPY requirements.lock ./
RUN PYTHONDONTWRITEBYTECODE=1 pip install --no-cache-dir -r requirements.lock
COPY . .
CMD [ "uvicorn", "src.main:app", "--proxy-headers", \
    "--forwarded-allow-ips", "*", "--host", "0.0.0.0", "--port", "8889" ]
