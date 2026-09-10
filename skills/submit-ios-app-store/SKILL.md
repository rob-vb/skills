---
name: submit-ios-app-store
description: Submits a native iOS app to App Store Connect. Use when the user wants to ship, archive, upload, or submit an iPhone app, or mentions App Store, TestFlight, Transporter, Fastlane deliver, or App Store Connect.
---

# Submit an iOS app to the App Store

## Done

The version is in App Store Connect in `Waiting for Review` or later. A Linux box cannot prove that. Prove it with `fastlane deliver --skip_binary_upload --skip_screenshots --skip_metadata` status, or a screenshot of the App Store Connect version page.

Do not click Submit for Review until the operator says to. That send is irreversible.

## Domain

One `StoreApp` record. Keep these fields in one place (`store/app.json` in the app repo, or say them once in the chat). Do not scatter them across scripts.

```
bundleId          string     Xcode PRODUCT_BUNDLE_IDENTIFIER
teamId            string     DEVELOPMENT_TEAM
listingName       string     App Store Connect name, unique, max 30 chars
displayName       string     home screen name, INFOPLIST_KEY_CFBundleDisplayName
sku               string     Connect SKU, immutable after create
primaryCategory   string     e.g. HEALTH_AND_FITNESS
version           string     MARKETING_VERSION
build             string     CURRENT_PROJECT_VERSION
deviceFamily      1 | 1,2    1 = iPhone only
encryptionExempt  bool       ITSAppUsesNonExemptEncryption
privacyPolicyURL  string or none
```

Assets are files, not chat. Put them where the checker looks.

```
icon1024          1024x1024 PNG, no alpha, no rounded corners
screenshots69     1 to 10 PNGs at 1320x2868, 1290x2796, or 1260x2736, no alpha
```

## Workflow

Copy this list and check boxes only when the evidence exists.

```
- [ ] 1. Readiness script is green, or every FAIL has an owner
- [ ] 2. Listing name is reserved in App Store Connect
- [ ] 3. Icon and 6.9" screenshots exist on disk at the required pixels
- [ ] 4. App Store Connect API key is available to this session
- [ ] 5. A Mac or GitHub Actions macos runner archived a signed IPA
- [ ] 6. Build is in Connect under the version
- [ ] 7. Operator said submit
- [ ] 8. Version status is Waiting for Review or later
```

### 1. Readiness

From this skill directory:

```bash
scripts/check-readiness.sh --project /path/to/App.xcodeproj
```

Fix every `FAIL` you can from the current OS. Leave `FAIL` rows that need a Mac, an image, or an Apple login. Show the table to the operator.

Details of each gate live in [references/gates.md](references/gates.md).

### 2. Listing name

Create the app record in App Store Connect as soon as the bundle id and team are known. Apple rejects an exact duplicate name at save time. That is the availability check.

The home screen name can stay the product name when the listing name has to change.

If an existing app already uses the name, stop and ask the operator for a listing name of at most 30 characters. Do not rename the bundle id.

### 3. Images

Stop and list missing files. Do not generate a brand icon or fake device screenshots unless the operator asks.

Required files, sizes, and capture notes are in [references/assets.md](references/assets.md).

### 4. App Store Connect API key

Need all three. Stop if any is missing.

- Issuer ID
- Key ID
- `.p8` private key file, role App Manager or Admin

Create them at [App Store Connect API](https://appstoreconnect.apple.com/access/integrations/api). Put the `.p8` outside git. The operator pastes the values or points at the file.

How to use the key is in [references/asc-api.md](references/asc-api.md).

### 5. Archive

`xcodebuild` and Fastlane need macOS. This session is Linux unless `command -v xcodebuild` succeeds.

On a Mac, archive with automatic signing and the team id from `StoreApp`.

On Linux, add a GitHub Actions `macos-14` workflow that uses the API key, then run it. Do not add Fastlane you cannot run. The first archive you keep is one you watched succeed.

Never commit `.p8`, `.mobileprovision`, or certificates.

### 6. Upload

Upload the IPA with `xcrun altool --upload-app` or Fastlane `pilot` / `deliver`, authenticated by the API key. Wait until Connect shows the build as processed.

### 7. Submit

Fill privacy nutrition labels (this app collects nothing if it only writes a local file). Attach the 6.9" screenshots. Set export compliance from `encryptionExempt`. Then stop.

Submit for Review only after the operator says to.

## Hoppa defaults

Use these when the repo is `hoppa-ios` and the operator has not overridden them.

| Field | Value |
| --- | --- |
| bundleId | `com.robvb.hoppa` |
| teamId | `LBSGW42B34` |
| displayName | Hoppa |
| listingName | ask. `Hoppa` is already on the store ([id6448965355](https://apps.apple.com/gb/app/hoppa/id6448965355)) |
| sku | `hoppa` |
| primaryCategory | Health & Fitness |
| deviceFamily | 1 (iPhone) |
| encryptionExempt | true |
| privacyPolicyURL | ask. Need a public URL if Connect requires one |

`HarnessSeed.isEnabled` must stay `false` in the uploaded binary.
