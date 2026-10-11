"""Calibration and agreement across the decision census.

Two things are computed here, and they answer different questions:

* **Per model** — how well its probabilities match the eleven committed labels at the pre-registered
  τ = 0.50. The confusion matrix and the Brier score are the headline; the reliability buckets say
  whether a probability of 0.7 means 70% of the time. A model's *best* threshold is also computed and
  is **post-hoc by construction** — it is a diagnostic about the probabilities, never the headline,
  because choosing a threshold after seeing the labels is how a fitted number gets published.
* **Across models** — where the census disagrees. That is the most informative thing the census
  produces and it needs no extra labels: a fixture where independent decision models split is a
  fixture whose call is genuinely close, and saying so is more useful than a single probability
  presented as fact.

Both are reported at n = 11 with four positives, and every table says so. Adding models does not add
statistical power: the eleven labels are compared eleven times per model.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import json


def _decide(p: float, tau: float) -> str:
    return "bid" if p >= tau else "no_bid"


def _brier(pairs: list[tuple[float, int]]) -> float:
    return sum((p - y) ** 2 for p, y in pairs) / len(pairs)


def _reliability(pairs: list[tuple[float, int]], buckets: int = 5) -> list[dict]:
    out = []
    for i in range(buckets):
        lo, hi = i / buckets, (i + 1) / buckets
        inside = [(p, y) for p, y in pairs if (p >= lo and (p < hi or (i == buckets - 1 and p <= hi)))]
        if not inside:
            continue
        out.append({
            "bucket": f"{lo:.1f}-{hi:.1f}",
            "n": len(inside),
            "mean_p": round(sum(p for p, _ in inside) / len(inside), 4),
            "observed": round(sum(y for _, y in inside) / len(inside), 4),
        })
    return out


def _best_threshold(pairs: list[tuple[float, int]], tau: float) -> tuple[float, int]:
    """Post-hoc: the threshold that would have maximised correct calls. Diagnostic only."""
    candidates = sorted({0.0, 1.0, *[p for p, _ in pairs]})
    best_t, best_n = tau, sum(_decide(p, tau) == ("bid" if y else "no_bid") for p, y in pairs)
    for t in candidates:
        n = sum(_decide(p, t) == ("bid" if y else "no_bid") for p, y in pairs)
        if n > best_n:
            best_t, best_n = t, n
    return round(best_t, 4), best_n


@dataclass
class ModelScore:
    model: str
    provider: str | None
    resolved: str | None
    n: int
    pairs: list[tuple[str, float, int]] = field(default_factory=list)  # fixture, p, y
    refused: int = 0
    cost: float = 0.0

    @property
    def probabilities(self) -> dict[str, float]:
        return {f: p for f, p, _ in self.pairs}

    def decided(self, tau: float) -> dict[str, str]:
        return {f: _decide(p, tau) for f, p, _ in self.pairs}

    def confusion(self, tau: float) -> dict[str, dict[str, int]]:
        out: dict[str, dict[str, int]] = {}
        for f, p, y in self.pairs:
            truth = "bid" if y else "no_bid"
            out.setdefault(truth, {}).setdefault(_decide(p, tau), 0)
            out[truth][_decide(p, tau)] += 1
        return out

    def correct(self, tau: float) -> int:
        return sum(_decide(p, tau) == ("bid" if y else "no_bid") for _, p, y in self.pairs)

    @property
    def brier(self) -> float:
        return round(_brier([(p, y) for _, p, y in self.pairs]), 4)

    def reliability(self) -> list[dict]:
        return _reliability([(p, y) for _, p, y in self.pairs])

    def post_hoc_threshold(self, tau: float) -> tuple[float, int]:
        return _best_threshold([(p, y) for _, p, y in self.pairs], tau)


def score(labels: dict, decisions: dict) -> list[ModelScore]:
    """One ModelScore per model that answered at least one fixture."""
    truth = {entry["fixture"]: 1 if entry["label"] == "bid" else 0 for entry in labels["labels"]}
    by_model: dict[str, ModelScore] = {}
    for row in decisions["answers"]:
        key = row["model_canonical"]
        s = by_model.get(key)
        if s is None:
            s = ModelScore(model=key, provider=row.get("provider"), resolved=row.get("resolved_model"),
                           n=0)
            by_model[key] = s
        if row.get("noul") is None or row.get("fixture") not in truth:
            s.refused += 1
            continue
        s.pairs.append((row["fixture"], float(row["noul"]), truth[row["fixture"]]))
        s.n = len(s.pairs)
        s.cost += float(row.get("cost") or 0)
        s.provider = s.provider or row.get("provider")
    return sorted(by_model.values(), key=lambda s: (-s.correct(decisions["operating_point_tau"]), s.model))


def disagreement(decisions: dict) -> dict:
    """Where the census splits. The artifact that needs no extra labels."""
    tau = decisions["operating_point_tau"]
    by_fixture: dict[str, dict[str, list[float]]] = {}
    providers: dict[str, str | None] = {}
    for row in decisions["answers"]:
        if row.get("noul") is None:
            continue
        by_fixture.setdefault(row["fixture"], {})
        by_fixture[row["fixture"]].setdefault("pro", []).append(float(row["noul"]))
        providers[row["model_canonical"]] = row.get("provider")
    out = {"tau": tau, "fixtures": {}}
    for fixture, data in sorted(by_fixture.items()):
        pro = data["pro"]
        bid = sum(1 for p in pro if p >= tau)
        out["fixtures"][fixture] = {
            "models": len(pro),
            "bid": bid,
            "no_bid": len(pro) - bid,
            "min": round(min(pro), 4),
            "median": round(sorted(pro)[len(pro) // 2], 4),
            "max": round(max(pro), 4),
            "split": 0 < bid < len(pro),
        }
    out["unanimous"] = sum(1 for f in out["fixtures"].values() if not f["split"])
    out["split"] = sum(1 for f in out["fixtures"].values() if f["split"])
    return out


def render(scores: list[ModelScore], disagreement_data: dict, tau: float) -> str:
    lines = [
        f"operating point: tau = {tau} (pre-registered) · n = {scores[0].n} fixtures, "
        f"{sum(y for _, _, y in scores[0].pairs)} of them bid",
        "",
        "| model | provider | correct @ tau | Brier | post-hoc tau* | correct @ tau* |",
        "|---|---|---|---|---|---|",
    ]
    for s in scores:
        t, n = s.post_hoc_threshold(tau)
        lines.append(f"| {s.model[:44]} | {s.provider or '—'} | **{s.correct(tau)}/{s.n}** | {s.brier} "
                     f"| {t} | {n}/{s.n} |")
    lines += ["", "*tau\\* is post-hoc: computed after seeing the labels. Diagnostic of the "
                  "probabilities, never the headline.*", ""]
    worst = [s for s in scores if s.refused]
    if worst:
        lines += [f"did not answer: {', '.join(f'{s.model} ({s.refused})' for s in worst)}", ""]
    lines += [
        f"agreement across the census: **{disagreement_data['unanimous']} fixtures unanimous**, "
        f"{disagreement_data['split']} split",
        "",
        "| fixture | models | bid | no_bid | min p | median p | max p |",
        "|---|---|---|---|---|---|---|",
    ]
    for fixture, d in disagreement_data["fixtures"].items():
        mark = " **← split**" if d["split"] else ""
        lines.append(f"| {fixture[:52]} | {d['models']} | {d['bid']} | {d['no_bid']} | {d['min']} "
                     f"| {d['median']} | {d['max']} |{mark}")
    return "\n".join(lines)


def to_json(scores: list[ModelScore], disagreement_data: dict, tau: float) -> dict:
    return {
        "schema": "calibration/1",
        "operating_point_tau": tau,
        "sample": {
            "fixtures": scores[0].n if scores else 0,
            "positives": sum(y for _, _, y in scores[0].pairs) if scores else 0,
            "note": ("The sample size does not grow with the number of models: each model's "
                     "probabilities are compared against the same eleven labels. Several thin "
                     "calibration curves are still thin."),
        },
        "models": [
            {
                "model": s.model,
                "provider": s.provider,
                "resolved_model": s.resolved,
                "answered": s.n,
                "refused": s.refused,
                "correct_at_tau": s.correct(tau),
                "confusion_at_tau": s.confusion(tau),
                "brier": s.brier,
                "reliability": s.reliability(),
                "post_hoc_threshold": s.post_hoc_threshold(tau)[0],
                "correct_at_post_hoc": s.post_hoc_threshold(tau)[1],
                "cost_usd": round(s.cost, 8),
                "probabilities": s.probabilities,
            }
            for s in scores
        ],
        "disagreement": disagreement_data,
    }


def load(path) -> dict:
    return json.loads(open(path).read())
