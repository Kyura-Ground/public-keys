# LineageOS signing keys

Use at `vendor/lineage-priv/keys` and inherit `keys.mk` from the product.
The existing certificates are RSA 2048/SHA-256 pairs created in March 2025,
valid until July 2052. Their age does not require replacing them for Android 15.
The standard Android 15 certificate names are present.

This public repository contains private `.pk8` files. Its keys are shared/test
keys, not a secret release-signing identity. For private releases, keep a separate
key set outside public source control. Switching keys on an installed ROM needs
a planned signing migration; the validation tool never rotates keys.

`keys.mk` preserves the existing `releasekey` as the default application and OTA
signer for `user`/`userdebug`. OTA metadata lists `releasekey` first, and the
existing `otakey` is added to both system and recovery trust stores. `eng` keeps
the platform defaults.

Validate every certificate/private-key pair and all required Android 15 names:

```bash
python3 vendor/lineage-priv/keys/validate_keys.py
```

The validator checks matching public keys and certificate validity dates. It
does not generate or replace files and never prints private key material.
`--json` outputs certificate fingerprints and dates for audits.

This is inline build signing. Module-specific APEX payload keys and presigned
vendor APKs remain governed by their platform definitions; this configuration
does not claim to re-sign every component with private release keys.

References: [AOSP release signing](https://source.android.com/docs/core/ota/sign_builds),
[Android 15 Make signing](https://github.com/LineageOS/android_build/blob/lineage-22.2/core/config.mk),
[Soong signing configuration](https://github.com/LineageOS/android_build_soong/blob/lineage-22.2/android/config.go).
