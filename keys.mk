ifneq (eng,$(TARGET_BUILD_VARIANT))
ifneq (,$(wildcard vendor/lineage-priv/keys/releasekey.pk8))
PRODUCT_DEFAULT_DEV_CERTIFICATE := vendor/lineage-priv/keys/releasekey
PRODUCT_DEFAULT_PROPERTY_OVERRIDES += ro.oem_unlock_supported=1

# The normal OTA signer uses PRODUCT_DEFAULT_DEV_CERTIFICATE. Keep its
# certificate first in target-files META/otakeys.txt as well.
PRODUCT_OTA_PUBLIC_KEYS := $(PRODUCT_DEFAULT_DEV_CERTIFICATE).x509.pem

# Continue trusting the existing OTA certificate in both Android and recovery.
ifneq (,$(wildcard vendor/lineage-priv/keys/otakey.x509.pem))
PRODUCT_OTA_PUBLIC_KEYS += vendor/lineage-priv/keys/otakey.x509.pem
PRODUCT_EXTRA_OTA_KEYS += vendor/lineage-priv/keys/otakey
PRODUCT_EXTRA_RECOVERY_KEYS += vendor/lineage-priv/keys/otakey
endif
endif
endif
