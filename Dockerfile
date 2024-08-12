FROM python:2.7-alpine3.11
WORKDIR /app
COPY . .
RUN apk upgrade
CMD sh