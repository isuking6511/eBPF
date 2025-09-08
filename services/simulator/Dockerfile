FROM python:3.11-slim
RUN pip install nats-py
WORKDIR /app
COPY gen.py .
CMD ["python","gen.py","--mode","scan","--seconds","10"]
