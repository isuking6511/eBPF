FROM python:3.11-slim
RUN pip install fastapi uvicorn onnxruntime prometheus-client requests
WORKDIR /app
COPY app.py .
EXPOSE 8080 9101
ENV THRESHOLD=0.7
CMD ["uvicorn","app:app","--host","0.0.0.0","--port","8080"]
