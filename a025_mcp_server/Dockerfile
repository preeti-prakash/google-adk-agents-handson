FROM python:3.12-slim

WORKDIR /app

# Install dependencies first so this layer is cached when only server.py changes
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY server.py .

# Run as a non-root user
RUN adduser --disabled-password --gecos "" appuser
USER appuser

# Listen on all interfaces so Cloud Run can reach the server.
# Cloud Run sets PORT (8080) at runtime; 8080 is the default for local docker run.
ENV HOST=0.0.0.0
ENV PORT=8080
EXPOSE 8080

CMD ["python", "server.py"]
