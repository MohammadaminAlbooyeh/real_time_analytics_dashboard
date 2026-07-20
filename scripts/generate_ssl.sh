#!/bin/bash
# Generate self-signed SSL certificates for development
# For production, use Let's Encrypt or a trusted CA

SSL_DIR="$(dirname "$0")/../nginx/ssl"
mkdir -p "$SSL_DIR"

openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout "$SSL_DIR/key.pem" \
    -out "$SSL_DIR/cert.pem" \
    -subj "/CN=localhost/O=Analytics Dashboard/C=US"

echo "✅ SSL certificates generated at $SSL_DIR"
echo "   cert.pem - Self-signed certificate"
echo "   key.pem  - Private key"
echo ""
echo "⚠️  For production, replace these with Let's Encrypt certificates"
echo "   certbot --nginx -d yourdomain.com"
