# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Para asegurar que los logs se emitan en tiempo real
ENV PYTHONUNBUFFERED=1

# Set the working directory to /app
WORKDIR /app

# Install any needed packages specified in requirements.txt
RUN pip install kazoo requests

# Copy the source code
COPY src/main_part_1_2_3.py .

# Configurar el punto de entrada para permitir el paso de argumentos por línea de comandos
# Esto permite que Docker Compose le pase el ID único a cada instancia [cite: 124, 126]
ENTRYPOINT ["python", "main_part_1_2_3.py"]

# Define environment variable
# Valores por defecto para el entorno de Docker
ENV ZK_HOST=zookeeper:2181
ENV API_URL=http://api-measurements:4000/
ENV SAMPLING_PERIOD=5
