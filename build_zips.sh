#!/bin/sh
# Builds one zip per skill in dist/, for upload to Claude.ai (Settings → Capabilities → Skills).
set -e
cd "$(dirname "$0")/skills"
rm -f ../dist/*.zip
for s in */; do
  s="${s%/}"
  zip -qr "../dist/$s.zip" "$s" -x '*/__pycache__/*' '*.DS_Store'
  echo "dist/$s.zip"
done
