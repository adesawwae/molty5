FROM python:3.11-slim

# Install requirements terlebih dahulu untuk caching layer
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy semua file ke dalam container
COPY . .

# Jalankan script utama
CMD ["python", "-u", "main.py"]
