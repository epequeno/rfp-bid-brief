"""The decision: does this profile bid on this solicitation, and why.

Deterministic on purpose. Two committed inputs go in — the frozen bidder profile and a validated
extraction — and a recommendation with reasons comes out. No model is consulted about capability
(ADR 0002), so the same inputs always produce the same call, and a reader can disagree with a
specific reason rather than with a vibe.

## What this module deliberately does not do

It does not emit a probability. The calibrated probability channel is the typed decision layer's
(Jev), and it is not wired yet, so `Decision.probability` is `None` and the brief says so. Emitting
a plausible-looking number here — 0.9, 0.72 — would quietly break the one claim the project is
built on: that the published operating point means something. A deterministic verdict plus cited
reasons is honest and useful on its own; a fabricated probability is neither.

## The bindings

Each requirement kind is bound to a phrase that must appear in the **frozen profile's** exclusion
lists. The profile stays the source of truth — this module only says which requirement corresponds
to which exclusion — and a test fails if any binding's phrase is absent from the profile, so the two
cannot drift apart silently.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from .extract import Citation, Extraction, Fact

BID = "bid"
NO_BID = "no_bid"

# Primary reason class wins by hard-disqualifier-first: if you cannot be there, the business-model
# argument never gets reached.
PRIORITY = ("geography", "product_not_services", "functional_stack_not_held", "operations_not_projects")


@dataclass(frozen=True)
class Binding:
    requirement: str
    test: Callable[[Any], bool]
    profile_exclusion: str
    reason_class: str
    summary: str

    def triggered(self, fact: Fact | None) -> bool:
        return fact is not None and self.test(fact.value)


def _is_true(v: Any) -> bool:
    return v is True


def _non_empty(v: Any) -> bool:
    return bool(v)


BINDINGS: tuple[Binding, ...] = (
    Binding(
        requirement="requires_recurring_onsite",
        test=_is_true,
        profile_exclusion="regular on-site staffing",
        reason_class="geography",
        summary="winning requires a standing on-site presence the firm cannot commit to",
    ),
    Binding(
        requirement="requires_emergency_onsite_response",
        test=_is_true,
        profile_exclusion="emergency on-site response commitment",
        reason_class="geography",
        summary="winning requires an emergency on-site response, which is a geographic commitment",
    ),
    Binding(
        requirement="requires_product_supply",
        test=_is_true,
        profile_exclusion="supplying a hosted product",
        reason_class="product_not_services",
        summary="the issuer is buying a product and the services are incidental",
    ),
    Binding(
        requirement="functional_stacks",
        test=_non_empty,
        profile_exclusion="functional SAP / Oracle / Workday configuration",
        reason_class="functional_stack_not_held",
        summary="winning requires vendor-specific functional expertise the profile excludes",
    ),
    Binding(
        requirement="delivery_model",
        test=lambda v: v == "continuous_operations",
        profile_exclusion="24×7 monitoring",
        reason_class="operations_not_projects",
        summary="the work is continuous operations rather than a project with an end",
    ),
)


@dataclass(frozen=True)
class Reason:
    requirement: str
    value: Any
    summary: str
    reason_class: str
    profile_exclusion: str
    citations: tuple[Citation, ...]


@dataclass(frozen=True)
class Consideration:
    """A requirement the profile does *not* exclude. Not a reason to decline, and not nothing."""

    requirement: str
    value: Any
    citations: tuple[Citation, ...]


@dataclass
class Decision:
    recommendation: str
    probability: float | None
    primary_reason_class: str
    reasons: list[Reason]
    considered: list[Consideration]
    notes: list[str]

    @property
    def is_bid(self) -> bool:
        return self.recommendation == BID


def profile_exclusions(profile: dict) -> list[str]:
    return list(profile.get("excluded_delivery_models", [])) + list(
        profile.get("excluded_capability_areas", [])
    )


def profile_carries(profile: dict, phrase: str) -> bool:
    return any(phrase in entry for entry in profile_exclusions(profile))


def decide(profile: dict, extraction: Extraction) -> Decision:
    """Apply the bindings to an extraction. Deterministic; no probability is invented.

    A requirement only becomes a *reason to decline* when the profile actually excludes it. A
    triggered requirement the profile does not exclude is recorded as a consideration instead —
    otherwise the profile would be decorative, and every solicitation naming an on-site day would
    be a no-bid regardless of who was bidding. The profile, and only the profile, decides
    capability (ADR 0002).
    """
    reasons: list[Reason] = []
    considered: list[Consideration] = []
    for binding in BINDINGS:
        fact = extraction.requirements.get(binding.requirement)
        if not binding.triggered(fact):
            continue
        if not profile_carries(profile, binding.profile_exclusion):
            considered.append(
                Consideration(binding.requirement, fact.value, fact.citations)
            )
            continue
        reasons.append(
            Reason(
                requirement=binding.requirement,
                value=fact.value,
                summary=binding.summary,
                reason_class=binding.reason_class,
                profile_exclusion=binding.profile_exclusion,
                citations=fact.citations,
            )
        )

    triggered_classes = {r.reason_class for r in reasons}
    primary = next((c for c in PRIORITY if c in triggered_classes), "in_scope")
    recommendation = NO_BID if reasons else BID

    notes = [
        "deterministic verdict: no calibrated probability is available yet, so the pre-registered "
        "operating point (tau = 0.50) does not apply to this brief",
        f"profile {profile.get('profile_id')} — {len(reasons)} exclusion(s) matched, "
        f"{len(considered)} requirement(s) considered and not excluded",
    ]
    if recommendation == BID:
        notes.append("no exclusion in the profile is triggered by this solicitation")

    return Decision(
        recommendation=recommendation,
        probability=None,
        primary_reason_class=primary,
        reasons=reasons,
        considered=considered,
        notes=notes,
    )
