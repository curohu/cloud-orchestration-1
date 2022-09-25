FROM python:3

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
WORKDIR /usr/src/app/api-template
CMD ["python", "-m gunicorn api-template:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8080"]
