#!/bin/bash

# Create keys directory if it doesn't exist
mkdir -p keys

# Generate private key
openssl genrsa -out keys/private_key.pem 2048

# Generate public key
openssl rsa -in keys/private_key.pem -pubout -out keys/public_key.pem

echo "JWT keys generated successfully!"
echo "Private key: keys/private_key.pem"
echo "Public key: keys/public_key.pem"