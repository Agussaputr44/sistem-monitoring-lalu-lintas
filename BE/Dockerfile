FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy seluruh proyek
COPY . .

# Expose port
EXPOSE 8000

# Jalankan Uvicorn (FastAPI)
CMD ["uvicorn", "app_optimation.main:app", "--host", "0.0.0.0", "--port", "8000"]
