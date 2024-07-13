FROM debian:testing

ARG WORKDIR=/usr/src/grpc

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

# Required packages
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install --yes --no-install-recommends \
    ca-certificates \
    curl \
    git \
    jq \
    newsboat \
    python-is-python3 \
    python3-venv && \
    rm -rf /var/lib/apt/lists/*

# Debugging packages
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install ---yes --no-install-recommends \
    arping \
    bind9-dnsutils \
    dnsmasq \
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

# Additional required packages installed manually
RUN curl -sL https://api.github.com/repos/fullstorydev/grpcurl/releases/latest | \
    jq -r '.assets[] | .browser_download_url' | \
    grep deb | grep -E "$(uname -m | sed 's/x86_64/amd64/;s/aarch64/arm64/')" | \
    tee /dev/tty | xargs curl -sL -o grpcurl.deb && \
    dpkg -i grpcurl.deb && rm -f grpcurl.deb && which grpcurl && grpcurl --version
RUN curl -sL https://api.github.com/repos/bufbuild/buf/releases/latest | \
    jq -r '.assets[] | .browser_download_url' | \
    grep Linux | grep -E "$(uname -m)\.tar\.gz" | \
    tee /dev/tty | xargs curl -sL | \
    tar -xvzf - -C /usr/local --strip-components 1 && which buf && buf --version

WORKDIR ${WORKDIR}
RUN chown ${USER}:${GROUP} ${WORKDIR}

USER ${USER}

COPY src/requirements.txt requirements.txt
RUN cd /home/${USER} && python -m venv venv && . venv/bin/activate
RUN . /home/${USER}/venv/bin/activate && python -m pip install -r requirements.txt
RUN echo "if [ -f /home/${USER}/venv/bin/activate  ]; then . /home/${USER}/venv/bin/activate; fi" >> /home/${USER}/.bashrc

# Configure huggingface transformers
ENV HF_HOME=${WORKDIR}
ENV OPENBLAS_NUM_THREADS=1

SHELL ["/bin/bash", "-l", "-c"]

CMD ["sleep", "infinity"]
