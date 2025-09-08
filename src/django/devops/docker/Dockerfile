# syntax=docker/dockerfile:1
ARG PY_VER=3.13
FROM python:${PY_VER}-slim-trixie
ARG PY_VER

ARG APP_TLS_CERTS_DIR=/etc/wfs/ssl/certs \
    APP_TLS_PRICATE_DIR=/etc/wfs/ssl/private \
    APP_PORT_HTTP=8000 \
    APP_PORT_WS=8001 \
    ENVIRONMENT=development \
    GID=1000 \
    GROUP=nonroot \
    TLS_ENABLE=1 \
    UID=1000 \
    USER=nonroot \
    WORKDIR=/usr/src

ENV APP_TLS_CERTS_DIR=$APP_TLS_CERTS_DIR \
    APP_TLS_PRICATE_DIR=$APP_TLS_PRICATE_DIR \
    APP_PORT_HTTP=$APP_PORT_HTTP \
    APP_PORT_WS=$APP_PORT_WS \
    ENVIRONMENT=$ENVIRONMENT \
    PYTHONIOENCODING=UTF-8 \
    PYTHONUNBUFFERED=True \
    TLS_ENABLE=$TLS_ENABLE \
    WORKDIR=$WORKDIR

# Set the UID/GID of the user:group to the IDs of the user using this Dockerfile
RUN echo user:group ${USER}:${GROUP}
RUN echo uid:gid ${UID}:${GID}
RUN getent group ${GROUP} || groupadd --non-unique --gid ${GID} ${GROUP}
RUN getent passwd ${USER} || useradd --uid ${UID} --gid ${GID} --create-home --shell /bin/bash ${USER}
RUN if [ "${GID}" != "1000" ] || [ "${UID}" != "1000" ]; then \
      groupmod --non-unique --gid ${GID} ${GROUP} && \
      usermod --uid ${UID} --gid ${GID} ${USER} && \
      chown -R ${UID}:${GID} /home/${USER}; \
    fi

# Configure sudo
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install --yes --no-install-recommends \
    sudo && \
    rm -rf /var/lib/apt/lists/*
RUN echo "${USER} ALL=(ALL) NOPASSWD: ALL" > /etc/sudoers.d/${USER}
RUN chmod 0440 /etc/sudoers.d/${USER}
RUN sudo -lU ${USER}
USER ${USER}
RUN whoami
RUN sudo ls /etc
USER root

# Required packages
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install --yes --no-install-recommends \
    ack \
    ca-certificates \
    curl \
    gcc \
    libc6-dev \
    libpq-dev \
    newsboat \
    openssl && \
    rm -rf /var/lib/apt/lists/*

# Debugging packages
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install --yes --no-install-recommends \
    arping \
    bind9-dnsutils \
    dnsmasq \
    graphviz \
    iproute2 \
    iptables \
    iputils-ping \
    jq \
    libgraphviz-dev \
    libxml2-utils \
    net-tools \
    netcat-traditional \
    nmap \
    node-ws \
    procps \
    tcpdump \
    tshark \
    vim && \
    rm -rf /var/lib/apt/lists/*

WORKDIR ${WORKDIR}
COPY . ${WORKDIR}

RUN mkdir -p ${APP_TLS_CERTS_DIR} ${APP_TLS_PRICATE_DIR}
RUN chown -R ${USER}:${GROUP} ${APP_TLS_CERTS_DIR} ${APP_TLS_PRICATE_DIR} ${WORKDIR}

USER ${USER}:${GROUP}
ENV PATH=/home/${USER}/.local/bin:${PATH}
RUN python -m pip install --upgrade pip -r ${WORKDIR}/requirements.txt --no-cache-dir

# Assert the expected python version
RUN test $(python -c 'import sys; version=sys.version_info[:2]; print(f"{version[0]}.{version[1]}")') = ${PY_VER}

EXPOSE ${APP_PORT_HTTP} ${APP_PORT_WS}
VOLUME ${WORKDIR}

HEALTHCHECK CMD ${WORKDIR}/scripts/healthcheck.sh || exit 1

ENTRYPOINT /bin/sh -c "${WORKDIR}/scripts/startup.sh"
