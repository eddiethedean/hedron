"""Stable diagnostic codes for fastapi-workbench."""

from __future__ import annotations

FWB_0001 = "FWB-0001"  # invalid configuration / conflicting mount or origin
FWB_0002 = "FWB-0002"  # malformed or rejected rserver-url output
FWB_0003 = "FWB-0003"  # rserver-url binary missing or failed
FWB_0004 = "FWB-0004"  # bind / listen failure
FWB_0005 = "FWB-0005"  # application import or factory failure
FWB_0006 = "FWB-0006"  # adversarial or malformed request target rejected
FWB_0007 = "FWB-0007"  # platform / image cannot run (e.g. non-amd64)
FWB_0008 = "FWB-0008"  # deprecated compatibility alias used
FWB_0009 = "FWB-0009"  # unsupported Workbench launch topology
