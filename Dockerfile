FROM alpine:3.20

RUN apk add --no-cache \
    python3 \
    ffmpeg \
    nginx \
    curl

WORKDIR /app

COPY relay.py .
COPY nginx.conf /etc/nginx/nginx.conf

RUN mkdir /hls
RUN mkdir /config

EXPOSE 8151

CMD python3 relay.py & nginx -g 'daemon off;'