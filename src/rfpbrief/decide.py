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
# Unreachable outranks unsuitable: if the firm is ineligible before capability is assessed, no other
# reason is the interesting one. That is why not_qualified sorts first (adr/0013).
PRIORITY = ("not_qualified", "geography", "product_not_services", "functional_stack_not_held",
            "operations_not_projects")


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


BINDINGS: tuple[Binding, ...] = (
    # A gate is not a capability question: the firm is ineligible before anyone asks whether the work
    # suits it. Four bindings rather than one, for the same reason functional_stacks has three -- the
    # profile excludes these under four differently worded phrases, and a reason should quote the
    # phrase it actually enforces. The extraction reports which shape of gate is present (adr/0012).
    Binding(
        requirement="eligibility_gates",
        test=lambda v: _any_stack(v, "comparable_implementations"),
        profile_exclusion="a minimum number of prior comparable implementations the firm does not have",
        reason_class="not_qualified",
        summary="the issuer requires more prior comparable implementations than the firm can show, "
                "which is a qualification rather than a score — the firm is ineligible before "
                "capability is assessed",
    ),
    Binding(
        requirement="eligibility_gates",
        test=lambda v: _any_stack(v, "contract_vehicle"),
        profile_exclusion="holding a pre-awarded contract vehicle, cooperative contract or vendor partnership tier the firm lacks",
        reason_class="not_qualified",
        summary="the procurement is open only to holders of a contract vehicle the firm does not have",
    ),
    Binding(
        requirement="eligibility_gates",
        test=lambda v: _any_stack(v, "certification"),
        profile_exclusion="a certification, licence, reseller authorisation or tier status the firm does not hold",
        reason_class="not_qualified",
        summary="a credential the firm does not hold is a condition of eligibility",
    ),
    Binding(
        requirement="eligibility_gates",
        test=lambda v: _any_stack(v, "clearance"),
        profile_exclusion="a security clearance or federal clearance sponsorship",
        reason_class="not_qualified",
        summary="the work requires a clearance or sponsorship the firm does not have",
    ),
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
        requirement="delivery_model",
        test=lambda v: v == "continuous_operations",
        profile_exclusion="24×7 monitoring",
        reason_class="operations_not_projects",
        summary="the work is continuous operations rather than a project with an end",
    ),
    # Functional stacks are three bindings, not one, because the profile excludes them under three
    # different phrases. What triggers them is *functional configuration* -- deciding how a vendor
    # product is set up -- never administration of it and never platform engineering underneath it.
    # That distinction is the extraction's job to make, and it is what separates Energy Trust
    # (configuring D365: no-bid) from CAPK (migrating onto it: bid).
    Binding(
        requirement="functional_stacks",
        test=lambda v: _any_stack(v, "dynamics"),
        profile_exclusion="vendor-specific functional stack the firm does not hold",
        reason_class="functional_stack_not_held",
        summary="the engagement is functional configuration of Microsoft Dynamics, a stack the "
                "profile does not hold — the profile's own escape clause, platform engineering "
                "underneath it, does not apply",
    ),
    Binding(
        requirement="functional_stacks",
        test=lambda v: _any_stack(v, "sap", "oracle", "workday"),
        profile_exclusion="functional SAP / Oracle / Workday configuration",
        reason_class="functional_stack_not_held",
        summary="the engagement is functional configuration of SAP, Oracle or Workday",
    ),
    Binding(
        requirement="functional_stacks",
        test=lambda v: _any_stack(v, "erp", "student information"),
        profile_exclusion="ERP and student information system functional implementation",
        reason_class="functional_stack_not_held",
        summary="the engagement is a functional implementation of ERP or student systems",
    ),
)


def _any_stack(stacks: Any, *needles: str) -> bool:
    if not stacks:
        return False
    lowered = [str(s).lower() for s in stacks]
    return any(n in s for s in lowered for n in needles)


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
    """Every place the profile says what this firm does not do. The rules of thumb count.

    They are not commentary: rule 4 both excludes a family of work and states the escape from it
    ("no-bid unless the work is platform engineering underneath it"), and a binding that could not
    cite that rule would have to invent a phrase of its own.
    """
    return (
        list(profile.get("excluded_delivery_models", []))
        + list(profile.get("excluded_capability_areas", []))
        # The gate list belongs here for the same reason the others do: it is the profile saying what
        # this firm does not have. It was omitted while no binding could cite it, which is the kind of
        # gap that reads as intentional later (adr/0012).
        + list(profile.get("excluded_eligibility_gates", []))
        + list(profile.get("decision_rules_of_thumb", []))
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
        "deterministic verdict: this layer emits a verdict, not a probability — the probability "
        "channel, the pre-registered operating point and the census are under Decision below",
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
