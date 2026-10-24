#!/usr/bin/env python3
"""Validate Android 15 inline signing keys without generating or replacing keys."""

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys

# Android 15 build/make/target/product/security certificates, plus our OTA signer.
REQUIRED_KEYS = (
    'bluetooth', 'cts_uicc_2021', 'media', 'networkstack', 'nfc',
    'platform', 'releasekey', 'sdk_sandbox', 'shared', 'testkey',
)


class ValidationError(Exception):
    pass


def openssl(*args, data=None):
    try:
        result = subprocess.run(['openssl', *args], input=data, capture_output=True,
                                check=True)
    except FileNotFoundError as error:
        raise ValidationError('openssl is required') from error
    except subprocess.CalledProcessError as error:
        # Do not expose private material or command output in build logs.
        raise ValidationError('OpenSSL rejected the certificate or private key') from error
    return result.stdout


def validate(keys_dir):
    for name in REQUIRED_KEYS:
        for suffix in ('.x509.pem', '.pk8'):
            path = keys_dir / (name + suffix)
            if not path.is_file() or path.stat().st_size == 0:
                raise ValidationError(f'missing signing file: {path.name}')

    now = datetime.now(timezone.utc)
    results = []
    for cert in sorted(keys_dir.glob('*.x509.pem')):
        name = cert.name.removesuffix('.x509.pem')
        key = keys_dir / (name + '.pk8')
        if not key.is_file() or key.stat().st_size == 0:
            raise ValidationError(f'missing private key: {key.name}')
        try:
            dates = dict(line.split('=', 1) for line in
                         openssl('x509', '-in', str(cert), '-noout', '-dates').decode().splitlines())
            not_before = datetime.strptime(dates['notBefore'], '%b %d %H:%M:%S %Y GMT').replace(tzinfo=timezone.utc)
            not_after = datetime.strptime(dates['notAfter'], '%b %d %H:%M:%S %Y GMT').replace(tzinfo=timezone.utc)
            if not not_before <= now < not_after:
                raise ValidationError('certificate is expired or not yet valid')
            public_pem = openssl('x509', '-in', str(cert), '-pubkey', '-noout')
            public_der = openssl('pkey', '-pubin', '-outform', 'DER', data=public_pem)
            private_public_der = openssl('pkey', '-inform', 'DER', '-in', str(key),
                                        '-passin', 'pass:',
                                        '-pubout', '-outform', 'DER')
            if public_der != private_public_der:
                raise ValidationError('certificate and private key do not match')
            cert_der = openssl('x509', '-in', str(cert), '-outform', 'DER')
        except (ValidationError, KeyError, ValueError) as error:
            raise ValidationError(f'{name}: {error}') from error
        results.append({
            'name': name,
            'not_before': not_before.isoformat(),
            'not_after': not_after.isoformat(),
            'certificate_sha256': hashlib.sha256(cert_der).hexdigest(),
        })
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--keys-dir', type=Path, default=Path(__file__).resolve().parent)
    parser.add_argument('--json', action='store_true', help='print certificate metadata only')
    args = parser.parse_args()
    try:
        results = validate(args.keys_dir)
    except ValidationError as error:
        print(f'Signing key validation failed: {error}', file=sys.stderr)
        return 1
    if args.json:
        print(json.dumps(results, indent=2))
    else:
        earliest = min(result['not_after'] for result in results)
        print(f'Validated {len(results)} signing key pairs; earliest expiry: {earliest}.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
