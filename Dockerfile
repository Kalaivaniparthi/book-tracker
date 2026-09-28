# Use Python 3.11 as the base
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Copy requirements first (Docker caches this layer)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the code
COPY . .

# Run the server
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
