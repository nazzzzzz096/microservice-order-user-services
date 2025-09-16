FROM python:3.12-slim

WORKDIR /app

# Install system dependencies and ensure network tools
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# Debug: Check internet connectivity
RUN curl -I https://pypi.org

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt --index-url https://pypi.org/simple/

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]