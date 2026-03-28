FROM node:20-slim AS node_base

RUN npm install -g opencode-ai@1.3.2 @fission-ai/openspec@1.2.0 opencode-plugin-openspec

FROM quay.io/modh/odh-generic-data-science-notebook@sha256:7c1a4ca213b71d342a2d1366171304e469da06d5f15710fab5dd3ce013aa1b73

ENV OPENCODE_CONFIG_DIR=/workspace/.opencode_config

USER root

COPY --from=node_base /usr/local/bin /usr/local/bin
COPY --from=node_base /usr/local/lib/node_modules /usr/local/lib/node_modules

RUN printf '#!/bin/sh\nopencode-ai "$@"\n' > /usr/local/bin/opencode \
    && printf '#!/bin/sh\nfission-openspec "$@"\n' > /usr/local/bin/openspec \
    && chmod a+x /usr/local/bin/opencode /usr/local/bin/openspec


RUN chgrp -R 0 /usr/local/lib/node_modules \
    && chmod -R g=u /usr/local/lib/node_modules \
    && chgrp -R 0 /usr/local/bin \
    && chmod -R g=u /usr/local/bin

USER 1001

COPY requirements.txt ./requirements.txt

RUN pip install --upgrade pip \
	&& pip install -r requirements.txt \
    && wget https://www.sqlite.org/src/tarball/sqlite.tar.gz?r=release -O sqlite.tar.gz \
    && tar xzf sqlite.tar.gz \
    && cd sqlite/ \
    && ./configure \
    && make sqlite3.c \
    && cd - \
    && git clone https://github.com/coleifer/pysqlite3.git \
    && cp sqlite/sqlite3.[ch] pysqlite3 \
    && cd pysqlite3 \
    && python setup.py build \
    && pip install . \
    && cd -
