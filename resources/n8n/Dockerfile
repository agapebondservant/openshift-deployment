FROM docker.io/library/python:3.12 as builder

USER root

COPY requirements.txt ./requirements.txt

RUN python3 -m pip install --upgrade pip \
        && pip install -r requirements.txt
        #&& chown -R 1001:1001 /usr/local/lib/python3.12/site-packages

FROM n8nio/n8n:1.114.4

USER 1001

COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages

USER node