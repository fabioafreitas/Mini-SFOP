# syntax=docker/dockerfile:1
FROM python:3.12.2-slim

WORKDIR /app

# Install web dependencies
COPY ./requirements.txt ./requirements.txt
RUN pip install -r ./requirements.txt

# Copy the application
COPY . .

# Set up Django application
WORKDIR /app/backend

# Collect static files at runtime
COPY ./entrypoint.sh ./entrypoint.sh

# Remove Windows-style line endings (\r\n)
RUN sed -i 's/\r$//' ./entrypoint.sh

# Give script root permissions
RUN chmod +x ./entrypoint.sh

# Command to start the server
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers=4", "backend.wsgi:application", "--log-level", "debug"]

# Running script in container runtime to generate static files
# and migrate DB before Django service start in CMD command
ENTRYPOINT ["./entrypoint.sh"]
