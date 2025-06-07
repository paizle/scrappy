FROM python:3.9-slim-buster

WORKDIR /app

# Copy only the requirements.txt file first
COPY app/requirements.txt .

# Install dependencies
RUN pip install -r requirements.txt

# Copy the application source code
COPY app .

CMD ["python", "./main.py"]