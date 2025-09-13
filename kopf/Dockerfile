FROM python:3.12.3-alpine3.20
WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY src src
CMD ["kopf", "run", "--liveness=http://0.0.0.0:8080/healthz", "/app/src/operator.py"]