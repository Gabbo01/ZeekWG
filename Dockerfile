FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV PATH="/opt/zeek/bin:$PATH"

# Install system dependencies
RUN apt-get update && \
    apt-get install -y curl git cmake make gcc g++ libpcap-dev \
        libssl-dev python3 python3-pip python3-dev zlib1g-dev \
        bison flex swig 

# Install Zeek
RUN apt update
RUN apt install -y zeek

# Create app directory and copy files
WORKDIR /app
COPY app/ /app/
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Install Python dependencies
RUN pip3 install flask werkzeug google-genai markdown


EXPOSE 5000

ENTRYPOINT ["/entrypoint.sh"]
