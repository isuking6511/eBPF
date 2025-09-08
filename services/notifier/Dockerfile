FROM python:3.11-slim
RUN pip install fastapi uvicorn prometheus-client
WORKDIR /app
COPY app.py .
EXPOSE 8080 9102
CMD ["uvicorn","app:app","--host","0.0.0.0","--port","8080"]
