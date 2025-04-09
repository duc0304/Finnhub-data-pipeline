FROM bitnami/spark:3.4.1

# Install curl for healthcheck and other dependencies
USER root
RUN apt-get update && apt-get install -y curl && apt-get clean

WORKDIR /app

# Cài đặt Cassandra connector và các dependency cần thiết
ENV SPARK_EXTRA_JARS_DIR=/opt/bitnami/spark/jars/
ENV SPARK_EXTRA_CLASSPATH=/opt/bitnami/spark/jars/*

# Tải Cassandra connector và các dependency cần thiết
RUN mkdir -p /tmp/spark-jars && \
    cd /tmp/spark-jars && \
    curl -O https://repo1.maven.org/maven2/com/datastax/spark/spark-cassandra-connector_2.12/3.4.0/spark-cassandra-connector_2.12-3.4.0.jar && \
    curl -O https://repo1.maven.org/maven2/com/datastax/spark/spark-cassandra-connector-driver_2.12/3.4.0/spark-cassandra-connector-driver_2.12-3.4.0.jar && \
    curl -O https://repo1.maven.org/maven2/com/datastax/oss/java-driver-core/4.14.1/java-driver-core-4.14.1.jar && \
    curl -O https://repo1.maven.org/maven2/io/netty/netty-buffer/4.1.58.Final/netty-buffer-4.1.58.Final.jar && \
    curl -O https://repo1.maven.org/maven2/io/netty/netty-codec/4.1.58.Final/netty-codec-4.1.58.Final.jar && \
    curl -O https://repo1.maven.org/maven2/io/netty/netty-common/4.1.58.Final/netty-common-4.1.58.Final.jar && \
    curl -O https://repo1.maven.org/maven2/io/netty/netty-handler/4.1.58.Final/netty-handler-4.1.58.Final.jar && \
    curl -O https://repo1.maven.org/maven2/io/netty/netty-resolver/4.1.58.Final/netty-resolver-4.1.58.Final.jar && \
    curl -O https://repo1.maven.org/maven2/io/netty/netty-transport/4.1.58.Final/netty-transport-4.1.58.Final.jar && \
    cp *.jar $SPARK_EXTRA_JARS_DIR && \
    cd / && \
    rm -rf /tmp/spark-jars

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