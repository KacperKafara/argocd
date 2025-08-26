FROM python:3.12.3-alpine3.20
COPY src /src
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
CMD ["kopf", "run", "--liveness=http://0.0.0.0:8080/healthz", "/src/operator.py"]