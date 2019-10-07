FROM python:alpine

RUN apk update && apk add --no-cache ca-certificates gcc musl-dev git jq curl bash

RUN mkdir /dataSTAGE-data-ingestion

COPY . /dataSTAGE-data-ingestion

WORKDIR /dataSTAGE-data-ingestion

RUN pip3 install --upgrade pip && pip3 install pipenv

RUN chmod +x run.sh

CMD ["/bin/bash", "./run.sh"]