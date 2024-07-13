#!/usr/bin/env bash

set -Eeuo pipefail

function autocomplete() {
  source /usr/share/bash-completion/completions/git
  sudo curl -o /etc/bash_completion.d/docker \
    https://raw.githubusercontent.com/docker/docker-ce/master/components/cli/contrib/completion/bash/docker
  source ~/.bashrc
}

function configure_tmux() {
  echo "set -g mouse on" > ~/.tmux.conf
}

autocomplete
configure_tmux
