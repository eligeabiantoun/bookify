FROM python:3.12-slim

WORKDIR /app

# System deps (optional but fine)
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
 && rm -rf /var/lib/apt/lists/*

# Copy root requirements and install
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copy the WHOLE project (including manage.py, apps, etc.)
COPY search_service/ .


EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]