FROM python:3.12-slim

# Workdir inside container
WORKDIR /app

# Install OS deps
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
 && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt /app/

RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . /app/

# Expose Django port
EXPOSE 8000

# Entrypoint (will run start.sh)
CMD ["sh", "accounts_service/start.sh"]

