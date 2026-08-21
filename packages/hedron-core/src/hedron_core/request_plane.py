"""Bind request-local SecurityContext + RequestBudget for host adapters."""

from __future__ import annotations

import contextvars
from dataclasses import dataclass

from hedron_core.request_budget import (
    RequestBudget,
    RequestBudgetLimits,
    reset_request_budget,
    set_request_budget,
)
from hedron_core.security_context import (
    SecurityContext,
    reset_security_context,
    set_security_context,
)
from hedron_core.security_policy import SecurityPolicy


@dataclass(slots=True)
class RequestSecurityBinding:
    """Tokens and ledger installed for the current request."""

    context_token: contextvars.Token[SecurityContext | None]
    budget_token: contextvars.Token[RequestBudget | None]
    budget: RequestBudget | None


def bind_request_security(
    *,
    policy: SecurityPolicy,
    application_id: str,
    subject_id: str = "",
    tenant_id: str = "",
    scopes: frozenset[str] | None = None,
    auth_level: int = 0,
    correlation_id: str = "",
) -> RequestSecurityBinding:
    """Install ContextVar security plane early in the host request lifecycle."""
    ctx = SecurityContext(
        application_id=application_id,
        subject_id=subject_id,
        tenant_id=tenant_id,
        scopes=scopes or frozenset(),
        auth_level=auth_level,
        profile_name=policy.profile.value
        if hasattr(policy.profile, "value")
        else str(policy.profile),
        policy_version=policy.version,
        correlation_id=correlation_id,
    )
    limits = policy.request_budget_limits or RequestBudgetLimits()
    budget = RequestBudget(limits=limits)
    return RequestSecurityBinding(
        context_token=set_security_context(ctx),
        budget_token=set_request_budget(budget),
        budget=budget,
    )


def unbind_request_security(binding: RequestSecurityBinding) -> None:
    """Close the ledger and reset ContextVars (always call from ``finally``)."""
    if binding.budget is not None:
        binding.budget.close()
    reset_request_budget(binding.budget_token)
    reset_security_context(binding.context_token)
