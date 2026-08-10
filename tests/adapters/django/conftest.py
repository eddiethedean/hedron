"""Shared Django settings for adapter tests (configure once)."""

from __future__ import annotations

import pytest
from django.test import Client


@pytest.fixture
def django_client() -> Client:
    return Client()


@pytest.fixture
def django_csrf_client() -> Client:
    return Client(enforce_csrf_checks=True)
