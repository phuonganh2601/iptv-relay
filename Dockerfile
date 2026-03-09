FROM python:3.11-alpine

RUN apk add --no-cache ffmpeg

WORKDIR /app

COPY relay.py .

RUN mkdir /hls
RUN mkdir /config

EXPOSE 8151

CMD ["python","relay.py"]