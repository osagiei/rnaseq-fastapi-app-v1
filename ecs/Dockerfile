FROM --platform=linux/amd64 python:3.9-slim

RUN apt-get update && apt-get install -y wget

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 80

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]

