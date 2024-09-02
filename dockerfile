
FROM python:3.12.3-slim


WORKDIR /app


RUN apt-get update && apt-get install -y \
    gcc \
    libffi-dev \
    libssl-dev \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

COPY . /app


RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8080

CMD ["uvicorn", "appfast:app", "--host", "0.0.0.0", "--port", "8080"]
