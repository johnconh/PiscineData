FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    libpq-dev \
    build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY  requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5432

#CMD ["tail", "-f", "/dev/null"]