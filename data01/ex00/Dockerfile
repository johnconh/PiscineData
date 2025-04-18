FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    libpq-dev \
    build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY  requirements.txt .
COPY  start.sh /usr/local/bin/start.sh
RUN  chmod +x /usr/local/bin/start.sh

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5432

CMD ["bash", "/usr/local/bin/start.sh"]
#CMD ["tail", "-f", "/dev/null"]