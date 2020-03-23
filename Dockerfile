FROM python:3.6-slim-buster

RUN apt update && apt install -y git jq curl bash snapd groff python3-pip hub zip

RUN curl -O https://bootstrap.pypa.io/get-pip.py

RUN python3 get-pip.py

RUN pip3 install awscli

# Installing gcloud package (includes gsutil)
RUN curl https://dl.google.com/dl/cloudsdk/release/google-cloud-sdk.tar.gz > /tmp/google-cloud-sdk.tar.gz
RUN mkdir -p /usr/local/gcloud \
  && tar -C /usr/local/gcloud -xvf /tmp/google-cloud-sdk.tar.gz \
  && /usr/local/gcloud/google-cloud-sdk/install.sh
ENV PATH $PATH:/usr/local/gcloud/google-cloud-sdk/bin

RUN mkdir /dataSTAGE-data-ingestion

WORKDIR /dataSTAGE-data-ingestion

RUN pip3 install --upgrade pip && pip3 install pipenv

COPY . /dataSTAGE-data-ingestion

RUN chmod +x /dataSTAGE-data-ingestion/scripts/generate-file-manifest.sh && chmod +x run.sh

CMD ["/bin/bash", "./run.sh"]