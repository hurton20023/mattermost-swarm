#!/bin/bash
# Generate self-signed certificate for Mattermost Traefik setup

set -e

CERT_DIR="$HOME/mattermost-swarm/nginx/certs"
IP="10.100.6.146"

mkdir -p "$CERT_DIR"

echo "Generating self-signed certificate for $IP..."

openssl req -x509 -newkey rsa:4096 -sha256 -days 3650 -nodes \
  -keyout "$CERT_DIR/key.pem" -out "$CERT_DIR/cert.pem" \
  -subj "/CN=$IP" \
  -addext "subjectAltName=IP:$IP"

echo "Certificate generation complete. Files are in $CERT_DIR"
