#!/usr/bin/env bash

set -Eeuo pipefail

WORK_DIR=$(basename $(pwd))
ROOT_DIR="grpc"
if [[ "$WORK_DIR" != "$ROOT_DIR" ]]; then
  echo "Error: Script must be run from the $ROOT_DIR directory"
  exit 1
fi

echo "Executing: $0"

docker compose version

export BUILDKIT_PROGRESS=plain
# tag::build_container_images[]
docker compose build --build-arg UID=$(id -u) --build-arg GID=$(id -g) # <2>
# end::build_container_images[]

# tag::start_containers[]
docker compose up --detach --wait # <3>
# end::start_containers[]

# tag::wait_for_containers[]
timeout 30 bash -c 'while true; do if docker compose ps -q client --filter status=running; then break; else sleep 5; fi; done'
timeout 30 bash -c 'while true; do if docker compose ps -q server --filter status=running; then break; else sleep 5; fi; done'
# end::wait_for_containers[]

# tag::buf_lint_proto_for_echo[]
docker compose exec client bash -ic "cd src/echo/echo/proto && buf lint"
# end::buf_lint_proto_for_echo[]
# tag::buf_format_proto_for_echo[]
docker compose exec client bash -ic "cd src/echo/echo/proto && buf format --diff --write"
# end::buf_format_proto_for_echo[]
# tag::generate_grpc_client_and_server_interfaces_for_echo[]
docker compose exec client bash -ic \
       "cd src/echo && \
       python -m grpc_tools.protoc \
       --proto_path=echo/proto/echo/v1=echo/proto/echo/v1 \
       --python_out=. --grpc_python_out=. \
       echo/proto/echo/v1/echo.proto"
# end::generate_grpc_client_and_server_interfaces_for_echo[]

# tag::buf_lint_proto_for_enricher[]
docker compose exec client bash -ic "cd src/enricher/enricher/proto && buf lint"
# end::buf_lint_proto_for_enricher[]
# tag::buf_format_proto_for_enricher[]
docker compose exec client bash -ic "cd src/enricher/enricher/proto && buf format --diff --write"
# end::buf_format_proto_for_enricher[]
docker compose exec client bash -c "cd src/enricher && rm -rf build *.egg-info"
# tag::generate_grpc_client_and_server_interfaces_for_enricher[]
docker compose exec client bash -ic \
       "cd src/enricher && \
       python -m grpc_tools.protoc \
       --proto_path=enricher/proto/enricher/v1=enricher/proto/enricher/v1 \
       --python_out=. --grpc_python_out=. \
       enricher/proto/enricher/v1/enricher.proto"
# end::generate_grpc_client_and_server_interfaces_for_enricher[]

echo "create_self_signed_root_ca_certificate"
# tag::create_self_signed_root_ca_certificate[]
docker compose exec server bash -c \
       'cd src && \
       openssl req -x509 -newkey ec:<(openssl ecparam -name prime256v1) -days 3650 -nodes \
       -keyout ca.key -out ca.crt -subj "/CN=example.com Root CA" \
       -addext "basicConstraints=critical,CA:TRUE" \
       -addext "keyUsage=cRLSign,keyCertSign"'
# end::create_self_signed_root_ca_certificate[]

echo "create_server_certificate_signing_request"
# tag::create_server_certificate_signing_request[]
docker compose exec server bash -c \
       'cd src && \
       openssl req -new -newkey ec:<(openssl ecparam -name prime256v1) -nodes \
       -keyout server.key -out server.csr -subj "/CN=server" \
       -addext "subjectAltName=DNS:server"'
# end::create_server_certificate_signing_request[]

echo "sign_server_certificate_signing_request"
# tag::sign_server_certificate_signing_request[]
docker compose exec server bash -c \
       'cd src && \
       openssl x509 -req -CAcreateserial -days 365 -copy_extensions copy \
       -in server.csr -out server.crt -CA ca.crt -CAkey ca.key \
       -extfile <(printf "basicConstraints=critical,CA:FALSE\n\
       keyUsage=digitalSignature\nextendedKeyUsage=serverAuth")'
# end::sign_server_certificate_signing_request[]

echo "create_client_certificate_signing_request"
# tag::create_client_certificate_signing_request[]
docker compose exec client bash -c \
       'cd src && \
       openssl req -new -newkey ec:<(openssl ecparam -name prime256v1) -nodes \
       -keyout client.key -out client.csr -subj "/CN=client" \
       -addext "subjectAltName=DNS:client"'
# end::create_client_certificate_signing_request[]

echo "sign_client_certificate_signing_request"
# tag::sign_client_certificate_signing_request[]
docker compose exec client bash -c \
       'cd src && \
       openssl x509 -req -CAcreateserial -days 365 -copy_extensions copy \
       -in client.csr -out client.crt -CA ca.crt -CAkey ca.key \
       -extfile <(printf "basicConstraints=critical,CA:FALSE\n\
       keyUsage=digitalSignature\nextendedKeyUsage=clientAuth")'
# end::sign_client_certificate_signing_request[]

docker ps

id && pwd && ls -al
docker compose exec client bash -c "id && pwd && ls -al"
