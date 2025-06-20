FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV PATH="/usr/local/zeek/bin:$PATH"

# Install system dependencies
RUN apt-get update && \
    apt-get install -y curl git cmake make gcc g++ libpcap-dev \
        libssl-dev python3 python3-pip python3-dev zlib1g-dev \
        bison flex swig 

# Install Zeek
RUN echo 'deb http://download.opensuse.org/repositories/security:/zeek/xUbuntu_22.04/ /' |  tee /etc/apt/sources.list.d/security:zeek.list
RUN curl -fsSL https://download.opensuse.org/repositories/security:zeek/xUbuntu_22.04/Release.key | gpg --dearmor |  tee /etc/apt/trusted.gpg.d/security_zeek.gpg > /dev/null
RUN apt update
RUN apt install -y zeek-6.0

# Create app directory and copy files
WORKDIR /app
COPY app/ /app/
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Install Python dependencies
RUN pip3 install flask werkzeug google-genai markdown


EXPOSE 5000

ENTRYPOINT ["/entrypoint.sh"]
