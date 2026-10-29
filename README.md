# Android 17 signing keys — LineageOS 24.0

Based on the official [LineageOS lineage-priv-template](https://github.com/LineageOS/scripts/tree/main/lineage-priv-template),
revision `01a110e3a59bbaa7aacdce5c733944f7d9f08f33`.

This branch contains a new shared signing identity for Android 17 and Android 15: standard Android
certificates, 78 certificate overrides, an AVB public key, and generated
`Android.bp` certificate modules. `main` retains the existing Android 15 keys.
The default application/OTA certificate follows the template's `testkey` name;
it is a newly generated key, not the AOSP public test key.

All 89 matching `.pk8` files are intentionally published alongside their
certificates. This is a shared/test signing identity: anyone with repository
access can sign with these keys. `certificates.json` records the public
certificate fingerprints and validity dates.

## Use in an Android checkout

Clone this branch at the path expected by the template:

```bash
git clone -b lineage-24.0 https://github.com/Kyura-Ground/public-keys.git vendor/lineage-priv/keys
```

The checkout already includes the matching signing files; no restore or key
generation step is required. The X00TD LineageOS 22.2 local manifest also selects
this keys branch. Key material is compatible with Android 15; unused certificate
overrides do not select additional ROM modules.

Inherit the configuration from the product:

```make
$(call inherit-product, vendor/lineage-priv/keys/keys.mk)
```

For Evolution-X, sync this repository at `vendor/evolution-priv/keys` and inherit
`vendor/evolution-priv/keys/keys.mk` instead. Signing paths follow the location of
`keys.mk`; both locations use the same certificates. Use the ROM's existing
signing configuration include; an additional device product include is not needed.

The committed `Android.bp` is already generated. In a complete Android source
checkout, `./keys.sh` can regenerate its metadata and fill missing key pairs;
existing complete pairs are preserved. A certificate without its matching
private file causes an error rather than generating a different identity.

`make_key.sh` uses OpenSSL directly and supports `KEY_SUBJECT` for a different
certificate subject. Standard platform keys use RSA 2048; certificate overrides,
AVB and `releasekey` use RSA 4096. Certificates use SHA-256 and 10,000-day validity.
No key-validation step is added to a ROM build script.

The optional upstream `check_keys.py` checks produced APK/APEX container
certificates and needs `requirements.txt` plus the Android apksigner tool. It is
not run automatically. Module-specific APEX payload signing remains governed
by the ROM's APEX key definitions.

This new identity differs from `main`; updates from ROMs signed with the older
keys require a signing migration or a clean installation.

## Changes from the upstream template

- The bundled example release key is replaced by a new locally generated pair.
- All matching key pairs are published as shared/test signing material by request.
- Generation stops on errors and preserves complete existing key pairs.
- An incomplete pair is rejected instead of being overwritten.
- `make_key.sh` uses noninteractive OpenSSL and removes temporary private files.
- OTA certificate metadata points to the same key used for package signing.
