# Store assets

Apple's sizes are in [Screenshot specifications](https://developer.apple.com/help/app-store-connect/reference/app-information/screenshot-specifications/). Recheck that page if a gate fails on pixels.

## App icon

- 1024 x 1024 PNG
- No alpha, no transparency
- No rounded corners. Apple applies the mask
- No overlay of "beta", "dev", or the iOS home-screen chrome
- Put the file in `AppIcon.appiconset` and name it in `Contents.json` as the `filename` for the `1024x1024` `ios` slot

A dark square that matches the in-app floor colour is enough if the brand has no other mark. Do not invent a new logo unless asked.

## iPhone screenshots

iPhone-only apps (`TARGETED_DEVICE_FAMILY = 1`) need one 6.9" set. Apple scales it down.

Accepted portrait sizes:

- 1320 x 2868
- 1290 x 2796
- 1260 x 2736

Prefer 1320 x 2868. PNG or JPEG. No alpha.

Capture on an iPhone 16 Pro Max or 17 Pro Max simulator, or a matching device. Status bar time, carrier, and battery should look finished. Do not include the simulator bezel unless it still hits an accepted pixel size exactly.

Put files in `store/screenshots/iphone-6.9/` named `01.png` through `10.png`.

iPad 13" shots are required only when the app runs on iPad.

## What to photograph

Ship the real product, not a marketing collage, unless the operator asks for framed marketing shots.

For a lifting logbook, a useful set is:

1. Empty first run
2. A program with days
3. Logging a set
4. Workout summary after finish
5. History or progress

A Linux UI snapshot from a non-iOS harness is not an App Store screenshot. Resize it only if the operator accepts a marketing frame that still lands on an exact Apple size.
