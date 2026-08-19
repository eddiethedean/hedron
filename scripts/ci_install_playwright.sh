#!/usr/bin/env bash
# Install one Playwright browser plus OS deps. Retries install-deps because
# GitHub ubuntu-latest apt (azure.archive.ubuntu.com / dpkg lock) can hang,
# especially for WebKit's large gstreamer stack.
set -euo pipefail

browser="${1:?browser name required}"
python_version="${2:-3.12}"

export DEBIAN_FRONTEND=noninteractive

sudo systemctl stop apt-daily.service apt-daily-upgrade.service unattended-upgrades.service 2>/dev/null || true
sudo systemctl stop apt-daily.timer apt-daily-upgrade.timer 2>/dev/null || true
sudo flock --wait 60 /var/lib/dpkg/lock-frontend true 2>/dev/null || true

attempt=0
until timeout 180 uv run --python "${python_version}" playwright install-deps "${browser}"; do
  attempt=$((attempt + 1))
  if [ "${attempt}" -ge 3 ]; then
    echo "playwright install-deps ${browser} failed after ${attempt} attempts" >&2
    exit 1
  fi
  echo "playwright install-deps timed out or failed; retry ${attempt}/3" >&2
  sudo flock --wait 60 /var/lib/dpkg/lock-frontend true 2>/dev/null || true
done

uv run --python "${python_version}" playwright install "${browser}"
