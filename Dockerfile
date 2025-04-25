FROM python:3.11-slim

WORKDIR /app
COPY . .
RUN pip install --no-cache-dir -r requirements.txt

# Ensure Python can find the app module
ENV PYTHONPATH=/app

EXPOSE 8080
EXPOSE 9090

CMD ["python", "app/main.py"]