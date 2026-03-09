FROM alpine:3.20

RUN apk add --no-cache \
    python3 \
    ffmpeg \
    nginx \
    nginx-mod-rtmp

WORKDIR /app

COPY relay.py .
COPY nginx.conf /etc/nginx/nginx.conf

RUN mkdir /config
RUN mkdir /var/hls

EXPOSE 8151
EXPOSE 1935

CMD python3 relay.py & nginx -g 'daemon off;'