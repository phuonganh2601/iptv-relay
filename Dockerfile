FROM python:3.11-alpine

RUN apk add --no-cache curl ca-certificates

ARG TARGETARCH

RUN if [ "$TARGETARCH" = "amd64" ]; then \
      URL="https://github.com/shaka-project/shaka-packager/releases/download/v2.6.1/packager-linux-x64"; \
    else \
      URL="https://github.com/shaka-project/shaka-packager/releases/download/v2.6.1/packager-linux-arm64"; \
    fi && \
    curl -L $URL -o /usr/bin/packager && \
    chmod +x /usr/bin/packager

WORKDIR /app

COPY relay.py .

RUN mkdir /hls
RUN mkdir /config

EXPOSE 8151

CMD ["python","relay.py"]