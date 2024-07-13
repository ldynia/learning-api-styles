#!/usr/bin/env bash

set -Eeuo pipefail

WORK_DIR=$(basename $(pwd))
ROOT_DIR="network"
if [[ "$WORK_DIR" != "$ROOT_DIR" ]]; then
  echo "Error: Script must be run from the $ROOT_DIR directory"
  exit 1
fi

echo "Executing: $0"

docker compose version

export BUILDKIT_PROGRESS=plain
# tag::build_container_images[]
docker compose build --build-arg UID=$(id -u) --build-arg GID=$(id -g)
# end::build_container_images[]

# tag::start_containers[]
docker compose up --detach --wait
# end::start_containers[]

# tag::wait_for_containers[]
timeout 30 bash -c 'while true; do if docker compose ps -q client --filter status=running; then break; else sleep 5; fi; done'
timeout 30 bash -c 'while true; do if docker compose ps -q router --filter status=running; then break; else sleep 5; fi; done'
timeout 30 bash -c 'while true; do if docker compose ps -q server --filter status=running; then break; else sleep 5; fi; done'
# end::wait_for_containers[]

echo "create_self_signed_root_ca_certificate"
# tag::create_self_signed_root_ca_certificate[]
docker compose exec server bash -c \
       'openssl req -x509 -newkey rsa:3072 -days 3650 -nodes \
       -keyout ca.key -out ca.crt -subj "/CN=example.com Root CA" \
       -addext "basicConstraints=critical,CA:TRUE" \
       -addext "keyUsage=cRLSign,keyCertSign"'
# end::create_self_signed_root_ca_certificate[]

echo "create_issuing_ca_certificate_signing_request"
# tag::create_issuing_ca_certificate_signing_request[]
docker compose exec server bash -c \
       'openssl req -new -newkey ec:<(openssl ecparam -name prime256v1) -nodes \
       -keyout ica.key -out ica.csr -subj "/CN=example.com Issuing CA"'
# end::create_issuing_ca_certificate_signing_request[]

echo "sign_issuing_ca_certificate_signing_request"
# tag::sign_issuing_ca_certificate_signing_request[]
docker compose exec server bash -c \
       'openssl x509 -req -CAcreateserial -days 365 \
       -in ica.csr -out ica.crt -CA ca.crt -CAkey ca.key \
       -extfile <(printf "basicConstraints=critical,CA:TRUE\n\
       keyUsage=keyCertSign,cRLSign")'
# end::sign_issuing_ca_certificate_signing_request[]

echo "print_issuing_ca_certificate"
# tag::print_issuing_ca_certificate[]
docker compose exec server bash -c 'openssl x509 -in ica.crt -noout -text'
# end::print_issuing_ca_certificate[]

echo "verify_issuing_ca_certificate"
# tag::verify_issuing_ca_certificate[]
docker compose exec server bash -c \
       'openssl verify -show_chain -CAfile ca.crt ica.crt'
# end::verify_issuing_ca_certificate[]

echo "create_server_certificate_signing_request"
# tag::create_server_certificate_signing_request[]
docker compose exec server bash -c \
       'openssl req -new -newkey ec:<(openssl ecparam -name prime256v1) -nodes \
       -keyout server.key -out server.csr -subj "/CN=server" \
       -addext "subjectAltName=DNS:server"'
# end::create_server_certificate_signing_request[]

echo "sign_server_certificate_signing_request"
# tag::sign_server_certificate_signing_request[]
docker compose exec server bash -c \
       'openssl x509 -req -CAcreateserial -days 365 -copy_extensions copy \
       -in server.csr -out server.crt -CA ica.crt -CAkey ica.key \
       -extfile <(printf "basicConstraints=critical,CA:FALSE\n\
       keyUsage=digitalSignature\nextendedKeyUsage=serverAuth")'
# end::sign_server_certificate_signing_request[]

echo "create_server_certificate_chain"
# tag::create_server_certificate_chain[]
docker compose exec server bash -c \
      'cat server.crt ica.crt > server_chain.crt'
# end::create_server_certificate_chain[]

echo "print_server_certificate"
# tag::print_server_certificate[]
docker compose exec server bash -c 'openssl x509 -in server.crt -noout -text'
# end::print_server_certificate[]

echo "verify_server_certificate"
# tag::verify_server_certificate[]
docker compose exec server bash -c \
       'openssl verify -show_chain -trusted ca.crt -trusted ica.crt server.crt'
# end::verify_server_certificate[]

# tag::deploy_server_certificate_chain_and_private_key[]
docker compose exec server bash -c \
       'sudo cp -pf ca.crt /etc/ssl/certs && \
       sudo cp -pf server_chain.crt /etc/ssl/certs && \
       sudo cp -pf server.key /etc/ssl/private && \
       sudo chmod go-rwx /etc/ssl/private/server.key'
# end::deploy_server_certificate_chain_and_private_key[]

# tag::configure_stunnel[]
docker compose exec server bash -c 'sudo sed -i "1i Options = NoTicket" /etc/ssl/openssl.cnf'  # Disable TLS session tickets
docker compose exec server bash -c 'sudo cp -f src/stunnel.conf /etc/stunnel'
docker compose exec server bash -c 'sudo /etc/init.d/stunnel4 restart'
# end::configure_stunnel[]

id && pwd && ls -al
docker compose exec client bash -c "id && pwd && ls -al"
