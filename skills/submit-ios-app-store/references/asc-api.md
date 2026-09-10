# App Store Connect API key

Create the key at [Users and Access, Integrations, App Store Connect API](https://appstoreconnect.apple.com/access/integrations/api).

1. Enable the App Store Connect API if it is off.
2. Create a key named after the machine or CI, role **App Manager** or **Admin**.
3. Download the `.p8` once. Apple will not show it again.
4. Copy the Key ID and the Issuer ID from that page.

Give the agent:

```bash
export APP_STORE_CONNECT_API_KEY_ID="..."
export APP_STORE_CONNECT_ISSUER_ID="..."
export APP_STORE_CONNECT_API_KEY_PATH="$HOME/keys/AuthKey_XXXXXX.p8"
```

Or GitHub Actions secrets with those same names, plus the `.p8` body in `APP_STORE_CONNECT_API_KEY_KEY`.

Fastlane:

```ruby
api_key = app_store_connect_api_key(
  key_id: ENV.fetch("APP_STORE_CONNECT_API_KEY_ID"),
  issuer_id: ENV.fetch("APP_STORE_CONNECT_ISSUER_ID"),
  key_filepath: ENV.fetch("APP_STORE_CONNECT_API_KEY_PATH")
)
```

`xcrun altool` / `notarytool` accept `--apiKey` and `--apiIssuer` with the `.p8` in `~/.appstoreconnect/private_keys/`.

Do not paste the `.p8` into git, chat logs, or screenshots. If it leaks, revoke it on the Integrations page and make a new key.
