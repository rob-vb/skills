# Readiness gates

`scripts/check-readiness.sh` prints one row per gate. `PASS` or `FAIL`. Exit code 1 if any `FAIL`.

| Gate | Pass when | Who can fix it |
| --- | --- | --- |
| `bundle-id` | `PRODUCT_BUNDLE_IDENTIFIER` is set and is not a `*.tests` id on the app target | Linux |
| `team-id` | `DEVELOPMENT_TEAM` is a 10-character team id | Linux |
| `display-name` | `INFOPLIST_KEY_CFBundleDisplayName` is set | Linux |
| `encryption` | `INFOPLIST_KEY_ITSAppUsesNonExemptEncryption` is `NO` for a local app with no custom crypto | Linux |
| `device-family` | `TARGETED_DEVICE_FAMILY` is present. `1` means iPhone only, so iPad 13" screenshots are not required | Linux |
| `version` | `MARKETING_VERSION` and `CURRENT_PROJECT_VERSION` are set | Linux |
| `privacy-manifest` | `PrivacyInfo.xcprivacy` exists next to the app sources | Linux |
| `icon-1024` | `AppIcon.appiconset` contains a PNG whose pixels are 1024x1024. The file has no alpha | Linux can measure. A person or an image tool must make the file |
| `screenshots-6.9` | `store/screenshots/iphone-6.9/` holds 1 to 10 PNGs at 1320x2868, 1290x2796, or 1260x2736, no alpha | A Mac simulator or a device. Linux snapshots at the wrong size do not pass |
| `xcodebuild` | `command -v xcodebuild` succeeds | A Mac, or GitHub Actions `macos-14` |
| `asc-auth` | `APP_STORE_CONNECT_API_KEY_ID`, `APP_STORE_CONNECT_ISSUER_ID`, and a readable `.p8` path in `APP_STORE_CONNECT_API_KEY_PATH` | Operator |

`asc-auth` reads the environment. It does not print secret values.
