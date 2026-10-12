# rfp-bid-brief

**A bid/no-bid triage pipeline for public-sector solicitations — plus a measured evaluation of the
decision models it can use.**

Given a solicitation and a bidder profile, it produces a one-page brief: the recommendation, the typed
fields behind it, and **verbatim citations** into the source document. Two claims hold it together:
every claim in a brief traces to a span of the source, and the decision layer's probabilities are
**calibrated and published at an operating point fixed in advance**.

It is a working pipeline, not a paper. `just check` runs everything offline.

```bash
just status         # inputs, stages, and what explicitly does not exist
just check          # fixture hashes, 109 tests, span reproducibility, extractions, baseline (no API key)
just brief fixtures/tahoe-transportation-district-it-consulting-2025.pdf     # render one brief
```

---

## Results

| what | result | the conditions that travel with it |
|---|---|---|
| Fixture set | **18 solicitations**, 6 bid / 12 no-bid | **deliberately enriched** — positives were searched for on purpose, so this is *not* the base rate a narrow firm meets. The real rate is lower. |
| Deterministic baseline | **18/18** calls · **17/18** primary reason class | runs on **hand-authored** extractions, so it measures the decision layer and the requirement vocabulary — not whether the pipeline reads documents. |
| Decision census | **248/252** answered | 14 served decision models × 18 fixtures, one frozen question, τ = 0.50 pre-registered, **$0.0159** per run |
| Models perfect at τ | **7 of 14** | every one gets all eighteen labels right |
| Calibration spread | **Brier 0.0000 – 0.0725** | accuracy is nearly identical across models; **calibration is not** — that is the project's thesis, as data |
| Agreement | 15 fixtures unanimous, **3 split** | the census marks the calls that are genuinely close instead of averaging them |
| Model path, end to end | **not measured** | the pipeline's accuracy *with a model reading the documents* has no number yet. Stated here rather than implied to be coming. |

### The one result worth reading

`energy-trust-of-oregon-crm-migration-to-d365` split **7 bid / 7 no-bid** across fourteen decision
models. The cause was visible in the profile: it named SAP/Oracle/Workday in its exclusions and
mentioned Dynamics 365 only inside a rule-of-thumb *escape clause* — so the models could not see a
phrase the deterministic layer was citing.

After the profile gained that class and the firm's experience record, the same question put to the same
models split **4 bid / 10 no-bid**. The instrument stopped hiding a phrase from the judges; the profile
was not edited to resolve the question. `results/calibration.json` and `adr/0011`.

---

## How it works

```
solicitation.pdf ─▶ parse ─▶ extract ─▶ decide ─▶ brief ─▶ one page per solicitation
                     │         │          │
                     │         │          └─ deterministic bindings against a frozen profile
                     │         └─ typed fields, every value carrying the span it came from
                     └─ deterministic span index: 8,497 spans over 444 pages, byte-reproducible
```

**The citation contract.** Every extracted value carries the id of the span it came from, and a quote
must exist **verbatim** in its fixture — whitespace-insensitive, word-boundary-aligned, page-level.
A quote that does not resolve **fails the build** rather than reaching a reader, which makes a
fabricated citation structurally impossible instead of reviewed for. [`adr/0001`](adr/0001-span-id-citations.md), [`adr/0004`](adr/0004-citations-locate-inside-spans.md), [`adr/0005`](adr/0005-citations-verify-at-page-level.md)

**The freeze order.** The profile is hashed, the operating point is pre-registered, and the labels are
committed **before any model sees a fixture** — in that order. Recording a threshold after seeing
results is not calibration, it is a fitted number. [`adr/0002`](adr/0002-required-bidder-profile.md), [`adr/0003`](adr/0003-pre-register-the-operating-point.md)

**The decision layer is a census, not a choice.** Every decision model the provider serves is asked the
same frozen question, at the same τ, for about a cent and a half — so selection bias has no defence to
make. Aliases and free tiers are excluded by rule, and every exclusion is recorded.
[`adr/0009`](adr/0009-the-decision-layer-is-a-census.md)

