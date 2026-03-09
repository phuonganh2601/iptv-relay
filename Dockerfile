FROM python:3.11-alpine

RUN apk add --no-cache curl ca-certificates

ADD https://github.com/shaka-project/shaka-packager/releases/download/v2.6.1/packager-linux-x64 /usr/bin/packager

RUN chmod +x /usr/bin/packager

WORKDIR /app

COPY relay.py .

RUN mkdir /hls
RUN mkdir /config

EXPOSE 8151

CMD ["python","/app/relay.py"]