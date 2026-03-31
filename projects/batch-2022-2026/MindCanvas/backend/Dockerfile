FROM python:3.11-slim

WORKDIR /app

ENV PYTHONPATH="${PYTHONPATH}:/app"
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV SENTENCE_TRANSFORMERS_HOME=/app/.st_cache

# Upgrade pip first to avoid JSON index parse bugs
RUN pip install --upgrade pip

# Install CPU-only torch first (~200MB vs ~2GB CUDA build)
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

# Install remaining deps (cached layer)
COPY ./requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . /app/

EXPOSE 8090

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8090"]
