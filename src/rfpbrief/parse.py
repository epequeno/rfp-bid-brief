"""Command-line surface for the span index.

    uv run rfpbrief build  fixtures/<fixture>.pdf          # write results/spans/<fixture>.json
    uv run rfpbrief find   fixtures/<fixture>.pdf "quote"  # which span, or nothing
    uv run rfpbrief verify results/spans/<fixture>.json    # is the index still reproducible?
    uv run rfpbrief stats  fixtures/<fixture>.pdf

`build` refuses a fixture that is not in the provenance manifest, and `verify` fails if the fixture,
the engine version or the page text has moved. Both refusals are the point: an index that silently
stops describing its document turns every citation against it into a confident guess.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from . import (brief, calibrate, decide, decision_model, evaluate, extract,
               model_extractor, providers, spans, variance)
from .spans import collapse_ws

REPO = Path(__file__).resolve().parents[2]
FIXTURES = REPO / "fixtures"
DEFAULT_OUT = REPO / "results" / "spans"
MANIFEST = FIXTURES / "PROVENANCE.md"

_MANIFEST_LINE = re.compile(r"^(?P<sha>[0-9a-f]{64})\s+(?P<name>\S+\.pdf)$")


def manifest_hashes() -> dict[str, str]:
    """The committed sha256 for each fixture, read from the manifest block in PROVENANCE.md."""
    if not MANIFEST.exists():
        return {}
    insec = fence = False
    out: dict[str, str] = {}
    for line in MANIFEST.read_text(encoding="utf-8").splitlines():
        if line.startswith("## Integrity manifest"):
            insec = True
            continue
        if insec and line.startswith("```"):
            fence = not fence
            continue
        if insec and fence:
            m = _MANIFEST_LINE.match(line.strip())
            if m:
                out[m.group("name")] = m.group("sha")
    return out


def cmd_build(args: argparse.Namespace) -> int:
    path = Path(args.fixture)
    doc = spans.build(path, fixture_name=path.name)
    known = manifest_hashes()
    if known and path.name not in known:
        print(f"refusing: {path.name} has no provenance row in fixtures/PROVENANCE.md", file=sys.stderr)
        return 2
    if known and known[path.name] != doc.fixture_sha256:
        print(
            f"refusing: {path.name} does not match its published hash\n"
            f"  manifest {known[path.name]}\n  fixture  {doc.fixture_sha256}",
            file=sys.stderr,
        )
        return 2
    out = Path(args.out) if args.out else DEFAULT_OUT / f"{path.stem}.json"
    spans.write_index(doc, out)
    print(
        f"{doc.fixture}: {len(doc.pages)} pages, {len(doc.spans)} spans, "
        f"{sum(len(p.text) for p in doc.pages)} chars, {doc.hyphen_breaks} hyphenated line breaks\n"
        f"  engine    {doc.engine_version}\n"
        f"  fixture   {doc.fixture_sha256[:16]}…\n"
        f"  index     {out.relative_to(REPO) if str(out).startswith(str(REPO)) else out}"
    )
    return 0


def cmd_find(args: argparse.Namespace) -> int:
    """Locate a quote. Exit 0 only when the answer is exactly one span.

    Ambiguity exits non-zero on purpose: a quote that appears on three pages is not a citation yet,
    and silently taking the first hit is how a brief ends up quoting the wrong section.
    """
    doc = spans.build(Path(args.fixture), fixture_name=Path(args.fixture).name)
    if args.exact:
        hits = doc.find(args.quote)
        if not hits:
            print("no span equals that quote exactly (try without --exact)", file=sys.stderr)
            return 1
        for s in hits:
            print(f"{s.id}\tpage {s.page}\t{s.quote}")
        return 0 if len(hits) == 1 else 1

    cites = doc.locate(args.quote, page=args.page)
    if not cites:
        print("not found: no span contains that quote under the verbatim rule "
              "(whitespace-only differences tolerated)", file=sys.stderr)
        return 1
    for c in cites:
        print(f"{c.id}\tpage {c.page}\t{c.quote}")
    if len(cites) > 1:
        pages = sorted({c.page for c in cites})
        print(f"ambiguous: {len(cites)} spans on page(s) {pages} contain that quote. "
              f"Re-run with --page to say which one you meant.", file=sys.stderr)
        return 1
    return 0


def cmd_verify(args: argparse.Namespace) -> int:
    index = spans.read_index(Path(args.index))
    fixture = FIXTURES / index["fixture"]
    if not fixture.exists():
        print(f"refusing: {fixture.name} is not in fixtures/", file=sys.stderr)
        return 2
    doc = spans.build(fixture, fixture_name=fixture.name)
    problems = spans.reproducibility_report(doc, index)
    if problems:
        print(f"{index['fixture']}: index is NOT reproducible", file=sys.stderr)
        for p in problems:
            print(f"  - {p}", file=sys.stderr)
        return 1
    print(f"{index['fixture']}: reproducible ({len(doc.spans)} spans, {len(doc.pages)} pages)")
    return 0


def cmd_extract(args: argparse.Namespace) -> int:
    """Validate the committed extraction for a fixture, or show it. The check is the point."""
    path = Path(args.fixture)
    doc = spans.build(path, fixture_name=path.name)
    ex = extract.for_fixture(doc, Path(args.extractions) if args.extractions else None)
    cites = ex.citations()
    if args.json:
        print(json.dumps({
            "fixture": ex.fixture,
            "produced_by": ex.produced_by,
            "facts": {k: {"value": v.value, "citations": [c.to_json() for c in v.citations]}
                      for k, v in ex.facts.items()},
            "requirements": {k: {"value": v.value, "citations": [c.to_json() for c in v.citations]}
                             for k, v in ex.requirements.items()},
        }, indent=1))
        return 0
    print(f"{ex.fixture}: {len(ex.facts)} facts, {len(ex.requirements)} requirements, "
          f"{len(cites)} citations — all verified against the span index")
    print(f"  produced by  {ex.produced_by}")
    for name, fact in {**ex.facts, **ex.requirements}.items():
        pages = ", ".join(f"p{c.page}" for c in fact.citations)
        print(f"  {name:<34} {str(fact.value)[:44]:<46} {pages}")
    return 0


def cmd_decide(args: argparse.Namespace) -> int:
    path = Path(args.fixture)
    doc = spans.build(path, fixture_name=path.name)
    ex = extract.for_fixture(doc, Path(args.extractions) if args.extractions else None)
    profile = json.loads((REPO / "bidder-profile.json").read_text(encoding="utf-8"))
    decision = decide.decide(profile, ex)
    if args.json:
        print(json.dumps({
            "recommendation": decision.recommendation,
            "probability": decision.probability,
            "primary_reason_class": decision.primary_reason_class,
            "reasons": [{"requirement": r.requirement, "reason_class": r.reason_class,
                         "profile_exclusion": r.profile_exclusion,
                         "citations": [c.to_json() for c in r.citations]} for r in decision.reasons],
            "notes": decision.notes,
        }, indent=1))
        return 0
    print(f"{doc.fixture}: {decision.recommendation.upper()} "
          f"(primary reason class: {decision.primary_reason_class})")
    for r in decision.reasons:
        print(f"  - {r.requirement}: {r.summary}")
        print(f"      profile excludes {r.profile_exclusion!r}")
        for c in r.citations:
            print(f"      {c.render()}")
    for n in decision.notes:
        print(f"  note: {n}")
    return 0


def cmd_brief(args: argparse.Namespace) -> int:
    path = Path(args.fixture)
    doc = spans.build(path, fixture_name=path.name)
    ex = extract.for_fixture(doc, Path(args.extractions) if args.extractions else None)
    profile = json.loads((REPO / "bidder-profile.json").read_text(encoding="utf-8"))
    decision = decide.decide(profile, ex)
    markdown = brief.render(decision, ex, doc)
    out = Path(args.out) if args.out else REPO / "results" / "briefs" / f"{path.stem}.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(markdown, encoding="utf-8")
    if not args.quiet:
        print(markdown)
    print(f"→ {_display(out)}", file=sys.stderr)
    return 0


def _display(path: Path) -> str:
    """A path relative to the repository when it is inside one, printed as given otherwise.

    `--out` may be relative to the caller's directory, which is not always the repository, and an
    exception about that is a bad way to end an otherwise successful run.
    """
    p = path if path.is_absolute() else (Path.cwd() / path)
    try:
        return str(p.relative_to(REPO))
    except ValueError:
        return str(p)


def _utc_now() -> str:
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def cmd_model_extract(args: argparse.Namespace) -> int:
    """Run the model-backed extractor on one fixture, with one bounded repair attempt (ADR 0006).

    A refused extraction does NOT land in the extraction directory. It used to, and that was a real
    flaw: the comparison then read refused values as though they were validated data. Refusals go to
    a `_refused/` subdirectory, where they are counted and never mistaken for an answer.
    """
    path = Path(args.fixture)
    doc = spans.build(path, fixture_name=path.name)
    outdir = Path(args.out_dir)
    outdir.mkdir(parents=True, exist_ok=True)
    started = _utc_now()
    run = model_extractor.extract(doc, model=args.model, retries=args.retries,
                                  caller=model_extractor.call_pi)
    finished = _utc_now()

    if run.accepted:
        if not args.no_write:
            out = outdir / f"{path.stem}.json"
            out.write_text(
                json.dumps(model_extractor.annotate(run, run.data, started, finished),
                           indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
        note = "repaired on attempt 2" if run.repaired else "first attempt"
        print(f"{doc.fixture}: validated — {note}")
        return 0

    refused = outdir / "_refused"
    refused.mkdir(parents=True, exist_ok=True)
    (refused / f"{path.stem}.json").write_text(
        json.dumps({
            "fixture": doc.fixture,
            "model": run.model,
            "attempts": run.attempts,
            "prompt_sha256": model_extractor.prompt_sha256(),
            "error": run.error,
            "refusals": run.refusals,
        }, indent=1) + "\n",
        encoding="utf-8",
    )
    print(f"{doc.fixture}: REFUSED after {run.attempts} attempt(s)", file=sys.stderr)
    last = run.refusals[-1]["problems"] if run.refusals else [run.error or "unknown"]
    for p in last:
        print(f"  - {p[:200]}", file=sys.stderr)
    return 1


def cmd_baseline(args: argparse.Namespace) -> int:
    """Run the decision layer against every committed label. Writes results/baseline.json."""
    labels = json.loads((REPO / "fixtures" / "labels.json").read_text(encoding="utf-8"))
    profile = json.loads((REPO / "bidder-profile.json").read_text(encoding="utf-8"))
    exdir = Path(args.extractions) if args.extractions else None
    cache: dict[str, spans.Document | None] = {}
    unusable: dict[str, list[str]] = {}
    seen_refused: set[str] = set()

    def extraction_for(fixture: str):
        if fixture not in cache:
            path = FIXTURES / fixture
            cache[fixture] = spans.build(path, fixture_name=fixture) if path.exists() else None
        doc = cache[fixture]
        if doc is None:
            return None
        try:
            return extract.for_fixture(doc, exdir)
        except FileNotFoundError:
            # A refusal is filed in _refused/, and it is a different thing from "not run yet".
            # Reporting it as absent would erase the citation-integrity number from the baseline.
            refused = (exdir or extract.EXTRACTIONS) / "_refused" / f"{Path(fixture).stem}.json"
            if refused.exists():
                recorded = json.loads(refused.read_text(encoding="utf-8"))
                problems = [p for r in recorded.get("refusals", []) for p in r.get("problems", [])]
                unusable[fixture] = problems or [recorded.get("error") or "refused"]
                seen_refused.add(fixture)
            return None
        except extract.ExtractionError as exc:
            # A refused extraction is a result, not a crash: it is the citation-integrity rate.
            unusable[fixture] = exc.problems
            seen_refused.add(fixture)
            return None

    baseline = evaluate.run(labels, extraction_for, lambda ex: decide.decide(profile, ex))
    baseline.unusable = [{"fixture": k, "problems": v} for k, v in sorted(unusable.items())]
    baseline.missing_extraction = [f for f in baseline.missing_extraction if f not in seen_refused]
    out = Path(args.out) if args.out else REPO / "results" / "baseline.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(baseline.to_json(), indent=1) + "\n", encoding="utf-8")
    if not args.quiet:
        print(evaluate.render(baseline))
    print(f"→ {_display(out)}", file=sys.stderr)
    return 0 if baseline.n and baseline.label_agree == baseline.n else 1


def cmd_payload(args: argparse.Namespace) -> int:
    """Print one fixture's spans, in the exact form the extractor prompt expects.

    Spans only: no label, no profile, no hand-authored extraction. The extractor sees the document
    and nothing about what the answer is supposed to be.
    """
    path = Path(args.fixture)
    doc = spans.build(path, fixture_name=path.name)
    print(f"fixture: {doc.fixture}")
    print(f"pages: {len(doc.pages)}  spans: {len(doc.spans)}")
    print("")
    for s in doc.spans:
        print(f"[{s.id}] (page {s.page}) {collapse_ws(s.text)}")
    return 0


def cmd_compare(args: argparse.Namespace) -> int:
    """Field-level comparison of two extraction sets. Scores a model against the stand-in."""
    rows = evaluate.compare_extractions(Path(args.a), Path(args.b))
    if not rows:
        print(f"no fixture present in both {args.a} and {args.b}")
        return 1
    for r in rows:
        verdict = ("requirements agree" if r.requirements_agree
                   else f"{r.req_differing}/{r.req_total} requirements differ")
        print(f"{r.fixture[:56]:<58} {verdict}")
        for d in r.details:
            print(f"    {d}")
    agree = sum(r.requirements_agree for r in rows)
    total = sum(r.req_total for r in rows)
    diffs = sum(r.req_differing for r in rows)
    print(f"\nrequirement agreement: {total - diffs}/{total} values across {agree}/{len(rows)} fixtures")
    return 0


def cmd_variance(args: argparse.Namespace) -> int:
    """Outcome stability across repeated runs. Writes results/variance.json."""
    dirs = []
    for pattern in args.directories:
        from glob import glob as _glob
        matched = sorted(_glob(pattern)) or [pattern]
        dirs.extend(Path(m) for m in matched)
    if not dirs:
        print("no run directories given", file=sys.stderr)
        return 2
    runs = [variance.read_run(d) for d in dirs]
    v = variance.summarise(runs)
    out = Path(args.out) if args.out else REPO / "results" / "variance.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(v.to_json(), indent=1) + "\n", encoding="utf-8")
    if not args.quiet:
        print(variance.render(v))
    print(f"→ {_display(out)}", file=sys.stderr)
    lo, hi = v.clean_range
    return 0 if lo == hi else 1 if args.strict else 0


def cmd_provider(args: argparse.Namespace) -> int:
    """Probe whether the intended decision model is callable yet. Exit 0 when it is."""
    p = providers.probe(args.model)
    print(providers.render(p))
    return 0 if p.callable_now else 1


def _labels_and_profile() -> tuple[dict, dict]:
    labels = json.loads((REPO / "fixtures" / "labels.json").read_text(encoding="utf-8"))
    profile = json.loads((REPO / "bidder-profile.json").read_text(encoding="utf-8"))
    return labels, profile


def cmd_census(args: argparse.Namespace) -> int:
    """Ask every eligible decision model about every fixture, on one frozen request."""
    labels, profile = _labels_and_profile()
    tau = float(labels["operating_point_tau"])
    candidates, taken = decision_model.census()
    eligible = [c for c in candidates if c.eligible]
    print(f"census taken {taken}: {len(candidates)} entries, {len(eligible)} eligible")
    for c in candidates:
        if not c.eligible:
            print(f"  excluded  {c.canonical:<46} {c.excluded_because}")
    if args.dry_run:
        print(f"\nwould ask {len(eligible)} models about {len(labels['labels'])} fixtures "
              f"= {len(eligible) * len(labels['labels'])} decisions")
        return 0

    fixtures = []
    for entry in labels["labels"]:
        path = FIXTURES / entry["fixture"]
        doc = spans.build(path, fixture_name=entry["fixture"])
        fixtures.append((doc, extract.for_fixture(doc)))
    print(f"\nasking {len(eligible)} models × {len(fixtures)} fixtures...")
    result = decision_model.run(fixtures, profile, candidates, tau, taken)
    payload = result.to_json()
    out = Path(args.out) if args.out else REPO / "results" / "decisions.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=1) + "\n", encoding="utf-8")
    # Archive under a content-addressed name: a re-run with a changed state must not silently
    # replace the previous measurement, which is exactly the mistake this repository criticises.
    archive = REPO / "results" / "census" / f"{taken}-{payload['state_sha256'][:12]}.json"
    archive.parent.mkdir(parents=True, exist_ok=True)
    archive.write_text(json.dumps(payload, indent=1) + "\n", encoding="utf-8")
    print(f"  archived as {_display(archive)}")
    ok = sum(1 for a in result.answers if a["noul"] is not None)
    cost = sum(float(a.get("cost") or 0) for a in result.answers)
    print(f"  {ok}/{len(result.answers)} answered · total cost ${cost:.6f}")
    print(f"→ {_display(out)}", file=sys.stderr)
    return 0 if ok else 1


def cmd_calibration(args: argparse.Namespace) -> int:
    """Per-model calibration and cross-model agreement, at the pre-registered tau."""
    labels, _ = _labels_and_profile()
    src = Path(args.decisions) if args.decisions else REPO / "results" / "decisions.json"
    if not src.exists():
        print(f"no census at {src} — run `rfpbrief census` first", file=sys.stderr)
        return 2
    decisions = json.loads(src.read_text(encoding="utf-8"))
    tau = float(decisions.get("operating_point_tau", labels["operating_point_tau"]))
    scores = calibrate.score(labels, decisions)
    if not scores:
        print("census has no answered decisions", file=sys.stderr)
        return 1
    dis = calibrate.disagreement(decisions)
    out = Path(args.out) if args.out else REPO / "results" / "calibration.json"
    out.write_text(json.dumps(calibrate.to_json(scores, dis, tau), indent=1) + "\n", encoding="utf-8")
    if not args.quiet:
        print(calibrate.render(scores, dis, tau))
    print(f"→ {_display(out)}", file=sys.stderr)
    return 0


def cmd_stats(args: argparse.Namespace) -> int:
    doc = spans.build(Path(args.fixture), fixture_name=Path(args.fixture).name)
    lengths = sorted(len(s.text) for s in doc.spans)
    n = len(lengths)
    if not n:
        print("no spans extracted")
        return 1
    print(f"{doc.fixture}")
    print(f"  pages                 {len(doc.pages)}")
    print(f"  spans                 {n}")
    print(f"  span chars            min {lengths[0]}  median {lengths[n // 2]}  p90 {lengths[int(n * .9)]}  max {lengths[-1]}")
    print(f"  hyphenated breaks     {doc.hyphen_breaks}")
    print(f"  engine                {doc.engine_version}")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="rfpbrief", description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)

    b = sub.add_parser("build", help="build a span index and write it to results/spans/")
    b.add_argument("fixture")
    b.add_argument("--out", help="output path (default results/spans/<fixture>.json)")
    b.set_defaults(func=cmd_build)

    f = sub.add_parser("find", help="locate a quote inside a span (exactly one, or it fails)")
    f.add_argument("fixture")
    f.add_argument("quote")
    f.add_argument("--page", type=int, help="disambiguate a quote that appears on several pages")
    f.add_argument("--exact", action="store_true",
                   help="require a whole-span match instead of containment")
    f.set_defaults(func=cmd_find)

    v = sub.add_parser("verify", help="check a committed index is still reproducible")
    v.add_argument("index")
    v.set_defaults(func=cmd_verify)

    s = sub.add_parser("stats", help="span size distribution for one fixture")
    s.add_argument("fixture")
    s.set_defaults(func=cmd_stats)

    e = sub.add_parser("extract", help="validate the committed extraction for a fixture")
    e.add_argument("fixture")
    e.add_argument("--extractions", help="directory of extraction files (default extractions/)")
    e.add_argument("--json", action="store_true", help="emit JSON")
    e.set_defaults(func=cmd_extract)

    d = sub.add_parser("decide", help="apply the frozen bidder profile to an extraction")
    d.add_argument("fixture")
    d.add_argument("--extractions")
    d.add_argument("--json", action="store_true")
    d.set_defaults(func=cmd_decide)

    br = sub.add_parser("brief", help="render the one-page brief")
    br.add_argument("fixture")
    br.add_argument("--extractions")
    br.add_argument("--out", help="output path (default results/briefs/<fixture>.md)")
    br.add_argument("--quiet", action="store_true", help="write the file without printing it")
    br.set_defaults(func=cmd_brief)

    bl = sub.add_parser("baseline", help="decision layer vs every committed label")
    bl.add_argument("--out", help="output path (default results/baseline.json)")
    bl.add_argument("--extractions", help="directory of extraction files (default extractions/)")
    bl.add_argument("--quiet", action="store_true")
    bl.set_defaults(func=cmd_baseline)

    pl = sub.add_parser("payload", help="print a fixture's spans in the extractor's input form")
    pl.add_argument("fixture")
    pl.set_defaults(func=cmd_payload)

    cp = sub.add_parser("compare", help="field-level comparison of two extraction sets")
    cp.add_argument("a")
    cp.add_argument("b")
    cp.set_defaults(func=cmd_compare)

    me = sub.add_parser("model-extract", help="run the model-backed extractor on one fixture")
    me.add_argument("fixture")
    me.add_argument("--model", default=model_extractor.DEFAULT_MODEL)
    me.add_argument("--retries", type=int, default=1,
                    help="repair attempts after a citation refusal (default 1; ADR 0006)")
    me.add_argument("--out-dir", default=str(REPO / "extractions" / "model"))
    me.add_argument("--no-write", action="store_true", help="validate without saving")
    me.set_defaults(func=cmd_model_extract)

    vr = sub.add_parser("variance", help="outcome stability across repeated model runs")
    vr.add_argument("directories", nargs="+", help="run directories, globs allowed")
    vr.add_argument("--out", help="output path (default results/variance.json)")
    vr.add_argument("--quiet", action="store_true")
    vr.add_argument("--strict", action="store_true",
                    help="exit non-zero unless every run was identical")
    vr.set_defaults(func=cmd_variance)

    pv = sub.add_parser("provider", help="is the intended decision model callable yet?")
    pv.add_argument("--model", default=providers.WANTED)
    pv.set_defaults(func=cmd_provider)

    ce = sub.add_parser("census", help="ask every eligible decision model about every fixture")
    ce.add_argument("--out", help="output path (default results/decisions.json)")
    ce.add_argument("--dry-run", action="store_true", help="list the census without calling it")
    ce.set_defaults(func=cmd_census)

    cal = sub.add_parser("calibration", help="per-model calibration and cross-model agreement")
    cal.add_argument("--decisions", help="census output (default results/decisions.json)")
    cal.add_argument("--out", help="output path (default results/calibration.json)")
    cal.add_argument("--quiet", action="store_true")
    cal.set_defaults(func=cmd_calibration)

    args = ap.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
