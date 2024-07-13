#!/usr/bin/env bash

set -Eeuo pipefail

WORK_DIR=$(basename $(pwd))
ROOT_DIR="http"
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
timeout 30 bash -c 'while true; do if docker compose ps -q http-server --filter status=running; then break; else sleep 5; fi; done'
timeout 30 bash -c 'while true; do if docker compose ps -q https-server --filter status=running; then break; else sleep 5; fi; done'
# end::wait_for_containers[]

# tag:configure_httpd[]
# Enforce HTTP/1.0 responses for all HTTP/1.0 requests, instead of HTTP/1.1
# This still sends "Connection: close" header in HTTP/1.0 response, but it seems not possible to unset
docker compose exec http-server bash -c 'echo # Enforce HTTP/1.0 responses for all HTTP/1.0 requests, instead of HTTP/1.1 >> /usr/local/apache2/conf/httpd.conf'
docker compose exec http-server bash -c 'echo BrowserMatch ".*" force-response-1.0 >> /usr/local/apache2/conf/httpd.conf'
docker compose exec http-server bash -c 'echo SetEnvIf Request_Protocol "HTTP/1\.0" downgrade_http_1_0 >> /usr/local/apache2/conf/httpd.conf'
docker compose exec http-server bash -c 'echo Header unset Connection env=downgrade_http_1_0 >> /usr/local/apache2/conf/httpd.conf'
docker compose exec http-server bash -c 'echo Header unset ETag env=downgrade_http_1_0 >> /usr/local/apache2/conf/httpd.conf'
docker compose exec http-server bash -c 'echo Header unset Accept-Ranges env=downgrade_http_1_0 >> /usr/local/apache2/conf/httpd.conf'
docker compose exec http-server bash -c '/usr/local/apache2/bin/httpd -k restart'
# Configure virtualhost
docker compose exec http-server bash -c 'echo # Configure virtualhost >> /usr/local/apache2/conf/httpd.conf'
docker compose exec http-server bash -c 'echo Include conf/extra/httpd-virtualhost.conf >> /usr/local/apache2/conf/httpd.conf'
docker compose exec http-server bash -c 'cp /usr/src/http/httpd/httpd-virtualhost.conf /usr/local/apache2/conf/extra'
docker compose exec http-server bash -c 'mkdir -p /usr/local/apache2/htdocs/server1.example.com'
docker compose exec http-server bash -c 'echo server1.example.com > /usr/local/apache2/htdocs/server1.example.com/index.html'
docker compose exec http-server bash -c 'mkdir -p /usr/local/apache2/htdocs/server2.example.org'
docker compose exec http-server bash -c 'echo server2.example.com > /usr/local/apache2/htdocs/server2.example.org/index.html'
docker compose exec http-server bash -c '/usr/local/apache2/bin/httpd -k restart'
# Create cgi scripts
docker compose exec http-server bash -c 'cp /usr/src/http/httpd/chunked.sh /usr/local/apache2/cgi-bin/chunked.sh'
docker compose exec http-server bash -c 'cp /usr/src/http/httpd/post.sh /usr/local/apache2/cgi-bin/post.sh'
docker compose exec http-server bash -c 'echo LoadModule cgi_module modules/mod_cgi.so >> /usr/local/apache2/conf/httpd.conf'
docker compose exec http-server bash -c 'chmod a+x /usr/local/apache2/cgi-bin/chunked.sh'
docker compose exec http-server bash -c 'chmod a+x /usr/local/apache2/cgi-bin/post.sh'
docker compose exec http-server bash -c '/usr/local/apache2/bin/httpd -k restart'
# Create HTML pages
docker compose exec http-server bash -c 'echo -ne "Hello\r\n" > /usr/local/apache2/htdocs/Hello.html'
docker compose exec http-server bash -c 'echo -ne "<!DOCTYPE html><title>Hello</title>\r\n" > /usr/local/apache2/htdocs/HelloValid.html'
docker compose exec http-server bash -c 'cp /usr/src/http/httpd/* /usr/local/apache2/htdocs'
# end:configure_httpd[]
# tag:configure_nginx[]
docker compose exec https-server bash -c 'mkdir -p /etc/nginx/ssl'
docker compose exec https-server bash -c 'openssl genpkey -algorithm RSA -out /etc/nginx/ssl/private.key 2>/dev/null'
docker compose exec https-server bash -c 'openssl req -new -x509 -key /etc/nginx/ssl/private.key -out /etc/nginx/ssl/certificate.crt -days 365 -subj "/C=US/ST=California/L=San Francisco/O=Your Organization/OU=Your Unit/CN=https-server"'
docker compose exec https-server bash -c 'cp -f /usr/src/http/nginx/default.conf /etc/nginx/conf.d'
docker compose exec https-server bash -c 'nginx -s reload'
# end:configure_nginx[]
# tag:configure_openssl[]
docker compose exec client bash -c 'sudo openssl genpkey -algorithm RSA -out /etc/ssl/private/openssl.key 2>/dev/null'
docker compose exec client bash -c 'sudo openssl req -new -x509 -key /etc/ssl/private/openssl.key -out /etc/ssl/certs/openssl.crt -days 365 -subj "/C=US/ST=California/L=San Francisco/O=Your Organization/OU=Your Unit/CN=127.0.0.1"'
# end:configure_openssl[]

docker ps

id && pwd && ls -al
docker compose exec client bash -c "id && pwd && ls -al"
