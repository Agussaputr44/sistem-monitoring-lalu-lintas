FROM python:3.11-slim

WORKDIR /app

# system dependencies untuk OpenCV
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    && rm -rf /var/lib/apt/lists/*

# install python deps
COPY requirements.txt .
RUN pip install --default-timeout=300 --no-cache-dir -r requirements.txt

# copy source
COPY . .

EXPOSE 8000

CMD ["uvicorn", "app_optimation.main:app", "--host", "0.0.0.0", "--port", "8000"]
