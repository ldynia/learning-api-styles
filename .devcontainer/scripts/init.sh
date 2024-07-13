#!/usr/bin/env bash

set -Eeuo pipefail

function install() {
  curl --silent https://ngrok-agent.s3.amazonaws.com/ngrok.asc | sudo tee /etc/apt/trusted.gpg.d/ngrok.asc > /dev/null
  echo "deb https://ngrok-agent.s3.amazonaws.com buster main" | sudo tee /etc/apt/sources.list.d/ngrok.list

  npm install --global \
    @asyncapi/generator \
    wscat

  sudo apt-get update && sudo DEBIAN_FRONTEND=noninteractive apt-get install -y \
    bash-completion \
    git-core \
    jq \
    newsboat \
    ngrok \
    screen \
    tmux \
    tshark \
    vim
}

function autocomplete() {
  source /usr/share/bash-completion/completions/git
  sudo curl -o /etc/bash_completion.d/docker \
    https://raw.githubusercontent.com/docker/docker-ce/master/components/cli/contrib/completion/bash/docker
  source ~/.bashrc
}

function configure_tmux() {
  echo "set -g mouse on" > ~/.tmux.conf
}

# Execut function(s)
install
autocomplete
configure_tmux