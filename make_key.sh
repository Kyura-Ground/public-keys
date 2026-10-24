#!/bin/bash
# SPDX-FileCopyrightText: The LineageOS Project
# SPDX-License-Identifier: Apache-2.0
set -euo pipefail

name=${1:?Usage: make_key.sh NAME [BITS]}
bits=${2:-2048}
if [[ -e "$name.pk8" && -e "$name.x509.pem" ]]; then
    echo "Keeping existing key: $name"
    exit 0
fi
if [[ -e "$name.pk8" || -e "$name.x509.pem" ]]; then
    echo "Incomplete key pair: $name; refusing to replace it." >&2
    exit 1
fi

umask 077
tmp_dir=$(mktemp -d)
trap 'rm -rf -- "$tmp_dir"' EXIT
openssl genrsa -out "$tmp_dir/key.pem" "$bits" 2>/dev/null
openssl req -new -x509 -sha256 -key "$tmp_dir/key.pem" \
    -out "$tmp_dir/certificate.pem" -days 10000 \
    -subj "${KEY_SUBJECT:-/C=ID/O=Kyura-Ground/OU=Android 17/CN=Kyura Android 17}"
openssl pkcs8 -topk8 -nocrypt -in "$tmp_dir/key.pem" -outform DER -out "$tmp_dir/key.pk8"
install -m 600 "$tmp_dir/key.pk8" "$name.pk8"
install -m 644 "$tmp_dir/certificate.pem" "$name.x509.pem"
echo "Created key: $name"
