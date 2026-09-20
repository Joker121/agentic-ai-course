FROM python:3.11-slim
WORKDIR /app
RUN pip install --no-cache-dir --break-system-packages fastapi uvicorn pydantic httpx click rich razorpay PyYAML python-dotenv
COPY main.py .
EXPOSE 8000
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
