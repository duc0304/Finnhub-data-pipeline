FROM bitnami/spark:3.4.1

# Install curl for healthcheck and other dependencies
USER root
RUN apt-get update && apt-get install -y curl && apt-get clean

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy processor code
COPY processor.py .

# We will use the command from docker-compose.yml instead
# so commenting out the default CMD
# CMD ["spark-submit", \
#     "--packages", \
#     "org.apache.spark:spark-sql-kafka-0-10_2.12:3.4.1,com.datastax.spark:spark-cassandra-connector_2.12:3.4.0", \
#     "processor.py"] 