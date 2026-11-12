FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
# Expose all possible ports so one file works for every service
EXPOSE 5000 8001 8002 8003 8004 8005
CMD ["python", "app.py"]