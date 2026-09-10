#!/usr/bin/env bash
set -euo pipefail

here="$(cd "$(dirname "$0")" && pwd)"

xcode_source_dir() {
	local xcodeproj="$1"
	local parent sibling
	parent="$(dirname "$xcodeproj")"
	sibling="$parent/$(basename "$xcodeproj" .xcodeproj)"
	if [[ -d "$sibling" ]]; then
		printf '%s' "$sibling"
	else
		printf '%s' "$parent"
	fi
}

project=""
while [[ $# -gt 0 ]]; do
	case "$1" in
		--project)
			project="${2:-}"
			shift 2
			;;
		-h|--help)
			printf 'usage: check-readiness.sh --project /path/to/App.xcodeproj\n'
			exit 0
			;;
		*)
			printf 'unknown arg: %s\n' "$1" >&2
			exit 2
			;;
	esac
done

if [[ -z "$project" ]]; then
	printf 'usage: check-readiness.sh --project /path/to/App.xcodeproj\n' >&2
	exit 2
fi

if [[ ! -d "$project" ]]; then
	printf 'project not found: %s\n' "$project" >&2
	exit 2
fi

pbx="$project/project.pbxproj"
if [[ ! -f "$pbx" ]]; then
	printf 'missing project.pbxproj in %s\n' "$project" >&2
	exit 2
fi

source_dir="$(xcode_source_dir "$project")"
app_dir="$(dirname "$project")"
repo_root="$(git -C "$app_dir" rev-parse --show-toplevel 2>/dev/null || printf '%s' "$app_dir")"
shots_dir="$repo_root/store/screenshots/iphone-6.9"

fail=0
printf 'gate\tstatus\tdetail\n'

pass() { printf '%s\tPASS\t%s\n' "$1" "$2"; }
fail_row() {
	printf '%s\tFAIL\t%s\n' "$1" "$2"
	fail=1
}

settings="$(python3 "$here/pbx_app_settings.py" "$pbx" || true)"

setting() {
	local key="$1"
	printf '%s\n' "$settings" | awk -F= -v k="$key" '$1 == k { print substr($0, index($0, "=") + 1); exit }'
}

if [[ -z "$settings" ]]; then
	fail_row "bundle-id" "could not parse app target from project.pbxproj"
	fail_row "team-id" "could not parse app target from project.pbxproj"
	fail_row "display-name" "could not parse app target from project.pbxproj"
	fail_row "encryption" "could not parse app target from project.pbxproj"
	fail_row "device-family" "could not parse app target from project.pbxproj"
	fail_row "version" "could not parse app target from project.pbxproj"
else
	bundle="$(setting PRODUCT_BUNDLE_IDENTIFIER)"
	team="$(setting DEVELOPMENT_TEAM)"
	display="$(setting INFOPLIST_KEY_CFBundleDisplayName)"
	encrypt="$(setting INFOPLIST_KEY_ITSAppUsesNonExemptEncryption)"
	family="$(setting TARGETED_DEVICE_FAMILY)"
	marketing="$(setting MARKETING_VERSION)"
	build="$(setting CURRENT_PROJECT_VERSION)"

	if [[ -n "$bundle" && "$bundle" != *"Tests"* ]]; then
		pass "bundle-id" "$bundle"
	else
		fail_row "bundle-id" "missing PRODUCT_BUNDLE_IDENTIFIER on the app target"
	fi

	if [[ "$team" =~ ^[A-Z0-9]{10}$ ]]; then
		pass "team-id" "$team"
	else
		fail_row "team-id" "DEVELOPMENT_TEAM is '${team:-empty}', want a 10-character id"
	fi

	if [[ -n "$display" ]]; then
		pass "display-name" "$display"
	else
		fail_row "display-name" "missing INFOPLIST_KEY_CFBundleDisplayName"
	fi

	if [[ "$encrypt" == "NO" ]]; then
		pass "encryption" "ITSAppUsesNonExemptEncryption = NO"
	else
		fail_row "encryption" "set INFOPLIST_KEY_ITSAppUsesNonExemptEncryption = NO unless you ship custom crypto"
	fi

	if [[ -n "$family" ]]; then
		pass "device-family" "$family"
	else
		fail_row "device-family" "missing TARGETED_DEVICE_FAMILY"
	fi

	if [[ -n "$marketing" && -n "$build" ]]; then
		pass "version" "MARKETING_VERSION=$marketing CURRENT_PROJECT_VERSION=$build"
	else
		fail_row "version" "need MARKETING_VERSION and CURRENT_PROJECT_VERSION"
	fi
fi

privacy="$(find "$source_dir" -maxdepth 3 -name PrivacyInfo.xcprivacy -print -quit 2>/dev/null || true)"
if [[ -n "$privacy" ]]; then
	pass "privacy-manifest" "$privacy"
else
	fail_row "privacy-manifest" "no PrivacyInfo.xcprivacy under $source_dir"
fi

icon_dir="$(find "$source_dir" -path '*AppIcon.appiconset' -type d -print -quit 2>/dev/null || true)"
if [[ -z "$icon_dir" ]]; then
	fail_row "icon-1024" "no AppIcon.appiconset"
else
	icon_ok=""
	shopt -s nullglob
	for f in "$icon_dir"/*.png "$icon_dir"/*.PNG; do
		info="$(file -b "$f" 2>/dev/null || true)"
		if [[ "$info" == *"1024 x 1024"* || "$info" == *"1024x1024"* ]]; then
			if python3 "$here/png_has_alpha.py" "$f"; then
				icon_ok="$f"
				break
			fi
		fi
	done
	shopt -u nullglob
	if [[ -n "$icon_ok" ]]; then
		pass "icon-1024" "$icon_ok"
	else
		fail_row "icon-1024" "no 1024x1024 PNG without alpha in $icon_dir"
	fi
fi

if [[ ! -d "$shots_dir" ]]; then
	fail_row "screenshots-6.9" "missing $shots_dir"
else
	shot_count=0
	shot_bad=0
	shopt -s nullglob
	for f in "$shots_dir"/*.png "$shots_dir"/*.jpg "$shots_dir"/*.jpeg; do
		shot_count=$((shot_count + 1))
		if ! python3 "$here/iphone69_screenshot.py" "$f"; then
			shot_bad=$((shot_bad + 1))
		fi
	done
	shopt -u nullglob
	if [[ "$shot_count" -ge 1 && "$shot_count" -le 10 && "$shot_bad" -eq 0 ]]; then
		pass "screenshots-6.9" "$shot_count files in $shots_dir"
	else
		fail_row "screenshots-6.9" "$shot_count files, $shot_bad wrong size or alpha, want 1-10 at 1320x2868 / 1290x2796 / 1260x2736"
	fi
fi

if command -v xcodebuild >/dev/null 2>&1; then
	pass "xcodebuild" "$(command -v xcodebuild)"
else
	fail_row "xcodebuild" "no xcodebuild on this host. Use a Mac or GitHub Actions macos-14"
fi

key_id="${APP_STORE_CONNECT_API_KEY_ID:-}"
issuer="${APP_STORE_CONNECT_ISSUER_ID:-}"
key_path="${APP_STORE_CONNECT_API_KEY_PATH:-}"
if [[ -n "$key_id" && -n "$issuer" && -n "$key_path" && -f "$key_path" ]]; then
	pass "asc-auth" "key id set, issuer set, p8 exists"
else
	fail_row "asc-auth" "set APP_STORE_CONNECT_API_KEY_ID, APP_STORE_CONNECT_ISSUER_ID, APP_STORE_CONNECT_API_KEY_PATH"
fi

exit "$fail"