**A probability is never invented.** The deterministic layer emits a verdict and no number; the numbers
come from a census that was actually run. Where repeats disagree, the published figure is a **range**.
[`adr/0010`](adr/0010-repeat-the-census.md)

**Briefs carry the disagreement.** Each brief renders the probability channel with its resolved build
and serving host, a comparator, the pre-registered τ, what the census as a whole did, and whether the
rules layer agrees — and says plainly when it does not. A model that declined to answer is named rather
than absent.

---

## Repository map

| path | what it is |
|---|---|
| `bidder-profile.json` | The narrow bidder profile every recommendation is made against. Frozen and hashed before labelling. |
| `fixtures/` | 18 public solicitations, with provenance, notice and a hash manifest. `labels.json` is the held-out ground truth — 6 bid, 12 no-bid, each with its reason, evidence and counterargument. |
| `src/rfpbrief/` | `spans` (the index and the citation rule), `extract`, `decide`, `brief`, `evaluate`, `model_extractor`, `variance`, `decision_model`, `calibrate`. |
| `results/spans/` | One span index per fixture, regenerable byte-for-byte. |
| `results/briefs/` | The rendered one-pagers, committed as the artifact they are. |
| `results/decisions.json` · `results/census/` | The decision census. Every run archived content-addressed by state **and** answers, so a re-run cannot silently replace a measurement. |
| `results/calibration.json` | Per-model accuracy, Brier, reliability, and where the census splits. |
| `results/census-repeats/` | Four runs of one frozen state. **Historical (profile v1)**; the finding stands, the numbers describe a state no model will see again. |
| `adr/` | 15 decision records — including the ones that record being wrong. |
| `docs/NEXT.md` | State at closure: what is unfinished, and what a future session should not assume. |

```bash
just parse fixtures/<name>.pdf     # build one span index
just briefs                        # render every brief
just baseline                      # deterministic decision layer vs the committed labels
just provider-check                # is the intended decision model callable? decided by calling it
just census                        # ~$0.02, two minutes; archives itself
just calibration                   # per-model calibration at the pre-registered tau
```

---

## Honest limits

- **18 fixtures, 6 positives (33%).** Enough for a calibration curve to have shape, not enough for it to be
  conclusive. Fourteen models is 252 decisions and still **eighteen independent label comparisons per
  model** — the sample does not grow with the number of models.
- **The census is not exactly reproducible.** One decision in 616 changed sides across four repeats, so
  counts carry ranges (`adr/0010`). The stability measurement itself was made under profile v1 and has
  not been repeated since.
- **The extraction path is not measured end to end.** The baseline uses hand-authored extractions; the
  model-backed extractor has been run over an earlier, smaller fixture set with an earlier profile, and
  those results are historical.
- **The set is enriched, by design and on the record.** Each label carries its own counterargument.

## What this is not

Not a bid decision and not advice: it makes no leaderboard or benchmark claim about any model, and it
claims no relationship with any issuing organisation. It is also **not an agent application** — no
MCP surface, no orchestration framework, no deployed site, because this product is a document and those
artifacts would demonstrate nothing about it ([`adr/0015`](adr/0015-this-is-an-evaluation-not-an-agent-application.md)).

## Fixtures

Eighteen public solicitations from eighteen independent issuers — municipal, county, community colleges,
a university system, school districts, state agencies, a state court system, and state-chartered
non-profits. All are public records retrieved from the issuers' own published copies, all with
extractable text and no OCR anywhere.

They are third-party documents reproduced unmodified. Read [`fixtures/NOTICE.md`](fixtures/NOTICE.md)
before redistributing and [`fixtures/PROVENANCE.md`](fixtures/PROVENANCE.md) for the source of each.

## License

Apache-2.0 — see [`LICENSE`](LICENSE). The fixtures are **not** covered by it; they remain the property
of their issuers.
