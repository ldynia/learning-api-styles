#!/usr/bin/env bash

set -Eeuo pipefail

# Install dependencies
apt-get update
apt-get install -y \
  git \
  make \
  openssl

# Clone tls-gen repository
git clone https://github.com/rabbitmq/tls-gen.git /tmp/tls-gen
cd /tmp/tls-gen/basic

# Generate certificates. CN MUST be name of rabbitmq service or hostname
make CN=broker
make CN=broker alias-leaf-artifacts

echo /tmp/tls-gen/basic/result && ls -al /tmp/tls-gen/basic/result

# Copy certificates and fix permissions
mkdir -p /etc/rabbitmq/ssl/certs /etc/rabbitmq/ssl/private

# Private keys
mv result/ca_key.pem \
  result/client_key.pem \
  result/server_key.pem \
  /etc/rabbitmq/ssl/private

# Certificates
mv result/ca_certificate.pem \
  result/client_certificate.pem \
  result/server_certificate.pem \
  /etc/rabbitmq/ssl/certs

chmod 444 /etc/rabbitmq/ssl/certs/*
chmod 444 /etc/rabbitmq/ssl/private/*

echo /etc/rabbitmq/ssl/certs && ls -al /etc/rabbitmq/ssl/certs
echo /etc/rabbitmq/ssl/private && ls -al /etc/rabbitmq/ssl/private
