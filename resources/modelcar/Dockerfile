FROM registry.access.redhat.com/ubi9/python-311:latest as base

ARG HF_TOKEN

ENV HF_TOKEN=${HF_TOKEN}

USER root

RUN pip install huggingface-hub

COPY download_model.py .

RUN python download_model.py

FROM registry.access.redhat.com/ubi9/ubi-micro:9.4

COPY --from=base /models /models

USER 1001