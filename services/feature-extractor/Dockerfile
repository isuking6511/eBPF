FROM python:3.11-slim
RUN pip install nats-py prometheus-client requests
WORKDIR /app
COPY extractor.py .
ENV NATS_URL=nats://nats:4222 SUB_IN=telemetry.flow INFER_URL=http://inferencer:8080/infer
CMD ["python","extractor.py"]
