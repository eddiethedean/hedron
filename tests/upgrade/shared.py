"""Shared metadata fixture for the Hedron 0.67-to-1.0 migration bridge.

The release packet references this file from warning records.  It intentionally
contains no application import or executable setup; per-version fixture tests
own execution in their isolated environments.
"""

FIXTURE_SCHEMA = "hedron.upgrade-fixture/1"
BASELINE = "v0.67.0"
TARGET = "v1.0.0"
