FROM python:alpine

RUN apk update && apk add --no-cache ca-certificates gcc musl-dev git jq curl bash

# Installing aws cli
RUN apk -v --update add \
        python \
        py-pip \
        groff \
        less \
        mailcap \
        && \
    pip install --upgrade awscli==1.14.5 s3cmd==2.0.1 python-magic && \
    apk -v --purge del py-pip && \
    rm /var/cache/apk/*
VOLUME /root/.aws
VOLUME /project
WORKDIR /project

# Installing gcloud package (includes gsutil)
RUN curl https://dl.google.com/dl/cloudsdk/release/google-cloud-sdk.tar.gz > /tmp/google-cloud-sdk.tar.gz
RUN mkdir -p /usr/local/gcloud \
  && tar -C /usr/local/gcloud -xvf /tmp/google-cloud-sdk.tar.gz \
  && /usr/local/gcloud/google-cloud-sdk/install.sh
ENV PATH $PATH:/usr/local/gcloud/google-cloud-sdk/bin

RUN mkdir /dataSTAGE-data-ingestion

COPY . /dataSTAGE-data-ingestion

WORKDIR /dataSTAGE-data-ingestion

RUN pip3 install --upgrade pip && pip3 install pipenv

RUN chmod +x /dataSTAGE-data-ingestion/scripts/generate-file-manifest.sh && chmod +x run.sh

CMD ["/bin/bash", "./run.sh"]