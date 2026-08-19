#!/usr/bin/env bash
# Install one Playwright browser plus OS deps.
# GitHub ubuntu-latest apt often stalls on azure.archive.ubuntu.com, and a killed
# apt-get leaves /var/lib/apt/lists/lock held. Prefer archive.ubuntu.com, wait for
# locks, and retry a timed install-deps.
set -euo pipefail

browser="${1:?browser name required}"
python_version="${2:-3.12}"

export DEBIAN_FRONTEND=noninteractive

rewrite_apt_mirrors() {
  local path
  for path in \
    /etc/apt/apt-mirrors.txt \
    /etc/apt/sources.list \
    /etc/apt/sources.list.d/ubuntu.sources
  do
    if [ -f "${path}" ]; then
      sudo sed -i \
        's|azure\.archive\.ubuntu\.com|archive.ubuntu.com|g' \
        "${path}" || true
    fi
  done
}

stop_apt_lockers() {
  sudo systemctl stop apt-daily.service apt-daily-upgrade.service unattended-upgrades.service 2>/dev/null || true
  sudo systemctl stop apt-daily.timer apt-daily-upgrade.timer 2>/dev/null || true
  sudo killall -q apt-get apt || true
  sudo flock --wait 90 /var/lib/dpkg/lock-frontend true 2>/dev/null || true
  sudo flock --wait 90 /var/lib/apt/lists/lock true 2>/dev/null || true
}

rewrite_apt_mirrors
stop_apt_lockers

attempt=0
until timeout --kill-after=30 480 uv run --python "${python_version}" playwright install-deps "${browser}"; do
  attempt=$((attempt + 1))
  if [ "${attempt}" -ge 2 ]; then
    echo "playwright install-deps ${browser} failed after ${attempt} attempts" >&2
    exit 1
  fi
  echo "playwright install-deps timed out or failed; retry ${attempt}/2" >&2
  stop_apt_lockers
done

uv run --python "${python_version}" playwright install "${browser}"
