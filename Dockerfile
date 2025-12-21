# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Para asegurar que los logs se emitan en tiempo real se vean en el contentenedor
ENV PYTHONUNBUFFERED=1

# Set the working directory to /app
WORKDIR /app

# Install any needed packages
RUN pip install kazoo requests

# Copy the source code
COPY src/main_all_docker.py .

# Configurar el punto de entrada para permitir el paso de argumentos por línea de comandos
# Permite que Docker Compose le pase el ID único a cada instancia
ENTRYPOINT ["python", "main_all_docker.py"]

# Define environment variable
ENV ZK_HOST=zookeeper:2181
ENV API_URL=http://api-measurements:4000/
ENV SAMPLING_PERIOD=5
