#!/bin/sh
set -eu
# DNS del contenedor: resuelve api en Compose y el dominio público en Render.
resolvers=$(awk '$1 == "nameserver" { if ($2 ~ /:/) printf "[%s] ", $2; else printf "%s ", $2 }' /etc/resolv.conf)
test -n "$resolvers"
printf 'resolver %s valid=30s ipv6=off;\n' "$resolvers" > /etc/nginx/conf.d/upstream-resolver.inc
