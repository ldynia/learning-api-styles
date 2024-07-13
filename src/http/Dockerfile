FROM debian:testing

ARG WORKDIR=/usr/src/http

# Set the UID/GID of the user:group to the IDs of the user using this Dockerfile
ARG USER=nonroot
ARG GROUP=nonroot
ARG UID=1000
ARG GID=1000
RUN echo user:group ${USER}:${GROUP}
RUN echo uid:gid ${UID}:${GID}
RUN getent group ${GROUP} || groupadd --non-unique --gid ${GID} ${GROUP}
RUN getent passwd ${USER} || useradd --uid ${UID} --gid ${GID} --create-home --shell /bin/false ${USER}
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
RUN sudo -lU ${USER}
USER ${USER}
RUN sudo ls /etc
USER root

# Install lsb-release to obtain the debian release codename
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install --yes --no-install-recommends \
    lsb-release && \
    rm -rf /var/lib/apt/lists/*

# Required packages
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install --yes --no-install-recommends \
    ca-certificates \
    curl \
    firefox-esr \
    git \
    gnutls-bin \
    nghttp2 \
    python-is-python3 \
    python3-pycurl && \
    rm -rf /var/lib/apt/lists/*

# Sanity test curl
RUN which curl
RUN ldd `which curl`
RUN curl --version
RUN curl --version | grep HTTP3

# Debugging packages
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install ---yes --no-install-recommends \
    arping \
    bind9-dnsutils \
    dnsmasq \
    iperf \
    iproute2 \
    iptables \
    iputils-ping \
    less \
    moreutils \
    net-tools \
    netcat-traditional \
    nmap \
    procps \
    tcpdump \
    tshark \
    vim \
    xxd && \
    rm -rf /var/lib/apt/lists/*

WORKDIR ${WORKDIR}
RUN chown ${USER}:${GROUP} ${WORKDIR}

USER ${USER}

CMD ["sleep", "infinity"]
