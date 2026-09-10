#!/usr/bin/env python3
"""Read PRODUCT_* and INFOPLIST_* from the app target's Release XCBuildConfiguration."""
import re
import sys

WANTED = (
    "PRODUCT_BUNDLE_IDENTIFIER",
    "DEVELOPMENT_TEAM",
    "INFOPLIST_KEY_CFBundleDisplayName",
    "INFOPLIST_KEY_ITSAppUsesNonExemptEncryption",
    "TARGETED_DEVICE_FAMILY",
    "MARKETING_VERSION",
    "CURRENT_PROJECT_VERSION",
)

CONFIG_RE = re.compile(
    r"[A-F0-9]+ /\* (Debug|Release) \*/ = \{\s*isa = XCBuildConfiguration;"
    r"\s*buildSettings = \{(.*?)\n\t\t\t\};\s*name = \1;",
    re.S,
)


def is_test_bundle(ident: str) -> bool:
    return ident.endswith("Tests") or "UITests" in ident


def app_release_settings(pbx_text: str) -> str | None:
    picked = None
    for name, body in CONFIG_RE.findall(pbx_text):
        match = re.search(r"PRODUCT_BUNDLE_IDENTIFIER = ([^;]+);", body)
        if not match:
            continue
        ident = match.group(1).strip()
        if is_test_bundle(ident):
            continue
        if name == "Release":
            return body
        if picked is None:
            picked = body
    return picked


def main() -> int:
    text = open(sys.argv[1], encoding="utf-8").read()
    body = app_release_settings(text)
    if body is None:
        return 1
    for key in WANTED:
        match = re.search(rf"{key} = ([^;]+);", body)
        if match:
            print(f"{key}={match.group(1).strip()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
